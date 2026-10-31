import os
import sys
import httpx
import streamlit as st

BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Project Description | Project Brain",
    page_icon="📖",
    layout="wide"
)

# 1. Path setup
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
project_root = os.path.abspath(os.path.join(parent_dir, ".."))
for p in [current_dir, parent_dir, project_root]:
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

# 3. NOW fetch repositories and data
repos = fetch_repositories()
current_repo = get_active_repo(repos)
repo_id = current_repo["id"] if current_repo else None

try:
    from sidebar_nav import render_sidebar
    render_sidebar(repos=repos, key="desc_repo_select")
except Exception:
    pass

repo_name = f"{current_repo['owner']}/{current_repo['name']}" if current_repo else "No repository selected"

if not repo_id:
    st.warning("⚠️ Please select or import a repository on the main dashboard first!")
    st.stop()

# PAGE STYLES

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

.stApp,
[data-testid="stAppViewContainer"] {
    background: #f8fafc !important;
    color: #0f172a !important;
    font-family: 'Inter', -apple-system, sans-serif !important;
}

header[data-testid="stHeader"] { background: transparent !important; }
#MainMenu, footer { visibility: hidden; }

.block-container {
    max-width: 1200px !important;
    padding-top: 1.5rem !important;
    padding-bottom: 3rem !important;
}

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

.metric-deck {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 24px;
}

.metric-card {
    background: #ffffff;
    border: 1.5px solid #e2e8f0;
    border-radius: 14px;
    padding: 18px 20px;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.02);
    transition: all 0.25s ease;
}

.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 24px -4px rgba(15, 23, 42, 0.06);
    border-color: #cbd5e1;
}

.mc-title {
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    color: #64748b;
    margin-bottom: 6px;
}

.mc-val {
    font-size: 24px;
    font-weight: 800;
    color: #0f172a;
    line-height: 1.1;
}

.mc-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    margin-top: 8px;
    padding: 3px 8px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 600;
}

.content-card {
    background: #ffffff;
    border: 1.5px solid #e2e8f0;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    margin-bottom: 22px;
}

.card-title-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-bottom: 14px;
    margin-bottom: 16px;
    border-bottom: 1.5px solid #f1f5f9;
}

.card-heading {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 16px;
    font-weight: 800;
    color: #0f172a;
    letter-spacing: -0.2px;
}

.tech-tag {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #f1f5f9;
    color: #0f172a;
    border: 1px solid #e2e8f0;
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 12px;
    font-weight: 600;
    margin-right: 8px;
    margin-bottom: 8px;
}

.stMarkdown table {
    width: 100% !important;
    border-collapse: separate !important;
    border-spacing: 0 !important;
    border: 1.5px solid #e2e8f0 !important;
    border-radius: 12px !important;
    overflow: hidden !important;
    background: #ffffff !important;
}

.stMarkdown th {
    background: #f8fafc !important;
    color: #0f172a !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    padding: 12px 16px !important;
    border-bottom: 1.5px solid #e2e8f0 !important;
    text-align: left !important;
}

.stMarkdown td {
    padding: 10px 16px !important;
    font-size: 13px !important;
    color: #334155 !important;
    border-bottom: 1px solid #f1f5f9 !important;
}

.stMarkdown tr:last-child td {
    border-bottom: none !important;
}

.stMarkdown td code {
    background: #eff6ff !important;
    color: #1d4ed8 !important;
    border: 1px solid #bfdbfe !important;
    border-radius: 5px !important;
    padding: 2px 7px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12px !important;
    font-weight: 600 !important;
}

.tree-container {
    background: #0f172a;
    color: #f8fafc;
    border-radius: 12px;
    padding: 18px 22px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12.5px;
    line-height: 1.65;
    max-height: 480px;
    overflow-y: auto;
    border: 1px solid #1e293b;
    box-shadow: inset 0 2px 6px rgba(0,0,0,0.3);
}

.tree-folder {
    color: #38bdf8;
    font-weight: 700;
}

.tree-file {
    color: #94a3b8;
}

