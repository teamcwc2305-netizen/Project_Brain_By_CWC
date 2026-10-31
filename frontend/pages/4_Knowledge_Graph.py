# frontend/pages/4_Knowledge_Graph.py
import os
import sys
import json
import httpx
import streamlit as st
import streamlit.components.v1 as components

BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Knowledge Graph | Project Brain",
    page_icon="🕸️",
    layout="wide"
)

# 1. Path setup
pages_dir = os.path.dirname(os.path.abspath(__file__))
frontend_dir = os.path.abspath(os.path.join(pages_dir, ".."))
project_root = os.path.abspath(os.path.join(frontend_dir, ".."))
for p in [pages_dir, frontend_dir, project_root]:
    if p not in sys.path:
        sys.path.insert(0, p)

# 2. RENDER STYLES & NAVBAR IMMEDIATELY (Prevents old interface flash)
try:
    from sidebar_nav import render_sidebar
    render_sidebar()
except Exception:
    pass

try:
    from auth import require_auth
    require_auth()
except Exception:
    pass

try:
    from repo_manager import fetch_repositories, get_active_repo, render_repo_selector
except Exception:
    pass

# Fetch repositories and data
repos = fetch_repositories()
current_repo = get_active_repo(repos)
repo_id = current_repo["id"] if current_repo else None

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@400;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

  .stApp,
  [data-testid="stAppViewContainer"] {
    background-color: #f8fafc !important;
    color: #0f172a !important;
    font-family: 'Inter', -apple-system, sans-serif !important;
  }

  header[data-testid="stHeader"] { background: transparent !important; }
  #MainMenu, footer { visibility: hidden; }
  
  .top-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 6px 0 18px 0;
    border-bottom: 1.5px solid #e2e8f0;
    margin-bottom: 22px;
  }

  .header-left {
    display: flex;
    align-items: center;
    gap: 14px;
  }

  .header-badge {
    width: 44px;
    height: 44px;
    border-radius: 12px;
    background: #0f172a;
    display: grid;
    place-items: center;
    flex-shrink: 0;
    box-shadow: 0 4px 10px rgba(15, 23, 42, 0.20);
  }

  .header-title {
    font-weight: 800;
    font-size: 19px;
    letter-spacing: -0.3px;
    color: #0f172a;
    margin: 0;
    line-height: 1.2;
  }

  .header-subtitle {
    font-size: 12.5px;
    color: #64748b;
    font-weight: 500;
    margin-top: 4px;
  }

  .header-pill {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    background: #eff6ff;
    border: 1.5px solid #bfdbfe;
    padding: 6px 16px;
    border-radius: 20px;
    font-size: 12px;
    color: #1d4ed8;
    font-weight: 700;
    box-shadow: 0 1px 3px rgba(37, 99, 235, 0.08);
  }

  .pill-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #2563eb;
  }

  div[data-testid="stExpander"] {
    background: #ffffff !important;
    border: 1.5px solid #e2e8f0 !important;
    border-radius: 16px !important;
    box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.04) !important;
    margin-top: 24px !important;
  }

  div[data-testid="stExpander"] summary {
    font-weight: 700 !important;
    font-size: 14px !important;
    color: #0f172a !important;
  }

  .stMarkdown table {
    width: 100% !important;
    border-collapse: separate !important;
    border-spacing: 0 !important;
    border: 1.5px solid #e2e8f0 !important;
    border-radius: 12px !important;
    overflow: hidden !important;
    background: #ffffff !important;
    margin-top: 8px !important;
  }

  .stMarkdown th {
    background: #f8fafc !important;
    color: #0f172a !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    padding: 11px 16px !important;
    border-bottom: 1.5px solid #e2e8f0 !important;
    text-align: left !important;
  }

  .stMarkdown td {
    padding: 9px 16px !important;
    font-size: 13px !important;
    color: #334155 !important;
    border-bottom: 1px solid #f1f5f9 !important;
  }

  .stMarkdown tr:last-child td {
    border-bottom: none !important;
  }

  .stMarkdown td code {
    background: #ecfdf5 !important;
    color: #059669 !important;
    border: 1px solid #a7f3d0 !important;
    border-radius: 5px !important;
    padding: 2px 7px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12px !important;
    font-weight: 700 !important;
  }
