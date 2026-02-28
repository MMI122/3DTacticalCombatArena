"""
AI Decision Tree Visualization — Browser-based
Serves a lightweight web page that displays real-time AI decision trees.
Uses Python's built-in http.server (no extra dependencies).
Auto-opens in the default browser.
"""

from __future__ import annotations
import http.server
import socketserver
import threading
import json
import webbrowser
from typing import Optional

from .decision_tree_data import DecisionTreeData, DecisionNode, FuzzyDecisionInfo, NodeStatus


# ── HTML + CSS + JS served as a single page ────────────────
HTML_PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Decision Tree Visualizer</title>
<style>
  :root {
    --bg: #0d1117; --panel: #161b22; --header: #0f3460;
    --selected: #00e676; --selected-bg: #122e1a;
    --pruned: #ff5252; --pruned-bg: #2e1212;
    --explored: #ffd740; --explored-bg: #2e2a12;
    --discarded: #78909c; --discarded-bg: #1b2630;
    --red-team: #ef5350; --blue-team: #42a5f5;
    --text: #e6edf3; --text-dim: #8b949e;
    --line: #30363d; --border: #30363d;
    --score-pos: #69f0ae; --score-neg: #ff8a80;
    --fuzzy-bar: #7c4dff; --fuzzy-selected: #00e5ff;
  }
  * { margin:0; padding:0; box-sizing:border-box; }
  body { font-family:'Segoe UI',system-ui,sans-serif; background:var(--bg); color:var(--text); overflow-x:hidden; }

  .header { background:var(--header); padding:12px 20px; display:flex; align-items:center; justify-content:space-between; position:sticky; top:0; z-index:10; }
  .header h1 { font-size:16px; font-weight:600; }
  .header .stats { font-size:12px; color:var(--text-dim); }
  .nav-btn { background:var(--panel); color:var(--text); border:1px solid var(--border); border-radius:6px; padding:4px 12px; cursor:pointer; font-size:12px; margin-left:4px; }
  .nav-btn:hover { background:#21262d; }
  .turn-info { font-size:11px; color:var(--text-dim); margin-left:8px; }

  .legend { background:var(--panel); padding:6px 20px; display:flex; gap:18px; border-bottom:1px solid var(--border); font-size:12px; }
  .legend span { display:flex; align-items:center; gap:5px; }
  .dot { width:10px; height:10px; border-radius:50%; display:inline-block; }

  .waiting { display:flex; align-items:center; justify-content:center; height:60vh; flex-direction:column; color:var(--text-dim); }
  .waiting .spinner { width:40px; height:40px; border:3px solid var(--border); border-top-color:var(--blue-team); border-radius:50%; animation:spin 1s linear infinite; margin-bottom:16px; }
  @keyframes spin { to { transform:rotate(360deg); } }

  .tree-container { padding:24px; overflow:auto; min-height:50vh; }

  .tree { display:flex; flex-direction:column; align-items:center; }
  .tree-level { display:flex; gap:12px; margin-bottom:8px; justify-content:center; flex-wrap:wrap; }

  .node {
    border:2px solid var(--border); border-radius:10px; padding:10px 14px;
    min-width:170px; max-width:220px; background:var(--panel); position:relative;
    transition:transform 0.2s,box-shadow 0.2s;
  }
  .node:hover { transform:translateY(-2px); box-shadow:0 4px 16px rgba(0,0,0,0.4); }
  .node.selected { border-color:var(--selected); background:var(--selected-bg); }
  .node.pruned  { border-color:var(--pruned); background:var(--pruned-bg); opacity:0.7; border-style:dashed; }
  .node.explored { border-color:var(--explored); background:var(--explored-bg); }
  .node.discarded { border-color:var(--discarded); background:var(--discarded-bg); opacity:0.75; }

  .node .status-dot { width:8px; height:8px; border-radius:50%; display:inline-block; margin-right:6px; vertical-align:middle; }
  .node .action-label { font-size:13px; font-weight:600; line-height:1.3; }
  .node .detail { font-size:11px; color:var(--text-dim); margin-top:4px; }
  .node .score { position:absolute; top:10px; right:12px; font-family:'Consolas',monospace; font-size:13px; font-weight:700; }
  .node .status-tag { font-size:10px; margin-top:6px; font-weight:600; }
  .node.root { min-width:220px; border-width:2px; }

  .fuzzy-list { max-width:900px; margin:0 auto; }
  .fuzzy-title { font-size:14px; font-weight:600; color:var(--text-dim); margin-bottom:16px; }
  .fuzzy-row {
    display:flex; align-items:center; gap:12px; padding:10px 14px;
    border-radius:10px; margin-bottom:8px; border:1px solid transparent;
    transition:background 0.15s;
  }
  .fuzzy-row:hover { background:#1c2333; }
  .fuzzy-row.selected { background:var(--selected-bg); border-color:var(--selected); }
  .fuzzy-rank { font-family:'Consolas',monospace; font-size:14px; font-weight:700; min-width:30px; text-align:center; }
  .fuzzy-info { flex:1; min-width:200px; }
  .fuzzy-info .label { font-size:13px; font-weight:600; }
  .fuzzy-info .reason { font-size:11px; color:var(--text-dim); margin-top:2px; }
  .fuzzy-bar-wrap { flex:2; display:flex; align-items:center; gap:8px; }
  .fuzzy-bar { height:22px; border-radius:4px; transition:width 0.4s ease; }
  .fuzzy-score { font-family:'Consolas',monospace; font-size:13px; font-weight:700; min-width:55px; }
  .fuzzy-badge { font-size:10px; font-weight:700; color:var(--selected); white-space:nowrap; }

  .summary { border-top:1px solid var(--border); margin-top:16px; padding-top:12px; font-size:12px; color:var(--text-dim); }

  @media (max-width:768px) {
    .node { min-width:140px; max-width:180px; padding:8px 10px; }
    .node .action-label { font-size:11px; }
  }
</style>
</head>
<body>

<div class="header">
  <h1 id="title">Waiting for AI decisions...</h1>
  <div style="display:flex;align-items:center;">
    <span class="stats" id="stats"></span>
    <button class="nav-btn" onclick="showPrev()">Prev</button>
    <button class="nav-btn" onclick="showNext()">Next</button>
    <span class="turn-info" id="turnInfo"></span>
  </div>
</div>

<div class="legend">
  <span><span class="dot" style="background:var(--selected)"></span> Selected (Best)</span>
  <span><span class="dot" style="background:var(--explored)"></span> Explored</span>
  <span><span class="dot" style="background:var(--discarded)"></span> Discarded</span>
  <span><span class="dot" style="background:var(--pruned)"></span> Pruned</span>
</div>

<div class="tree-container" id="content">
  <div class="waiting">
    <div class="spinner"></div>
    <div>Waiting for the game to start...</div>
    <div style="margin-top:8px;font-size:12px;">Decision trees will appear here in real-time</div>
  </div>
</div>

<script>
const history = [];
let historyIdx = -1;

async function poll() {
  try {
    const res = await fetch('/api/data');
    const json = await res.json();
    if (json.data && json.version > (history.length ? history[history.length-1]._v : -1)) {
      json.data._v = json.version;
      history.push(json.data);
      historyIdx = history.length - 1;
      render(json.data);
    }
  } catch(e) {}
  setTimeout(poll, 400);
}

function showPrev() { if (historyIdx > 0) { historyIdx--; render(history[historyIdx]); } }
function showNext() { if (historyIdx < history.length-1) { historyIdx++; render(history[historyIdx]); } }

function render(data) {
  const isRed = data.team === 'RED';
  const teamColor = isRed ? 'var(--red-team)' : 'var(--blue-team)';
  const dot = isRed ? '\u{1F534}' : '\u{1F535}';
  const algo = data.algorithm;

  document.getElementById('title').innerHTML =
    '<span style="color:'+teamColor+'">'+dot+' '+data.team+' Team</span> \u00B7 '+algo+' '+(algo==='Minimax'?'Search Tree':'Scored Actions');

  const stats = [];
  if (data.nodes_searched > 0) stats.push('Nodes: '+data.nodes_searched);
  if (data.pruned_count > 0)  stats.push('Pruned: '+data.pruned_count);
  if (data.thinking_time > 0) stats.push('Time: '+data.thinking_time.toFixed(2)+'s');
  stats.push('Best: '+fmtScore(data.best_score));
  document.getElementById('stats').textContent = stats.join('  |  ');
  document.getElementById('turnInfo').textContent = 'Turn '+data.turn_number+'  |  '+(historyIdx+1)+'/'+history.length;

  const content = document.getElementById('content');
  if (algo === 'Minimax' && data.root) {
    content.innerHTML = renderMinimaxTree(data);
  } else if (algo === 'Fuzzy' && data.fuzzy_decisions) {
    content.innerHTML = renderFuzzyList(data);
  }
}

function statusClass(s) {
  return {SELECTED:'selected',PRUNED:'pruned',EXPLORED:'explored',DISCARDED:'discarded'}[s]||'';
}
function statusDotColor(s) {
  return {SELECTED:'var(--selected)',PRUNED:'var(--pruned)',EXPLORED:'var(--explored)',DISCARDED:'var(--discarded)'}[s]||'var(--text-dim)';
}
function statusTag(s) {
  return {SELECTED:'\u2713 BEST',PRUNED:'\u2702 PRUNED',EXPLORED:'explored',DISCARDED:'\u2717 worse'}[s]||'';
}
function scoreColor(v) { return v >= 0 ? 'var(--score-pos)' : 'var(--score-neg)'; }
function fmtScore(v) { return (v >= 0 ? '+' : '') + v.toFixed(1); }

function renderNode(node, isRoot) {
  const cls = statusClass(node.status);
  const dotCol = statusDotColor(node.status);
  const label = node.action_label.length > 28 ? node.action_label.slice(0,26)+'\u2026' : node.action_label;
  const detail = (node.action_detail||'').length > 35 ? node.action_detail.slice(0,33)+'\u2026' : (node.action_detail||'');
  const tag = statusTag(node.status);

  return '<div class="node '+cls+(isRoot?' root':'')+'">'
    +'<span class="score" style="color:'+scoreColor(node.score)+'">'+fmtScore(node.score)+'</span>'
    +'<div class="action-label"><span class="status-dot" style="background:'+dotCol+'"></span>'+esc(label)+'</div>'
    +'<div class="detail">'+esc(detail)+'</div>'
    +(tag?'<div class="status-tag" style="color:'+dotCol+'">'+tag+'</div>':'')
    +'</div>';
}

function renderMinimaxTree(data) {
  const root = data.root;
  let html = '<div class="tree">';
  html += '<div class="tree-level">'+renderNode(root, true)+'</div>';

  if (root.children && root.children.length) {
    html += '<div style="text-align:center;color:var(--line);font-size:20px;margin:4px 0;">\u2502</div>';
    html += '<div class="tree-level">';
    for (const child of root.children) html += renderNode(child, false);
    html += '</div>';

    const sel = root.children.find(c => c.status === 'SELECTED');
    if (sel && sel.children && sel.children.length) {
      html += '<div style="text-align:center;color:var(--selected);font-size:11px;margin:8px 0;">\u25BC Opponent responses to best move</div>';
      html += '<div class="tree-level">';
      for (const gc of sel.children) html += renderNode(gc, false);
      html += '</div>';
    }
  }

  html += '</div>';
  html += '<div class="summary">Searched '+data.nodes_searched+' nodes | Pruned '+data.pruned_count+' branches | Best action: '+esc(data.best_action_label)+' ('+fmtScore(data.best_score)+')</div>';
  return html;
}

function renderFuzzyList(data) {
  const decisions = data.fuzzy_decisions;
  if (!decisions || !decisions.length) return '<div class="waiting">No decisions</div>';

  const maxScore = Math.max(...decisions.map(d => Math.abs(d.score)), 0.01);
  let html = '<div class="fuzzy-list">';
  html += '<div class="fuzzy-title">Fuzzy Logic Action Scores (ranked best to worst)</div>';

  decisions.forEach((d, i) => {
    const sel = d.is_selected;
    const barW = Math.max(2, (Math.abs(d.score)/maxScore)*100);
    const barColor = sel ? 'var(--fuzzy-selected)' : 'var(--fuzzy-bar)';
    const label = d.action_label.length > 36 ? d.action_label.slice(0,34)+'\u2026' : d.action_label;
    const reason = (d.reasoning||'').length > 50 ? d.reasoning.slice(0,48)+'\u2026' : (d.reasoning||'');

    html += '<div class="fuzzy-row '+(sel?'selected':'')+'">'
      +'<div class="fuzzy-rank" style="color:'+(sel?'var(--selected)':'var(--text-dim)')+'">#'+(i+1)+'</div>'
      +'<div class="fuzzy-info">'
        +'<div class="label" style="color:'+(sel?'var(--selected)':'var(--text)')+'">'+esc(label)+'</div>'
        +'<div class="reason">'+esc(reason)+'</div>'
      +'</div>'
      +'<div class="fuzzy-bar-wrap">'
        +'<div class="fuzzy-bar" style="width:'+barW+'%;background:'+barColor+'"></div>'
        +'<span class="fuzzy-score" style="color:'+scoreColor(d.score)+'">'+fmtScore(d.score)+'</span>'
      +'</div>'
      +(sel?'<span class="fuzzy-badge">\u2713 SELECTED</span>':'')
      +'</div>';
  });

  html += '<div class="summary">Evaluated '+decisions.length+' actions | Best score: '+fmtScore(data.best_score)+' | Action: '+esc(data.best_action_label)+'</div>';
  html += '</div>';
  return html;
}

function esc(s) { const d=document.createElement('div'); d.textContent=s||''; return d.innerHTML; }

poll();
</script>
</body>
</html>"""


class DecisionTreeWindow:
    """
    Web-based AI Decision Tree Visualizer.
    Serves an HTML page on localhost and auto-opens the browser.
    Much lighter than tkinter - all rendering done by the browser.
    """

    def __init__(self, port: int = 9173):
        self._port = port
        self._server: Optional[socketserver.TCPServer] = None
        self._thread: Optional[threading.Thread] = None
        self._running = False
        self._current_data: Optional[dict] = None
        self._version = 0
        self._lock = threading.Lock()

    def start(self):
        """Launch the web server and open the browser"""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run_server, daemon=True)
        self._thread.start()
        threading.Timer(0.8, self._open_browser).start()

    def stop(self):
        """Shutdown the web server"""
        self._running = False
        if self._server:
            try:
                self._server.shutdown()
            except Exception:
                pass

    def push_decision(self, data: DecisionTreeData):
        """Thread-safe: push new decision data"""
        serialized = self._serialize(data)
        with self._lock:
            self._version += 1
            self._current_data = serialized

    # ── HTTP Server ────────────────────────────────────────

    def _run_server(self):
        parent = self

        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/api/data':
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    with parent._lock:
                        payload = {'version': parent._version, 'data': parent._current_data}
                    self.wfile.write(json.dumps(payload).encode())
                else:
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(HTML_PAGE.encode('utf-8'))

            def log_message(self, format, *args):
                pass  # Suppress logs

        socketserver.TCPServer.allow_reuse_address = True
        try:
            self._server = socketserver.TCPServer(('127.0.0.1', self._port), Handler)
            self._server.serve_forever()
        except OSError:
            try:
                self._port += 1
                self._server = socketserver.TCPServer(('127.0.0.1', self._port), Handler)
                self._server.serve_forever()
            except Exception as e:
                print(f"[TreeViz] Could not start server: {e}")

    def _open_browser(self):
        url = f'http://localhost:{self._port}'
        print(f"Decision Tree Visualizer: {url}")
        try:
            webbrowser.open(url)
        except Exception:
            print(f"   Open manually: {url}")

    # ── Serialization ──────────────────────────────────────

    def _serialize(self, data: DecisionTreeData) -> dict:
        return {
            'team': data.team,
            'algorithm': data.algorithm,
            'turn_number': data.turn_number,
            'best_action_label': data.best_action_label,
            'best_score': data.best_score,
            'nodes_searched': data.nodes_searched,
            'pruned_count': data.pruned_count,
            'thinking_time': data.thinking_time,
            'root': self._serialize_node(data.root) if data.root else None,
            'fuzzy_decisions': [self._serialize_fuzzy(f) for f in data.fuzzy_decisions] if data.fuzzy_decisions else None
        }

    def _serialize_node(self, node: DecisionNode) -> dict:
        return {
            'node_id': node.node_id,
            'action_label': node.action_label,
            'action_detail': node.action_detail,
            'score': node.score,
            'depth': node.depth,
            'is_maximizing': node.is_maximizing,
            'status': node.status.name,
            'unit_name': node.unit_name,
            'team': node.team,
            'children': [self._serialize_node(c) for c in node.children] if node.children else []
        }

    def _serialize_fuzzy(self, f: FuzzyDecisionInfo) -> dict:
        return {
            'action_label': f.action_label,
            'score': f.score,
            'reasoning': f.reasoning,
            'aggression': f.aggression,
            'is_selected': f.is_selected,
            'own_hp_pct': f.own_hp_pct,
            'team_advantage': f.team_advantage,
            'enemies_in_range': f.enemies_in_range
        }