.tree-file:hover {
    color: #ffffff;
}

div.stButton > button {
    background-color: #0f172a !important;
    color: #ffffff !important;
    border: 1.5px solid #0f172a !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 9px 18px !important;
    transition: all 0.2s ease !important;
}

div.stButton > button:hover {
    background-color: #2563eb !important;
    border-color: #2563eb !important;
    color: #ffffff !important;
    box-shadow: 0 6px 18px rgba(37, 99, 235, 0.35) !important;
    transform: translateY(-1px) !important;
}
</style>
""", unsafe_allow_html=True)

# TOP HEADER BAR
st.markdown(f"""
<div class="top-header">
  <div class="header-left">
    <div class="header-badge">
      <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round">
        <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
        <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
        <line x1="9" y1="7" x2="15" y2="7"></line>
        <line x1="9" y1="11" x2="13" y2="11"></line>
      </svg>
    </div>
    <div>
      <h2 class="header-title">Project Description &amp; Architecture</h2>
      <div class="header-subtitle">
        Active Repository: <b>{repo_name}</b> &middot; Purpose, structural hierarchy, and AI intelligence analysis
      </div>
    </div>
  </div>
  <div>
    <span class="header-pill">
      <span class="pill-dot"></span> Repository Anatomy
    </span>
  </div>
</div>
""", unsafe_allow_html=True)

# FETCH REPOSITORY DESCRIPTION & TREE DATA
repo_data = {}
with st.spinner("Fetching repository metadata and directory hierarchy..."):
    try:
        resp = httpx.get(f"{BACKEND_URL}/api/repositories/{repo_id}/description", timeout=25.0)
        if resp.status_code == 200:
            repo_data = resp.json()
    except Exception as e:
        st.error(f"Failed to fetch repository details: {e}")

if not repo_data:
    st.error("Could not retrieve repository structure. Please ensure the backend server is running.")
    st.stop()

# FOUR HIGH-LEVEL METRIC CARDS

lang_val = repo_data.get("language") or "Mixed"
files_count = repo_data.get("total_files", 0)
stars_val = repo_data.get("stars", 0)
forks_val = repo_data.get("forks", 0)
branch_val = repo_data.get("default_branch", "main")
has_native_desc = repo_data.get("has_native_description", False)

st.markdown(f"""
<div class="metric-deck">
  <div class="metric-card">
    <div class="mc-title">Primary Language</div>
    <div class="mc-val">{lang_val}</div>
    <div class="mc-badge" style="background: #eff6ff; color: #2563eb;">
      <span>●</span> Detected Stack
    </div>
  </div>

  <div class="metric-card">
    <div class="mc-title">Repository Files</div>
    <div class="mc-val">{files_count}</div>
    <div class="mc-badge" style="background: #ecfdf5; color: #059669;">
      <span>✓</span> Verified Tree
    </div>
  </div>

  <div class="metric-card">
    <div class="mc-title">Community Stars &amp; Forks</div>
    <div class="mc-val">⭐ {stars_val} &nbsp; 🍴 {forks_val}</div>
    <div class="mc-badge" style="background: #fef3c7; color: #d97706;">
      <span>★</span> GitHub Public
    </div>
  </div>

  <div class="metric-card">
    <div class="mc-title">Default Branch</div>
    <div class="mc-val"><code>{branch_val}</code></div>
    <div class="mc-badge" style="background: #f1f5f9; color: #475569;">
      <span>⑂</span> Provenance Root
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# PROJECT DESCRIPTION

desc_text = repo_data.get("description") or "No description provided."
source_badge = '<span style="background: #ecfdf5; color: #059669; padding: 3px 10px; border-radius: 20px; font-size: 11.5px; font-weight: 700; border: 1px solid #a7f3d0;">✓ Official GitHub Description</span>' if has_native_desc else '<span style="background: #eff6ff; color: #2563eb; padding: 3px 10px; border-radius: 20px; font-size: 11.5px; font-weight: 700; border: 1px solid #bfdbfe;">⚡ Inferred by Intelligence Engine</span>'

