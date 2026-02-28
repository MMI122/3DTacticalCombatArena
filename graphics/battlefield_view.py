"""
Battlefield 3D Visualization
Creates the 3D representation of the game battlefield
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Dict, List, Tuple, Optional
import math

from ursina import (
    Entity, color, Vec3, Vec2, Text, Mesh
)
from ursina.shaders import lit_with_shadows_shader

from core.battlefield import Battlefield, Terrain, TERRAIN_DATA, Cell
from core.unit import Position
from config.settings import get_config

if TYPE_CHECKING:
    from .renderer import GameRenderer


class BattlefieldView:
    """
    3D visualization of the battlefield
    Creates terrain tiles, decorations, and grid overlay
    """
    
    def __init__(self, battlefield: Battlefield, renderer: 'GameRenderer'):
        self.battlefield = battlefield
        self.renderer = renderer
        self.config = get_config()
        
        self.cell_size = self.config.battlefield.cell_size
        
        # Entity containers
        self.terrain_entities: Dict[Tuple[int, int], Entity] = {}
        self.decoration_entities: List[Entity] = []
        self.grid_lines: List[Entity] = []
        self.highlight_entities: Dict[str, Entity] = {}
        
        # Root entity for organization
        self.root = Entity()
        
        # Add a large visible ground plane under everything (color 0-1 range)
        self.ground_plane = Entity(
            model='plane',
            scale=(100, 1, 100),
            position=(self.battlefield.width * self.cell_size / 2, -1, self.battlefield.height * self.cell_size / 2),
            color=color.Color(0.3, 0.5, 0.3, 1.0),
            double_sided=True
        )
        
        # Create the battlefield
        self._create_terrain()
        self._create_grid_overlay()
        self._create_decorations()
    
    def _get_terrain_color(self, terrain: Terrain) -> color:
        """Get color for terrain type"""
        props = TERRAIN_DATA[terrain]
        r, g, b = props.color
        # Ursina color uses 0-1 range, props.color is already 0-1
        return color.Color(r, g, b, 1.0)
    
    def _create_terrain(self):
        """Create all terrain tiles"""
        for y in range(self.battlefield.height):
            for x in range(self.battlefield.width):
                cell = self.battlefield.get_cell_at(x, y)
                if cell:
                    self._create_terrain_tile(x, y, cell)
    
    def _create_terrain_tile(self, x: int, y: int, cell: Cell):
        """Create a single terrain tile"""
        terrain_props = TERRAIN_DATA[cell.terrain]
        
        # Simple direct positioning - x and y on the grid, centered
        world_x = x * self.cell_size
        world_z = y * self.cell_size
        tile_height = 0.3 + terrain_props.height
        world_pos = Vec3(world_x, 0, world_z)  # For decoration positioning
        
        # Base tile - use simple cube with direct color, unlit so it shows without lighting
        tile = Entity(
            model='cube',
            scale=(self.cell_size * 0.95, tile_height, self.cell_size * 0.95),
            position=(world_x, tile_height / 2, world_z),
            color=self._get_terrain_color(cell.terrain),
            unlit=True
        )
        
        # Add terrain-specific details
        if cell.terrain == Terrain.FOREST:
            self._add_forest_decoration(world_pos)
        elif cell.terrain == Terrain.MOUNTAIN:
            self._add_mountain_decoration(world_pos, terrain_props.height)
        elif cell.terrain == Terrain.WATER:
            self._add_water_effect(tile)
        elif cell.terrain == Terrain.RUINS:
            self._add_ruins_decoration(world_pos)
        
        self.terrain_entities[(x, y)] = tile
    
    def _add_forest_decoration(self, pos: Vec3):
        """Add tree decorations"""
        # Simple tree representation - colors in 0-1 range
        trunk = Entity(
            model='cube',
            scale=(0.2, 1.5, 0.2),
            position=pos + Vec3(0.3, 0.75, 0.3),
            color=color.Color(0.4, 0.26, 0.13, 1.0)  # brown
        )
        
        foliage = Entity(
            model='sphere',
            scale=0.8,
            position=pos + Vec3(0.3, 1.8, 0.3),
            color=color.Color(0.13, 0.55, 0.13, 1.0)  # forest green
        )
        
        self.decoration_entities.extend([trunk, foliage])
    
    def _add_mountain_decoration(self, pos: Vec3, height: float):
        """Add mountain peak decoration - using cube as pyramid approximation"""
        # Main mountain body using stretched cube
        peak = Entity(
            model='cube',
            scale=(1.5, height + 1, 1.5),
            position=pos + Vec3(0, height / 2 + 0.5, 0),
            color=color.Color(0.55, 0.54, 0.54, 1.0)  # gray
        )
        
        # Snow cap using sphere
        snow = Entity(
            model='sphere',
            scale=(0.5, 0.4, 0.5),
            position=pos + Vec3(0, height + 1, 0),
            color=color.white
        )
        
        self.decoration_entities.extend([peak, snow])
    
    def _add_water_effect(self, tile: Entity):
        """Add water visual effect"""
        tile.color = color.Color(0.25, 0.41, 0.88, 1.0)  # royal blue
        tile.alpha = 0.7
        
        # Animated water surface (simple)
        water_surface = Entity(
            model='plane',
            scale=(self.cell_size * 0.95, 1, self.cell_size * 0.95),
            position=tile.position + Vec3(0, 0.2, 0),
            color=color.Color(0.39, 0.58, 0.93, 0.6),  # cornflower blue with alpha
            double_sided=True
        )
        
        self.decoration_entities.append(water_surface)
    
    def _add_ruins_decoration(self, pos: Vec3):
        """Add ruins decoration"""
        # Broken pillars
        for dx, dz in [(0.4, 0.4), (-0.4, -0.4)]:
            pillar = Entity(
                model='cube',
                scale=(0.3, 0.8 + (hash((dx, dz)) % 5) * 0.1, 0.3),
                position=pos + Vec3(dx, 0.4, dz),
                color=color.Color(0.66, 0.66, 0.66, 1.0)  # dark gray
            )
            self.decoration_entities.append(pillar)
    
    def _create_grid_overlay(self):
        """Create grid lines for visual reference"""
        line_color = color.Color(1.0, 1.0, 1.0, 0.2)  # White with low alpha
        
        # Horizontal lines
        for y in range(self.battlefield.height + 1):
            start = self.grid_to_world(0, y) - Vec3(self.cell_size / 2, 0, 0)
            end = self.grid_to_world(self.battlefield.width - 1, y) + Vec3(self.cell_size / 2, 0, 0)
            
            line = Entity(
                model='cube',
                scale=(end.x - start.x, 0.02, 0.02),
                position=(start + end) / 2 + Vec3(0, 0.16, -self.cell_size / 2),
                color=line_color,
                unlit=True
            )
            self.grid_lines.append(line)
        
        # Vertical lines
        for x in range(self.battlefield.width + 1):
            start = self.grid_to_world(x, 0) - Vec3(0, 0, self.cell_size / 2)
            end = self.grid_to_world(x, self.battlefield.height - 1) + Vec3(0, 0, self.cell_size / 2)
            
            line = Entity(
                model='cube',
                scale=(0.02, 0.02, end.z - start.z),
                position=(start + end) / 2 + Vec3(-self.cell_size / 2, 0.16, 0),
                color=line_color,
                unlit=True
            )
            self.grid_lines.append(line)
    
    def _create_decorations(self):
        """Add ambient decorations to the scene"""
        # Corner flag poles to mark battlefield boundaries
        corners = [
            (0, 0), 
            (self.battlefield.width - 1, 0),
            (0, self.battlefield.height - 1),
            (self.battlefield.width - 1, self.battlefield.height - 1)
        ]
        
        for i, (x, y) in enumerate(corners):
            pos = self.grid_to_world(x, y)
            # Thin pole that sits ON the ground (not floating)
            pole = Entity(
                model='cube',
                scale=(0.1, 1.5, 0.1),
                position=pos + Vec3(0, 0.75, 0),  # Half height so it sits on ground
                color=color.Color(0.3, 0.3, 0.3, 1.0),  # Dark gray
                unlit=True
            )
            # Small flag at top - Red for first 2 corners, Blue for last 2
            flag_color = color.Color(0.8, 0.2, 0.2, 1.0) if i < 2 else color.Color(0.2, 0.4, 0.8, 1.0)
            flag = Entity(
                model='cube',
                scale=(0.3, 0.2, 0.05),
                position=pos + Vec3(0.15, 1.4, 0),
                color=flag_color,
                unlit=True
            )
            self.decoration_entities.extend([pole, flag])
    
    def grid_to_world(self, grid_x: int, grid_y: int) -> Vec3:
        """Convert grid coordinates to world position"""
        world_x = grid_x * self.cell_size
        world_z = grid_y * self.cell_size
        
        # Get terrain height
        cell = self.battlefield.get_cell_at(grid_x, grid_y)
        world_y = cell.height if cell else 0
        
        return Vec3(world_x, world_y, world_z)
    
    def world_to_grid(self, world_pos: Vec3) -> Tuple[int, int]:
        """Convert world position to grid coordinates"""
        grid_x = int(world_pos.x / self.cell_size + 0.5)
        grid_y = int(world_pos.z / self.cell_size + 0.5)
        return (grid_x, grid_y)
    
    def highlight_cell(self, x: int, y: int, highlight_color: color, name: str = "default"):
        """Highlight a specific cell"""
        world_pos = self.grid_to_world(x, y)
        
        highlight = Entity(
            model='plane',
            scale=(self.cell_size * 0.9, 1, self.cell_size * 0.9),
            position=world_pos + Vec3(0, 0.2, 0),
            color=highlight_color,
            unlit=True,
            double_sided=True
        )
        
        # Remove existing highlight with same name
        if name in self.highlight_entities:
            self.highlight_entities[name].disable()
        
        self.highlight_entities[name] = highlight
    
    def highlight_cells(self, positions: List[Position], highlight_color: color, name: str = "default"):
        """Highlight multiple cells"""
        # Clear existing highlights with this name
        self.clear_highlights(name)
        
        for i, pos in enumerate(positions):
            self.highlight_cell(pos.x, pos.y, highlight_color, f"{name}_{i}")
    
    def clear_highlights(self, name_prefix: str = "default"):
        """Clear highlights by name prefix"""
        to_remove = []
        for name, entity in self.highlight_entities.items():
            if name.startswith(name_prefix):
                entity.disable()
                to_remove.append(name)
        
        for name in to_remove:
            del self.highlight_entities[name]
    
    def clear_all_highlights(self):
        """Clear all highlights"""
        for entity in self.highlight_entities.values():
            entity.disable()
        self.highlight_entities.clear()
    
    def show_movement_range(self, positions: List[Position]):
        """Show movement range for a unit"""
        self.highlight_cells(positions, color.Color(0.0, 0.39, 1.0, 0.4), "movement")
    
    def show_attack_range(self, positions: List[Position]):
        """Show attack range for a unit"""
        self.highlight_cells(positions, color.Color(1.0, 0.2, 0.2, 0.4), "attack")
    
    def show_path(self, positions: List[Position]):
        """Show a path on the battlefield"""
        for i, pos in enumerate(positions):
            alpha = 0.4 + 0.4 * (i / len(positions))
            self.highlight_cell(pos.x, pos.y, color.Color(1.0, 1.0, 0.0, alpha), f"path_{i}")
    
    def cleanup(self):
        """Clean up all entities"""
        for entity in self.terrain_entities.values():
            entity.disable()
        
        for entity in self.decoration_entities:
            entity.disable()
        
        for entity in self.grid_lines:
            entity.disable()
        
        self.clear_all_highlights()
        
        self.root.disable()