</style>
""", unsafe_allow_html=True)

# ACTIVE REPOSITORY SELECTION & SYNC

import sys
import os
pages_dir = os.path.dirname(os.path.abspath(__file__))
frontend_dir = os.path.abspath(os.path.join(pages_dir, ".."))
project_root = os.path.abspath(os.path.join(frontend_dir, ".."))
for p in [pages_dir, frontend_dir, project_root]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from frontend.auth import require_auth
except ImportError:
    from auth import require_auth

require_auth()

try:
    from frontend.repo_manager import (
        fetch_repositories,
        get_active_repo,
        render_repo_selector,
        set_active_repo_id
    )
except ImportError:
    from repo_manager import (
        fetch_repositories,
        get_active_repo,
        render_repo_selector,
        set_active_repo_id
    )

repos = fetch_repositories()
current_repo = get_active_repo(repos)
repo_id = current_repo["id"] if current_repo else None

try:
    from sidebar_nav import render_sidebar
    render_sidebar(repos=repos, key="graph_repo_selector")
except Exception:
    pass

current_repo = next((r for r in repos if r["id"] == repo_id), None)
repo_name = f"{current_repo['owner']}/{current_repo['name']}" if current_repo else f"Repository #{repo_id}"

if not repo_id:
    st.warning("⚠️ No active repository found. Please import or select a repository on the main dashboard first!")
    st.stop()

# TOP HEADER BAR
st.markdown(f"""
<div class="top-header">
  <div class="header-left">
    <div class="header-badge">
      <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="18" cy="5" r="3"></circle>
        <circle cx="6" cy="12" r="3"></circle>
        <circle cx="18" cy="19" r="3"></circle>
        <line x1="8.59" y1="13.51" x2="15.42" y2="17.49"></line>
        <line x1="15.41" y1="6.51" x2="8.59" y2="10.49"></line>
      </svg>
    </div>
    <div>
      <h2 class="header-title">Delivery Knowledge Graph</h2>
      <div class="header-subtitle">
        Active Repository: <b>{repo_name}</b> &middot; Relational delivery memory map
      </div>
    </div>
  </div>
  <div>
    <span class="header-pill">
      <span class="pill-dot"></span> Deterministic Graph
    </span>
  </div>
