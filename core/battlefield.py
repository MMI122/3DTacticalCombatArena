"""
Battlefield and Terrain System
3D grid-based battlefield with terrain features
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple, Set
from enum import Enum, auto
import random
import numpy as np

from .unit import Position, Unit, Team


class Terrain(Enum):
    """Terrain types with combat modifiers"""
    PLAIN = auto()      # No modifiers
    FOREST = auto()     # +2 defense, blocks line of sight
    HILL = auto()       # +1 attack, +1 defense
    WATER = auto()      # Impassable
    MOUNTAIN = auto()   # Impassable
    RUINS = auto()      # +3 defense (cover)
    ROAD = auto()       # +1 movement
    BRIDGE = auto()     # Normal, crosses water


@dataclass
class TerrainProperties:
    """Properties for each terrain type"""
    terrain: Terrain
    passable: bool
    defense_modifier: int
    attack_modifier: int
    movement_cost: int
    blocks_los: bool  # Line of sight
    height: float  # For 3D rendering
    color: Tuple[float, float, float]
    
    
TERRAIN_DATA: Dict[Terrain, TerrainProperties] = {
    Terrain.PLAIN: TerrainProperties(
        terrain=Terrain.PLAIN,
        passable=True,
        defense_modifier=0,
        attack_modifier=0,
        movement_cost=1,
        blocks_los=False,
        height=0.0,
        color=(0.4, 0.6, 0.3)  # Green
    ),
    Terrain.FOREST: TerrainProperties(
        terrain=Terrain.FOREST,
        passable=True,
        defense_modifier=2,
        attack_modifier=0,
        movement_cost=2,
        blocks_los=True,
        height=0.2,
        color=(0.2, 0.4, 0.15)  # Dark green
    ),
    Terrain.HILL: TerrainProperties(
        terrain=Terrain.HILL,
        passable=True,
        defense_modifier=1,
        attack_modifier=1,
        movement_cost=2,
        blocks_los=False,
        height=0.8,
        color=(0.5, 0.4, 0.3)  # Brown
    ),
    Terrain.WATER: TerrainProperties(
        terrain=Terrain.WATER,
        passable=False,
        defense_modifier=0,
        attack_modifier=0,
        movement_cost=99,
        blocks_los=False,
        height=-0.3,
        color=(0.2, 0.4, 0.8)  # Blue
    ),
    Terrain.MOUNTAIN: TerrainProperties(
        terrain=Terrain.MOUNTAIN,
        passable=False,
        defense_modifier=0,
        attack_modifier=0,
        movement_cost=99,
        blocks_los=True,
        height=1.5,
        color=(0.5, 0.5, 0.55)  # Gray
    ),
    Terrain.RUINS: TerrainProperties(
        terrain=Terrain.RUINS,
        passable=True,
        defense_modifier=3,
        attack_modifier=0,
        movement_cost=1,
        blocks_los=True,
        height=0.3,
        color=(0.45, 0.4, 0.35)  # Tan
    ),
    Terrain.ROAD: TerrainProperties(
        terrain=Terrain.ROAD,
        passable=True,
        defense_modifier=-1,
        attack_modifier=0,
        movement_cost=0,  # Bonus movement
        blocks_los=False,
        height=0.0,
        color=(0.55, 0.5, 0.4)  # Light brown
    ),
    Terrain.BRIDGE: TerrainProperties(
        terrain=Terrain.BRIDGE,
        passable=True,
        defense_modifier=0,
        attack_modifier=0,
        movement_cost=1,
        blocks_los=False,
        height=0.1,
        color=(0.5, 0.35, 0.2)  # Wood
    )
}


@dataclass
class Cell:
    """Single cell in the battlefield grid"""
    position: Position
    terrain: Terrain
    occupant: Optional[Unit] = None
    
    @property
    def properties(self) -> TerrainProperties:
        return TERRAIN_DATA[self.terrain]
    
    @property
    def is_passable(self) -> bool:
        return self.properties.passable and self.occupant is None
    
    @property
    def is_empty(self) -> bool:
        return self.occupant is None
    
    @property
    def defense_modifier(self) -> int:
        return self.properties.defense_modifier
    
    @property
    def attack_modifier(self) -> int:
        return self.properties.attack_modifier
    
    @property
    def height(self) -> float:
        return self.properties.height


class Battlefield:
    """
    Grid-based 3D battlefield
    Manages terrain, unit positions, and spatial queries
    """
    
    def __init__(self, width: int, height: int, seed: Optional[int] = None):
        self.width = width
        self.height = height
        self.seed = seed or random.randint(0, 999999)
        
        # Initialize grid
        self.grid: List[List[Cell]] = []
        self._initialize_grid()
        
        # Generate terrain
        self._generate_terrain()
    
    def _initialize_grid(self):
        """Create empty grid"""
        self.grid = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                cell = Cell(
                    position=Position(x, y),
                    terrain=Terrain.PLAIN
                )
                row.append(cell)
            self.grid.append(row)
    
    def _generate_terrain(self):
        """Generate interesting terrain using procedural methods"""
        random.seed(self.seed)
        np.random.seed(self.seed)
        
        # Generate height map using simple noise
        height_map = self._generate_noise(scale=4)
        
        # Generate moisture map for forests
        moisture_map = self._generate_noise(scale=3)
        
        for y in range(self.height):
            for x in range(self.width):
                h = height_map[y, x]
                m = moisture_map[y, x]
                
                # Assign terrain based on height and moisture
                if h > 0.8:
                    terrain = Terrain.MOUNTAIN
                elif h > 0.6:
                    terrain = Terrain.HILL
                elif h < 0.15:
                    terrain = Terrain.WATER
                elif m > 0.65 and h > 0.2:
                    terrain = Terrain.FOREST
                elif random.random() < 0.05:
                    terrain = Terrain.RUINS
                else:
                    terrain = Terrain.PLAIN
                
                self.grid[y][x].terrain = terrain
        
        # Ensure spawn areas are clear (plains)
        self._clear_spawn_areas()
        
        # Add some roads connecting areas
        self._generate_roads()
    
    def _generate_noise(self, scale: int = 4) -> np.ndarray:
        """Generate simple Perlin-like noise using pure numpy (no scipy)"""
        # Create small random grid
        small = np.random.rand(scale, scale)
        
        # Bilinear interpolation to upscale - pure numpy implementation
        target_h, target_w = self.height, self.width
        
        # Create coordinate grids for interpolation
        x = np.linspace(0, scale - 1, target_w)
        y = np.linspace(0, scale - 1, target_h)
        
        # Get integer and fractional parts
        x0 = np.floor(x).astype(int)
        y0 = np.floor(y).astype(int)
        x1 = np.minimum(x0 + 1, scale - 1)
        y1 = np.minimum(y0 + 1, scale - 1)
        
        # Fractional parts
        xf = x - x0
        yf = y - y0
        
        # Create output array using bilinear interpolation
        noise = np.zeros((target_h, target_w))
        for j in range(target_h):
            for i in range(target_w):
                # Get the four corner values
                c00 = small[y0[j], x0[i]]
                c10 = small[y0[j], x1[i]]
                c01 = small[y1[j], x0[i]]
                c11 = small[y1[j], x1[i]]
                
                # Bilinear interpolation
                c0 = c00 * (1 - xf[i]) + c10 * xf[i]
                c1 = c01 * (1 - xf[i]) + c11 * xf[i]
                noise[j, i] = c0 * (1 - yf[j]) + c1 * yf[j]
        
        # Normalize
        noise = (noise - noise.min()) / (noise.max() - noise.min() + 1e-10)
        return noise
    
    def _clear_spawn_areas(self):
        """Ensure spawn areas are passable"""
        # Red team spawn (left side)
        for y in range(self.height):
            for x in range(3):
                self.grid[y][x].terrain = Terrain.PLAIN
        
        # Blue team spawn (right side)
        for y in range(self.height):
            for x in range(self.width - 3, self.width):
                self.grid[y][x].terrain = Terrain.PLAIN
    
    def _generate_roads(self):
        """Add roads connecting spawn areas"""
        # Horizontal road through middle
        mid_y = self.height // 2
        for x in range(self.width):
            if self.grid[mid_y][x].terrain in [Terrain.PLAIN, Terrain.FOREST]:
                self.grid[mid_y][x].terrain = Terrain.ROAD
            elif self.grid[mid_y][x].terrain == Terrain.WATER:
                self.grid[mid_y][x].terrain = Terrain.BRIDGE
    
    def get_cell(self, position: Position) -> Optional[Cell]:
        """Get cell at position"""
        if self.is_valid_position(position):
            return self.grid[position.y][position.x]
        return None
    
    def get_cell_at(self, x: int, y: int) -> Optional[Cell]:
        """Get cell at coordinates"""
        return self.get_cell(Position(x, y))
    
    def is_valid_position(self, position: Position) -> bool:
        """Check if position is within bounds"""
        return 0 <= position.x < self.width and 0 <= position.y < self.height
    
    def is_passable(self, position: Position) -> bool:
        """Check if position can be moved to"""
        cell = self.get_cell(position)
        return cell is not None and cell.is_passable
    
    def place_unit(self, unit: Unit, position: Position) -> bool:
        """Place a unit on the battlefield"""
        cell = self.get_cell(position)
        if cell and cell.is_empty and cell.properties.passable:
            cell.occupant = unit
            unit.position = position
            return True
        return False
    
    def move_unit(self, unit: Unit, new_position: Position) -> bool:
        """Move a unit to a new position"""
        old_cell = self.get_cell(unit.position)
        new_cell = self.get_cell(new_position)
        
        if old_cell and new_cell and new_cell.is_passable:
            old_cell.occupant = None
            new_cell.occupant = unit
            unit.position = new_position
            return True
        return False
    
    def remove_unit(self, unit: Unit):
        """Remove a unit from the battlefield"""
        cell = self.get_cell(unit.position)
        if cell and cell.occupant == unit:
            cell.occupant = None
    
    def get_unit_at(self, position: Position) -> Optional[Unit]:
        """Get unit at position"""
        cell = self.get_cell(position)
        return cell.occupant if cell else None
    
    def get_reachable_positions(self, unit: Unit) -> List[Position]:
        """Get all positions a unit can move to"""
        reachable = []
        visited = {unit.position}
        frontier = [(unit.position, 0)]
        
        while frontier:
            current, cost = frontier.pop(0)
            
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                next_pos = Position(current.x + dx, current.y + dy)
                
                if next_pos in visited:
                    continue
                
                cell = self.get_cell(next_pos)
                if cell is None or not cell.properties.passable:
                    continue
                
                move_cost = cost + cell.properties.movement_cost
                if move_cost > unit.movement_range:
                    continue
                
                visited.add(next_pos)
                
                if cell.is_empty:
                    reachable.append(next_pos)
                    frontier.append((next_pos, move_cost))
                elif cell.occupant and cell.occupant.team == unit.team:
                    # Can pass through allies but not stop on them
                    frontier.append((next_pos, move_cost))
        
        return reachable
    
    def get_attackable_positions(self, unit: Unit) -> List[Position]:
        """Get all positions a unit can attack"""
        attackable = []
        
        for dy in range(-unit.attack_range, unit.attack_range + 1):
            for dx in range(-unit.attack_range, unit.attack_range + 1):
                if dx == 0 and dy == 0:
                    continue
                
                pos = Position(unit.position.x + dx, unit.position.y + dy)
                if unit.position.distance_to(pos) <= unit.attack_range:
                    if self.is_valid_position(pos):
                        attackable.append(pos)
        
        return attackable
    
    def get_enemies_in_range(self, unit: Unit) -> List[Unit]:
        """Get all enemy units within attack range"""
        enemies = []
        for pos in self.get_attackable_positions(unit):
            target = self.get_unit_at(pos)
            if target and target.team != unit.team and target.is_alive:
                enemies.append(target)
        return enemies
    
    def get_allies_in_range(self, unit: Unit, range_val: int) -> List[Unit]:
        """Get all allied units within range"""
        allies = []
        for dy in range(-range_val, range_val + 1):
            for dx in range(-range_val, range_val + 1):
                if dx == 0 and dy == 0:
                    continue
                pos = Position(unit.position.x + dx, unit.position.y + dy)
                if unit.position.distance_to(pos) <= range_val:
                    target = self.get_unit_at(pos)
                    if target and target.team == unit.team and target.is_alive:
                        allies.append(target)
        return allies
    
    def has_line_of_sight(self, from_pos: Position, to_pos: Position) -> bool:
        """Check if there's clear line of sight between positions"""
        # Bresenham's line algorithm
        x0, y0 = from_pos.x, from_pos.y
        x1, y1 = to_pos.x, to_pos.y
        
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        
        while True:
            if x0 == x1 and y0 == y1:
                return True
            
            cell = self.get_cell(Position(x0, y0))
            if cell and cell.properties.blocks_los:
                # Allow if it's the starting or ending cell
                if not (x0 == from_pos.x and y0 == from_pos.y) and \
                   not (x0 == to_pos.x and y0 == to_pos.y):
                    return False
            
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy
        
        return True
    
    def get_spawn_positions(self, team: Team, count: int) -> List[Position]:
        """Get spawn positions for a team"""
        positions = []
        
        if team == Team.RED:
            # Left side spawn
            x_range = range(0, 2)
        else:
            # Right side spawn
            x_range = range(self.width - 2, self.width)
        
        y_spacing = self.height // (count + 1)
        
        for i in range(count):
            y = (i + 1) * y_spacing
            for x in x_range:
                pos = Position(x, y)
                cell = self.get_cell(pos)
                if cell and cell.is_passable:
                    positions.append(pos)
                    break
        
        return positions[:count]
    
    def clone(self) -> Battlefield:
        """Create a deep copy of the battlefield"""
        import copy
        new_bf = Battlefield.__new__(Battlefield)
        new_bf.width = self.width
        new_bf.height = self.height
        new_bf.seed = self.seed
        
        new_bf.grid = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                old_cell = self.grid[y][x]
                new_cell = Cell(
                    position=Position(x, y),
                    terrain=old_cell.terrain,
                    occupant=old_cell.occupant.clone() if old_cell.occupant else None
                )
                row.append(new_cell)
            new_bf.grid.append(row)
        
        return new_bf
    
    def __repr__(self):
        """ASCII representation of battlefield"""
        symbols = {
            Terrain.PLAIN: '.',
            Terrain.FOREST: 'F',
            Terrain.HILL: '^',
            Terrain.WATER: '~',
            Terrain.MOUNTAIN: 'M',
            Terrain.RUINS: '#',
            Terrain.ROAD: '=',
            Terrain.BRIDGE: '|'
        }
        
        lines = []
        for y in range(self.height):
            line = ""
            for x in range(self.width):
                cell = self.grid[y][x]
                if cell.occupant:
                    if cell.occupant.team == Team.RED:
                        line += 'R'
                    else:
                        line += 'B'
                else:
                    line += symbols.get(cell.terrain, '?')
            lines.append(line)
        
        return '\n'.join(lines)