st.markdown(f"""
<div class="content-card">
  <div class="card-title-row">
    <div class="card-heading">
      <span>🎯</span> Project Purpose &amp; Executive Summary
    </div>
    <div>{source_badge}</div>
  </div>
  <div style="font-size: 15px; line-height: 1.7; color: #1e293b; font-weight: 500; margin-bottom: 18px;">
    {desc_text}
  </div>
""", unsafe_allow_html=True)

# Detected Tech Stack Badges
detected_stack = repo_data.get("heuristic", {}).get("detected_stack", [])
topics = repo_data.get("topics", [])
all_tags = list(set(detected_stack + topics))
if all_tags:
    tags_html = "".join([f'<span class="tech-tag">🏷️ {t}</span>' for t in all_tags])
    st.markdown(f"""
    <div style="margin-top: 14px; padding-top: 14px; border-top: 1px solid #f1f5f9;">
      <div style="font-size: 12px; font-weight: 700; color: #64748b; text-transform: uppercase; margin-bottom: 8px;">Technologies &amp; Topics</div>
      <div>{tags_html}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# DIRECTORY

st.markdown("""
<div class="content-card">
  <div class="card-title-row">
    <div class="card-heading">
      <span>📂</span> Directory Structure &amp; Architectural Hierarchy
    </div>
    <div style="font-size: 12px; color: #64748b; font-weight: 500;">
      Verifiable file layout extracted from repository tree
    </div>
  </div>
""", unsafe_allow_html=True)

tab_overview, tab_tree = st.tabs(["📊 Top-Level Directory Roles", "🌲 Interactive Tree View"])

with tab_overview:
    top_dirs = repo_data.get("top_directories", [])
    if top_dirs:
        table_rows = ""
        for td in top_dirs:
            ext_str = ", ".join([f"<code>{e}</code>" for e in td.get("extensions", [])]) or "mixed"
            table_rows += f"""
| 📁 `{td['directory']}/` | `{td['file_count']} files` | {ext_str} | {td['role']} |
"""
        st.markdown(f"""
| Directory | Total Files | Dominant Types | Architectural Responsibility |
| :--- | :--- | :--- | :--- |
{table_rows}
""")
    else:
        st.info("No subdirectories detected; repository files are in root.")

with tab_tree:
    all_paths = repo_data.get("file_paths", [])
    search_q = st.text_input("🔍 Filter files or paths", placeholder="e.g. src/, action.yml, test", key="tree_search_query")
    
    filtered_paths = all_paths
    if search_q.strip():
        q = search_q.strip().lower()
        filtered_paths = [p for p in all_paths if q in p.lower()]

    st.caption(f"Displaying {len(filtered_paths)} matching file path(s) out of {len(all_paths)} total files.")

    # Render formatted ASCII / Unicode Tree
    def format_tree_text(paths: list, limit: int = 150) -> str:
        lines = []
        for p in paths[:limit]:
            parts = p.split("/")
            indent = "  " * (len(parts) - 1)
            icon = "📁 " if len(parts) > 1 and parts[-1] == "" else ("📄 " if "." in parts[-1] else "📦 ")
            lines.append(f"{indent}{icon}{parts[-1]}")
        if len(paths) > limit:
            lines.append(f"... and {len(paths) - limit} more files")
        return "\n".join(lines)

    tree_text = format_tree_text(filtered_paths)
    st.markdown(f"""
    <div class="tree-container">
      <pre style="margin: 0; background: transparent; color: inherit; font-size: inherit; border: none; padding: 0;">{tree_text}</pre>
    </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# AI REPOSITORY ANALYZER
st.markdown("""
<div class="content-card">
  <div class="card-title-row">
    <div class="card-heading">
      <span>🤖</span> AI Deep Repository Analyzer &amp; Purpose Synthesizer
    </div>
    <span style="display:inline-flex; align-items:center; gap:6px; background:#eff6ff; color:#2563eb; border:1px solid #bfdbfe; padding:4px 12px; border-radius:20px; font-size:11.5px; font-weight:700;">
      <span>✨</span> LLM Architectural Audit
    </span>
  </div>
  <div style="font-size: 13.5px; color: #475569; margin-bottom: 16px; line-height: 1.6;">
    If a repository lacks detailed documentation, integrate an AI API (Google Gemini, Groq, or OpenAI) to perform an in-depth architectural audit, synthesize executive purpose, and generate an annotated directory guide.
  </div>
""", unsafe_allow_html=True)

col_ai_cfg1, col_ai_cfg2, col_ai_btn = st.columns([1, 1.6, 1], gap="medium")

with col_ai_cfg1:
    ai_provider = st.selectbox(
        "AI Provider",
        ["Google Gemini", "Groq (Llama 3.3)", "OpenAI (GPT-4o)"],
        key="ai_provider_select"
    )

provider_key_map = {
    "Google Gemini": ("gemini", os.getenv("GEMINI_API_KEY", "")),
    "Groq (Llama 3.3)": ("groq", os.getenv("GROQ_API_KEY", "")),
    "OpenAI (GPT-4o)": ("openai", os.getenv("OPENAI_API_KEY", "")),
}

selected_provider_code, default_key = provider_key_map.get(ai_provider, ("gemini", ""))

with col_ai_cfg2:
    entered_api_key = st.text_input(
        "API Key",
        value=st.session_state.get(f"key_{selected_provider_code}", default_key),
        type="password",
        placeholder=f"Enter {ai_provider} API key...",
        help=f"Optional: enter your personal {ai_provider} API key. Never logged or stored on disk.",
        key=f"input_key_{selected_provider_code}"
    )
    if entered_api_key:
        st.session_state[f"key_{selected_provider_code}"] = entered_api_key

with col_ai_btn:
    st.write("")
    st.write("")
    run_ai = st.button("🚀 Analyze with AI", use_container_width=True, key="btn_run_ai_analysis")

analysis_cache_key = f"ai_analysis_{repo_id}"
if run_ai:
    active_key = entered_api_key or default_key
    if not active_key:
        st.error(f"⚠️ Please enter a valid API key for {ai_provider} to run deep AI analysis.")
    else:
        with st.spinner(f"Analyzing {repo_name} using {ai_provider}... Parsing manifests and directory hierarchy..."):
            try:
                ai_payload = {
                    "provider": selected_provider_code,
                    "api_key": active_key.strip()
                }
                ai_resp = httpx.post(
                    f"{BACKEND_URL}/api/repositories/{repo_id}/ai-analyze",
                    json=ai_payload,
                    timeout=50.0
                )
                if ai_resp.status_code == 200:
                    ai_result = ai_resp.json()
                    if ai_result.get("success"):
                        st.session_state[analysis_cache_key] = ai_result
                        st.success(f"✅ Deep AI Analysis completed via {ai_result.get('provider')}!")
                    else:
                        st.error(ai_result.get("error", "AI analysis request failed."))
                else:
                    st.error(f"Backend returned status {ai_resp.status_code}: {ai_resp.text}")
            except Exception as e:
                st.error(f"Error calling AI Analyzer endpoint: {e}")

if analysis_cache_key in st.session_state:
    cached = st.session_state[analysis_cache_key]
    st.markdown(f"""
    <div style="margin-top: 18px; padding: 22px; background: #ffffff; border: 1.5px solid #bfdbfe; border-radius: 14px; box-shadow: 0 4px 16px rgba(37, 99, 235, 0.06);">
      <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; padding-bottom: 10px; border-bottom: 1.5px solid #eff6ff;">
        <span style="font-weight: 800; font-size: 15px; color: #1d4ed8;">⚡ Generated Architectural Intelligence ({cached.get('provider')})</span>
        <span style="font-size: 11px; color: #64748b;">Live Synthesized</span>
      </div>
    """, unsafe_allow_html=True)
    st.markdown(cached.get("analysis", ""))
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# RAW REPOSITORY README VIEWER
readme_body = repo_data.get("readme")
if readme_body:
    with st.expander("📄 View Official Repository README.md", expanded=False):
        st.markdown(readme_body)