</div>
""", unsafe_allow_html=True)

# LOAD REPOSITORY GRAPH DATA & STATS

repo_stats = {}
try:
    s_resp = httpx.get(f"{BACKEND_URL}/api/repositories/{repo_id}/stats", timeout=5.0)
    if s_resp.status_code == 200:
        repo_stats = s_resp.json()
except Exception:
    pass

with st.spinner("Compiling delivery memory graph..."):
    try:
        resp = httpx.get(f"{BACKEND_URL}/api/repositories/{repo_id}/graph", timeout=15.0)
        if resp.status_code != 200:
            st.error(f"Failed to fetch graph data: {resp.text}")
            st.stop()
        data = resp.json()
    except Exception as e:
        st.error(f"Cannot reach backend: {e}")
        st.stop()

nodes = data.get("nodes", [])
edges = data.get("edges", [])
audit = data.get("audit", {})
metrics = data.get("metrics", {})

group_counts = {
    "Author": 0,
    "Commit": 0,
    "File": 0,
    "Issue": 0,
    "PullRequest": 0
}
for n in nodes:
    g = n.get("group", "Unknown")
    group_counts[g] = group_counts.get(g, 0) + 1

imported_issues = metrics.get("imported_issues_count", audit.get("imported_issues_count", len([n for n in nodes if n.get("group") == "Issue" and n.get("is_imported")])))
referenced_issues = metrics.get("referenced_issues_count", audit.get("referenced_issues_count", len([n for n in nodes if n.get("group") == "Issue" and n.get("is_referenced")])))
total_issues = metrics.get("total_graph_issues_count", audit.get("total_graph_issues_count", group_counts.get("Issue", 0)))

imported_prs = metrics.get("imported_prs_count", audit.get("imported_prs_count", len([n for n in nodes if n.get("group") == "PullRequest" and n.get("is_imported")])))
referenced_prs = metrics.get("referenced_prs_count", audit.get("referenced_prs_count", len([n for n in nodes if n.get("group") == "PullRequest" and n.get("is_referenced")])))
total_prs = metrics.get("total_graph_prs_count", audit.get("total_graph_prs_count", group_counts.get("PullRequest", 0)))

display_commits = repo_stats.get("total_commits") or group_counts.get("Commit", 0)
display_issues = repo_stats.get("open_issues_count", group_counts.get("Issue", 0))
display_prs = repo_stats.get("open_prs_count", group_counts.get("PullRequest", 0))

nodes_json = json.dumps(nodes)
edges_json = json.dumps(edges)

dashboard_and_graph_html = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
  <style>
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      padding: 0;
      overflow: hidden;
      font-family: 'Space Grotesk', -apple-system, sans-serif;
      background: transparent;
    }}
    
    #main-wrapper {{
      position: relative;
      width: 100%;
      border-radius: 20px;
      border: 1.5px solid #cbd5e1;
      box-shadow: 
        0 30px 60px -15px rgba(0, 0, 0, 0.22),
        0 15px 30px -10px rgba(0, 0, 0, 0.12),
        0 0 1px 1px rgba(0, 0, 0, 0.05);
      overflow: hidden;
      background: #f8fafc;
    }}

    #canvas-bg {{
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      z-index: 1;
      pointer-events: none;
    }}

    .blur-backdrop-shadow {{
      position: absolute;
      top: 60%;
      left: 50%;
      transform: translate(-50%, -50%);
      width: 650px;
      height: 600px;
      border-radius: 50%;
      background: radial-gradient(
        circle,
        rgba(30, 41, 59, 0.14) 0%,
        rgba(51, 65, 85, 0.08) 45%,
        transparent 75%
      );
      filter: blur(55px);
      pointer-events: none;
      z-index: 2;
      animation: coreGlowBreath 6s ease-in-out infinite alternate;
    }}

    @keyframes coreGlowBreath {{
      0% {{ transform: translate(-50%, -50%) scale(0.9); opacity: 0.6; }}
      100% {{ transform: translate(-50%, -50%) scale(1.18); opacity: 1; }}
    }}

    #dashboard-header {{
      position: relative;
      z-index: 10;
      padding: 24px 28px 20px 28px;
      background: rgba(255, 255, 255, 0.95);
      backdrop-filter: blur(12px);
      border-bottom: 1.5px solid #e2e8f0;
      box-shadow: 0 4px 18px rgba(0, 0, 0, 0.03);
    }}

    .dash-top-bar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
    }}

    .dash-title-group {{
      display: flex;
      align-items: center;
      gap: 14px;
    }}

    .dash-icon-badge {{
      position: relative;
      width: 48px;
      height: 48px;
      border-radius: 14px;
      display: grid;
      place-items: center;
      color: #f8fafc;
      font-size: 24px;
      background: linear-gradient(135deg, #0f172a 0%, #334155 35%, #1e293b 65%, #475569 100%);
      background-size: 250% 250%;
      animation: greyGradientFlow 6s ease infinite;
      border: 1px solid rgba(148, 163, 184, 0.25);
      box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.35);
    }}

    .dash-icon-badge::before {{
      content: '';
      position: absolute;
      inset: -4px;
      border-radius: 18px;
      background: radial-gradient(circle, rgba(71, 85, 105, 0.45) 0%, transparent 70%);
      z-index: -1;
      animation: greyAuraPulse 3s ease-in-out infinite alternate;
    }}

    @keyframes greyGradientFlow {{
      0% {{ background-position: 0% 50%; }}
      50% {{ background-position: 100% 50%; }}
      100% {{ background-position: 0% 50%; }}
    }}

    @keyframes greyAuraPulse {{
      0% {{ transform: scale(0.95); opacity: 0.4; filter: blur(4px); }}
      100% {{ transform: scale(1.15); opacity: 0.9; filter: blur(8px); }}
    }}

    .dash-title {{
      font-size: 26px;
      font-weight: 800;
      background: linear-gradient(135deg, #0f172a 30%, #2563eb 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin: 0;
      letter-spacing: -0.5px;
    }}
    .dash-subtitle {{
      font-size: 13px;
      color: #64748b;
      margin: 3px 0 0 0;
      font-weight: 500;
    }}

    .live-beacon {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: #f0fdf4;
      border: 1.5px solid #bbf7d0;
      padding: 7px 16px;
      border-radius: 20px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      font-weight: 700;
      color: #15803d;
      box-shadow: 0 4px 12px rgba(22, 163, 74, 0.12);
    }}
    .live-dot {{
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #16a34a;
      box-shadow: 0 0 10px #16a34a;
      animation: pulse 1.8s infinite ease-in-out;
    }}
    @keyframes pulse {{
      0%, 100% {{ transform: scale(0.85); opacity: 0.6; }}
      50% {{ transform: scale(1.3); opacity: 1; }}
    }}

    .metric-deck {{
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      gap: 16px;
    }}
    .metric-card {{
      position: relative;
      background: #ffffff;
      border-radius: 14px;
      padding: 16px 20px;
      cursor: pointer;
      user-select: none;
      box-shadow: 0 6px 16px rgba(0, 0, 0, 0.04);
      transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }}
    .metric-card.author {{ border: 1.5px solid #fde68a; }}
    .metric-card.author:hover {{ transform: translateY(-4px); border-color: #f59e0b; box-shadow: 0 16px 32px rgba(245, 158, 11, 0.22); }}
    .metric-card.author .mc-num {{ color: #d97706; }}

    .metric-card.commit {{ border: 1.5px solid #a7f3d0; }}
    .metric-card.commit:hover {{ transform: translateY(-4px); border-color: #10b981; box-shadow: 0 16px 32px rgba(16, 185, 129, 0.22); }}
    .metric-card.commit .mc-num {{ color: #059669; }}

    .metric-card.file {{ border: 1.5px solid #bae6fd; }}
    .metric-card.file:hover {{ transform: translateY(-4px); border-color: #0284c7; box-shadow: 0 16px 32px rgba(2, 132, 199, 0.22); }}
    .metric-card.file .mc-num {{ color: #0284c7; }}

    .metric-card.issue {{ border: 1.5px solid #fecdd3; }}
    .metric-card.issue:hover {{ transform: translateY(-4px); border-color: #f43f5e; box-shadow: 0 16px 32px rgba(244, 63, 94, 0.22); }}
    .metric-card.issue .mc-num {{ color: #e11d48; }}

    .metric-card.pr {{ border: 1.5px solid #e9d5ff; }}
    .metric-card.pr:hover {{ transform: translateY(-4px); border-color: #a855f7; box-shadow: 0 16px 32px rgba(168, 85, 247, 0.22); }}
    .metric-card.pr .mc-num {{ color: #7c3aed; }}

    .mc-tag {{
      display: flex;
      align-items: center;
      gap: 6px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      font-weight: 700;
      color: #475569;
      text-transform: uppercase;
      margin-bottom: 8px;
    }}
    .mc-num {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 32px;
      font-weight: 800;
      line-height: 1.1;
    }}
    .mc-pill {{
      font-size: 10px;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 6px;
      margin-left: auto;
    }}
    .mc-pill.author {{ background: #fef3c7; color: #b45309; }}
    .mc-pill.commit {{ background: #dcfce7; color: #15803d; }}
    .mc-pill.file   {{ background: #e0f2fe; color: #0369a1; }}
    .mc-pill.issue  {{ background: #ffe4e6; color: #be123c; }}
    .mc-pill.pr     {{ background: #f3e8ff; color: #7e22ce; }}

    #controls-bar {{
      position: relative;
      z-index: 10;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 12px;
      padding: 12px 28px;
      background: rgba(255, 255, 255, 0.94);
      backdrop-filter: blur(8px);
      border-bottom: 1.5px solid #e2e8f0;
      font-size: 13px;
    }}
    .btn-group {{
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    .btn {{
      background: #ffffff;
      border: 1.5px solid #cbd5e1;
      color: #0f172a;
      padding: 8px 18px;
      border-radius: 9px;
      cursor: pointer;
      font-weight: 700;
      font-size: 12.5px;
      transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1);
      display: inline-flex;
      align-items: center;
      gap: 7px;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
    }}
    .btn:hover {{
      background: #0f172a;
      color: #ffffff;
      border-color: #0f172a;
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(15, 23, 42, 0.14);
    }}
    .btn.active {{
      background: #eff6ff;
      color: #2563eb;
      border-color: #bfdbfe;
    }}

    .legend-group {{
      display: flex;
      align-items: center;
      flex-wrap: wrap;
      gap: 16px;
    }}
    .legend-item {{
      display: inline-flex;
      align-items: center;
      gap: 7px;
      font-size: 12px;
      font-weight: 700;
      color: #334155;
      white-space: nowrap;
    }}
    .legend-dot {{
      width: 10px;
      height: 10px;
      border-radius: 50%;
      display: inline-block;
      flex-shrink: 0;
    }}

    #graph-container {{
      position: relative;
      z-index: 5;
      width: 100%;
      height: 580px;
      background: radial-gradient(#cbd5e1 1.2px, transparent 1.2px);
      background-size: 28px 28px;
      box-shadow: inset 0 0 60px rgba(0, 0, 0, 0.05);
    }}

    #details-panel {{
      position: relative;
      z-index: 10;
      padding: 12px 28px;
      background: #ffffff;
      border-top: 1.5px solid #e2e8f0;
      min-height: 44px;
      font-size: 13px;
      color: #0f172a;
      display: flex;
      align-items: center;
    }}
  </style>
</head>
<body>
  <div id="main-wrapper">
    <canvas id="canvas-bg"></canvas>
    <div class="blur-backdrop-shadow"></div>

    <div id="dashboard-header">
      <div class="dash-top-bar">
        <div class="dash-title-group">
          <div class="dash-icon-badge">
            <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="18" cy="5" r="3"></circle>
              <circle cx="6" cy="12" r="3"></circle>
              <circle cx="18" cy="19" r="3"></circle>
              <line x1="8.59" y1="13.51" x2="15.42" y2="17.49"></line>
              <line x1="15.41" y1="6.51" x2="8.59" y2="10.49"></line>
            </svg>
          </div>
          <div>
            <h1 class="dash-title">Delivery Knowledge Graph</h1>
            <p class="dash-subtitle">
              Active Repository: <b>{repo_name}</b> (ID: #{repo_id}) &middot; Relational delivery memory map
            </p>
          </div>
        </div>
        <div class="live-beacon">
          <span class="live-dot"></span>
          <span>LIVE MEMORY STREAM</span>
        </div>
      </div>

      <div class="metric-deck">
        <div class="metric-card author" data-target="Author" title="Click to filter Authors">
          <div class="mc-tag">👤 Authors <span class="mc-pill author">NODE</span></div>
          <div class="mc-num count-up" data-value="{group_counts.get('Author', 0)}">0</div>
        </div>

        <div class="metric-card commit" data-target="Commit" title="Click to filter Commits">
          <div class="mc-tag">💾 Commits <span class="mc-pill commit">GIT</span></div>
          <div class="mc-num count-up" data-value="{display_commits}">0</div>
          <div style="font-size: 11px; color: #64748b; margin-top: 3px;"><b>{group_counts.get('Commit', 0)}</b> in memory graph</div>
        </div>

        <div class="metric-card file" data-target="File" title="Click to filter Files">
          <div class="mc-tag">📄 Files <span class="mc-pill file">SRC</span></div>
          <div class="mc-num count-up" data-value="{group_counts.get('File', 0)}">0</div>
          <div style="font-size: 11px; color: #64748b; margin-top: 3px;">Tracked changed files</div>
        </div>

        <div class="metric-card issue" data-target="Issue" title="Click to filter Issues">
          <div class="mc-tag">🐛 Issues <span class="mc-pill issue">OPEN</span></div>
          <div class="mc-num count-up" data-value="{display_issues}">0</div>
          <div style="font-size: 11px; color: #64748b; margin-top: 3px;"><b>{imported_issues}</b> imported &middot; <b>{referenced_issues}</b> ref</div>
        </div>

        <div class="metric-card pr" data-target="PullRequest" title="Click to filter Pull Requests">
          <div class="mc-tag">🔀 PRs <span class="mc-pill pr">OPEN</span></div>
          <div class="mc-num count-up" data-value="{display_prs}">0</div>
          <div style="font-size: 11px; color: #64748b; margin-top: 3px;"><b>{imported_prs}</b> imported &middot; <b>{referenced_prs}</b> ref</div>
        </div>
      </div>
    </div>

    <div id="controls-bar" style="display: flex; justify-content: space-between; align-items: center; padding: 12px 24px;">
      <div style="display: flex; gap: 10px;">
        <button class="btn" onclick="resetGraphView()">🎯 Reset</button>
        <button class="btn" onclick="togglePhysics()">⚡ Toggle Physics</button>
      </div>
      <div style="display: flex; align-items: center; gap: 16px; flex-wrap: nowrap;">
        <span class="legend-item"><span class="legend-dot" style="background:#f59e0b;"></span>Author</span>
        <span class="legend-item"><span class="legend-dot" style="background:#a855f7;"></span>Pull Request</span>
        <span class="legend-item"><span class="legend-dot" style="background:#10b981;"></span>Commit</span>
        <span class="legend-item"><span class="legend-dot" style="background:#ffffff;border:1.5px solid #2563eb;"></span>Project Core</span>
        <span class="legend-item"><span class="legend-dot" style="background:#38bdf8;"></span>File</span>
        <span class="legend-item"><span class="legend-dot" style="background:#ef4444;"></span>Issue</span>
      </div>
    </div>

    <div id="graph-container"></div>

    <div id="details-panel">
      <span id="node-info">💡 <i>Click any node to inspect details, or use metric cards above to highlight specific entity groups.</i></span>
    </div>
  </div>

  <script>
    (function initGreyWaveBackground() {{
      const canvas = document.getElementById('canvas-bg');
      const ctx = canvas.getContext('2d');
      let width, height;

      function resize() {{
        width = canvas.width = canvas.offsetWidth;
        height = canvas.height = canvas.offsetHeight;
      }}
      window.addEventListener('resize', resize);
      resize();

      const particles = [];
      for (let i = 0; i < 40; i++) {{
        particles.push({{
          x: Math.random() * width,
          y: Math.random() * height,
          vx: (Math.random() - 0.5) * 0.4,
          vy: (Math.random() - 0.5) * 0.4,
          r: Math.random() * 3 + 1.5,
          alpha: Math.random() * 0.35 + 0.15
        }});
      }}

      let step = 0;
      function loop() {{
        ctx.clearRect(0, 0, width, height);
        step += 0.015;

        for (let i = 0; i < particles.length; i++) {{
          const p = particles[i];
          p.x += p.vx;
          p.y += p.vy;

          if (p.x < 0) p.x = width;
          if (p.x > width) p.x = 0;
          if (p.y < 0) p.y = height;
          if (p.y > height) p.y = 0;

          ctx.beginPath();
          ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
          ctx.fillStyle = 'rgba(71, 85, 105, ' + p.alpha + ')';
          ctx.fill();
        }}

        for (let i = 0; i < particles.length; i++) {{
          for (let j = i + 1; j < particles.length; j++) {{
            const dx = particles[i].x - particles[j].x;
            const dy = particles[i].y - particles[j].y;
            const dist = Math.sqrt(dx * dx + dy * dy);
            if (dist < 110) {{
              ctx.beginPath();
              ctx.moveTo(particles[i].x, particles[i].y);
              ctx.lineTo(particles[j].x, particles[j].y);
              ctx.strokeStyle = 'rgba(100, 116, 139, ' + (0.15 * (1 - dist / 110)) + ')';
              ctx.lineWidth = 1;
              ctx.stroke();
            }}
          }}
        }}

        requestAnimationFrame(loop);
      }}
      loop();
    }})();
  </script>

  <script>
    document.querySelectorAll('.count-up').forEach(el => {{
      const target = parseInt(el.getAttribute('data-value'), 10) || 0;
      let count = 0;
      const duration = 1100;
      const stepTime = 25;
      const step = Math.max(1, Math.ceil(target / (duration / stepTime)));
      
      const timer = setInterval(() => {{
        count += step;
        if (count >= target) {{
          el.innerText = target;
          clearInterval(timer);
        }} else {{
          el.innerText = count;
        }}
      }}, stepTime);
    }});
  </script>

  <script>
    var rawNodes = {nodes_json};
    var rawEdges = {edges_json};

    var brainNodeId = null;

    var groupStyles = {{
      Author: {{
        color: {{ background: '#f59e0b', border: '#d97706', highlight: {{ background: '#fbbf24', border: '#b45309' }} }},
        shape: 'dot',
        size: 24,
        shadow: {{ enabled: true, color: 'rgba(245, 158, 11, 0.25)', size: 16, x: 0, y: 3 }}
      }},
      PullRequest: {{
        color: {{ background: '#a855f7', border: '#7e22ce', highlight: {{ background: '#c084fc', border: '#6b21a8' }} }},
        shape: 'triangle',
        size: 20,
        shadow: {{ enabled: true, color: 'rgba(168, 85, 247, 0.25)', size: 14, x: 0, y: 3 }}
      }},
      Commit: {{
        color: {{ background: '#10b981', border: '#059669', highlight: {{ background: '#34d399', border: '#047857' }} }},
        shape: 'hexagon',
        size: 19,
        shadow: {{ enabled: true, color: 'rgba(168, 85, 247, 0.25)', size: 14, x: 0, y: 3 }}
      }},
      File: {{
        color: {{ background: '#ffffff', border: '#38bdf8', highlight: {{ background: '#f0f9ff', border: '#0284c7' }} }},
        shape: 'box',
        shapeProperties: {{ borderRadius: 8 }},
        margin: {{ top: 8, bottom: 8, left: 14, right: 14 }},
        shadow: {{ enabled: true, color: 'rgba(56, 189, 248, 0.22)', size: 14, x: 0, y: 3 }}
      }},
      Issue: {{
        color: {{ background: '#ef4444', border: '#b91c1c', highlight: {{ background: '#f87171', border: '#991b1b' }} }},
        shape: 'diamond',
        size: 24,
        shadow: {{ enabled: true, color: 'rgba(239, 68, 68, 0.35)', size: 16, x: 0, y: 3 }}
      }}
    }};

    var styledNodes = rawNodes.map(function(n) {{
      var s = groupStyles[n.group] || groupStyles.File;

      var isMainFile = n.group === 'File' && (
        n.label.toLowerCase().includes('readme') ||
        n.label.toLowerCase().includes('index') ||
        n.label.toLowerCase().includes('main') ||
        n.label.toLowerCase().includes('package')
      );

      if (isMainFile) {{
        brainNodeId = n.id;
        return {{
          id: n.id,
          label: '🧠 Project Brain',
          group: n.group,
          shape: 'box',
          shapeProperties: {{ borderRadius: 10 }},
          margin: {{ top: 12, bottom: 12, left: 22, right: 22 }},
          color: {{
            background: '#ffffff',
            border: '#2563eb',
            highlight: {{ background: '#eff6ff', border: '#1d4ed8' }},
            hover: {{ background: '#f8fafc', border: '#06b6d4' }}
          }},
          borderWidth: 2.5,
          font: {{
            color: '#0f172a',
            size: 14,
            face: 'Space Grotesk, system-ui',
            bold: true
          }},
          shadow: {{
            enabled: true,
            color: 'rgba(37, 99, 235, 0.25)',
            size: 26,
            x: 0,
            y: 4
          }}
        }};
      }}

      return {{
        id: n.id,
        label: n.label,
        group: n.group,
        shape: s.shape,
        shapeProperties: s.shapeProperties || {{ borderRadius: 6 }},
        size: s.size,
        margin: s.margin || {{ top: 6, bottom: 6, left: 10, right: 10 }},
        color: s.color,
        borderWidth: 1.5,
        font: {{
          color: '#0f172a',
          size: 12,
          face: 'Space Grotesk, system-ui',
          strokeWidth: 3,
          strokeColor: '#ffffff'
        }},
        shadow: s.shadow
      }};
    }});

    var styledEdges = rawEdges.map(function(e) {{
      return {{
        from: e.from,
        to: e.to,
        title: e.title,
        arrows: {{ to: {{ enabled: true, scaleFactor: 0.65 }} }},
        color: {{
          color: '#94a3b8',
          highlight: '#2563eb',
          hover: '#06b6d4',
          opacity: 0.85
        }},
        width: 1.6,
        hoverWidth: 3.8,
        selectionWidth: 4.2,
        shadow: {{
          enabled: true,
          color: 'rgba(6, 182, 212, 0.45)',
          size: 8,
          x: 0,
          y: 0
        }},
        smooth: {{ type: 'cubicBezier', roundness: 0.25 }}
      }};
    }});

    var container = document.getElementById('graph-container');
    var nodesDataSet = new vis.DataSet(styledNodes);
    var edgesDataSet = new vis.DataSet(styledEdges);
    var data = {{ nodes: nodesDataSet, edges: edgesDataSet }};

    var organicOptions = {{
      physics: {{
        solver: 'forceAtlas2Based',
        forceAtlas2Based: {{
          gravitationalConstant: -140,
          centralGravity: 0.038,
          springLength: 150,
          springConstant: 0.06,
          damping: 0.5
        }},
        stabilization: {{ iterations: 180 }}
      }},
      interaction: {{
        hover: true,
        hoverConnectedEdges: true,
        selectConnectedEdges: true,
        tooltipDelay: 350
      }}
    }};

    var network = new vis.Network(container, data, organicOptions);
    var physicsActive = true;

    network.once('stabilizationIterationsDone', function() {{
      network.fit({{ animation: false }});
    }});

    let animPulse = 0;
    network.on("beforeDrawing", function(ctx) {{
      animPulse += 0.02;
      if (!brainNodeId) return;

      const pos = network.getPositions([brainNodeId])[brainNodeId];
      if (!pos) return;

      const numWaves = 6;
      const maxRadius = 780;

      for (let w = 0; w < numWaves; w++) {{
        const progress = ((animPulse * 0.35 + w / numWaves) % 1);
        const waveRadius = 45 + progress * maxRadius;
        const waveAlpha = Math.sin(progress * Math.PI) * 0.35 * (1 - progress * 0.3);

        if (waveAlpha > 0.005) {{
          ctx.beginPath();
          ctx.arc(pos.x, pos.y, waveRadius, 0, 2 * Math.PI, false);
          ctx.strokeStyle = 'rgba(148, 163, 184, ' + waveAlpha + ')';
          ctx.lineWidth = 1.3;
          ctx.stroke();
        }}
      }}

      const baseRadius = 52;
      const pulseSize = Math.sin(animPulse * 2.2) * 5;
      const currentRadius = baseRadius + pulseSize;

      const coreGradient = ctx.createRadialGradient(pos.x, pos.y, 5, pos.x, pos.y, currentRadius + 40);
      coreGradient.addColorStop(0, 'rgba(148, 163, 184, 0.22)');
      coreGradient.addColorStop(0.5, 'rgba(203, 213, 225, 0.12)');
      coreGradient.addColorStop(1, 'rgba(255, 255, 255, 0)');

      ctx.beginPath();
      ctx.arc(pos.x, pos.y, currentRadius + 40, 0, 2 * Math.PI, false);
      ctx.fillStyle = coreGradient;
      ctx.fill();

      const numCenterRipples = 3;
      for (let r = 0; r < numCenterRipples; r++) {{
        const ripProgress = ((animPulse * 0.8 + r / numCenterRipples) % 1);
        const ripRadius = 38 + ripProgress * 55;
        const ripAlpha = (1 - ripProgress) * 0.35;

        ctx.beginPath();
        ctx.arc(pos.x, pos.y, ripRadius, 0, 2 * Math.PI, false);
        ctx.strokeStyle = 'rgba(100, 116, 139, ' + ripAlpha + ')';
        ctx.lineWidth = 1.3;
        ctx.stroke();
      }}

      ctx.save();
      ctx.translate(pos.x, pos.y);
      ctx.rotate(animPulse * 0.4);

      ctx.beginPath();
      ctx.arc(0, 0, 68, 0, 2 * Math.PI, false);
      ctx.setLineDash([4, 6]);
      ctx.strokeStyle = 'rgba(148, 163, 184, 0.45)';
      ctx.lineWidth = 1.2;
      ctx.stroke();
      ctx.restore();
    }});

    function triggerRedraw() {{
      network.redraw();
      requestAnimationFrame(triggerRedraw);
    }}
    requestAnimationFrame(triggerRedraw);

    function togglePhysics() {{
      physicsActive = !physicsActive;
      network.setOptions({{ physics: {{ enabled: physicsActive }} }});
      const btn = document.getElementById('btn-physics');
      if (btn) {{
        btn.innerHTML = physicsActive ? '⚡ Physics: ON' : '⏸️ Physics: OFF';
        btn.classList.toggle('active', !physicsActive);
      }}
      document.getElementById('node-info').innerHTML = physicsActive 
        ? '⚡ <i>Physics simulation enabled.</i>' 
        : '⏸️ <i>Physics frozen in place. You can drag and position nodes manually.</i>';
    }}

    function resetGraphView() {{
      nodesDataSet.forEach(node => {{
        nodesDataSet.update({{ id: node.id, hidden: false }});
      }});
      network.fit({{ animation: true }});
      document.getElementById('node-info').innerHTML = '💡 <i>Graph view reset. Showing all entities.</i>';
    }}

    document.querySelectorAll('.metric-card').forEach(card => {{
      card.addEventListener('click', () => {{
        const targetGroup = card.getAttribute('data-target');
        const selectedIds = [];

        nodesDataSet.forEach(node => {{
          if (node.group === targetGroup || (targetGroup === 'File' && node.label.includes('Project Brain'))) {{
            selectedIds.push(node.id);
          }}
        }});

        if (selectedIds.length > 0) {{
          network.selectNodes(selectedIds);
          network.fit({{ nodes: selectedIds, animation: true }});
          document.getElementById('node-info').innerHTML = 
            `<b>Filtered:</b> Highlighting and focusing all <b>${{selectedIds.length}} ${{targetGroup}}</b> entities in the knowledge graph.`;
        }}
      }});
    }});

    network.on("click", function(params) {{
      if (params.nodes.length > 0) {{
        var nodeId = params.nodes[0];
        var n = nodesDataSet.get(nodeId);
        document.getElementById('node-info').innerHTML = 
          '<b>Selected Node:</b> <span style="background:#0f172a; color:#ffffff; padding:3px 8px; border-radius:4px; font-weight:bold;">[' + n.group + '] ' + n.label + '</span> &mdash; ' + (n.title || '');
      }}
    }});
  </script>
</body>
</html>
"""

components.html(dashboard_and_graph_html, height=840)

# DIAGNOSTICS AUDIT

with st.expander("🔍 Graph Diagnostics & Authoritative Integrity Audit", expanded=True):
    total_edges_val = audit.get('total_edges', len(edges))
    connected_comps_val = audit.get('connected_components', 1)

    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:12px; flex-wrap:wrap; background:#ffffff; border:1.5px solid #e2e8f0; padding:12px 18px; border-radius:12px; margin-bottom:18px; font-size:13px; color:#334155; box-shadow:0 1px 3px rgba(0,0,0,0.02);">
      <span>📁 <b>Repository:</b> <span style="background:#f1f5f9; color:#0f172a; padding:2px 8px; border-radius:5px; font-family:'JetBrains Mono', monospace; font-size:12px; font-weight:600; border:1px solid #e2e8f0;">{repo_name}</span> (ID: <code style="color:#0f172a; font-weight:700;">#{repo_id}</code>)</span>
      <span style="color:#cbd5e1;">|</span>
      <span>🔗 <b>Total Verified Edges:</b> <span style="background:#eff6ff; color:#2563eb; padding:2px 8px; border-radius:5px; font-family:'JetBrains Mono', monospace; font-size:12px; font-weight:700; border:1px solid #bfdbfe;">{total_edges_val}</span></span>
      <span style="color:#cbd5e1;">|</span>
      <span>🧩 <b>Connected Components:</b> <span style="background:#ecfdf5; color:#059669; padding:2px 8px; border-radius:5px; font-family:'JetBrains Mono', monospace; font-size:12px; font-weight:700; border:1px solid #a7f3d0;">{connected_comps_val}</span></span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="display:flex; align-items:center; gap:12px; margin: 18px 0 14px 0;">
      <div style="width:36px; height:36px; border-radius:10px; background:#0f172a; display:grid; place-items:center; flex-shrink:0; box-shadow:0 2px 6px rgba(15,23,42,0.18);">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="18" cy="5" r="3"></circle>
          <circle cx="6" cy="12" r="3"></circle>
          <circle cx="18" cy="19" r="3"></circle>
          <line x1="8.59" y1="13.51" x2="15.42" y2="17.49"></line>
          <line x1="15.41" y1="6.51" x2="8.59" y2="10.49"></line>
        </svg>
      </div>
      <div>
        <div style="font-weight:800; font-size:17px; color:#0f172a; letter-spacing:-0.2px;">Authoritative Entity &amp; Node Breakdown</div>
        <div style="font-size:12px; color:#64748b; font-weight:500;">Verifiable delivery memory graph entity counts and database provenance</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.markdown(f"""
| Issue Pipeline Metric | Value |
| :--- | :--- |
| **Selected Repository ID** | `{repo_id}` |
| **Selected Repository Name** | `{repo_name}` |
| **Database Issue Row Count** | `{repo_stats.get('issues_count', audit.get('database_issues_count', 0))}` |
| **GitHub Open Issues Count** | `{display_issues}` |
| **Distinct Issue Number Count** | `{repo_stats.get('distinct_issues_count', audit.get('database_issues_count', 0))}` |
| **Database-Derived Issue Node Count** | `{imported_issues}` |
| **Relationship-Only Issue Node Count** | `{referenced_issues}` |
| **Final Graph Issue Node Count** | `{total_issues}` |
""")

    with col_d2:
        st.markdown(f"""
| PR & Relationship Metric | Value |
| :--- | :--- |
| **GitHub Total Commits Count** | `{display_commits}` |
| **GitHub Open PRs Count** | `{display_prs}` |
| **PullRequest Record Count** | `{repo_stats.get('pull_requests_count', audit.get('database_prs_count', 0))}` |
| **RelationshipRecord Count** | `{repo_stats.get('relationships_count', audit.get('relationships_count', 0))}` |
| **Database-Derived PR Node Count** | `{imported_prs}` |
| **Relationship-Only PR Node Count** | `{referenced_prs}` |
| **Final Graph PR Node Count** | `{total_prs}` |
| **Total Graph Nodes** | `{len(nodes)}` |
| **Total Graph Edges** | `{len(edges)}` |
""")

    isolated = audit.get("isolated_nodes", [])
    if isolated:
        st.warning(f"Detected {len(isolated)} isolated node(s) without links in this batch:")
        st.table(isolated)
    else:
        st.success("✅ All nodes in the delivery memory graph are connected by verified historical relationships.")