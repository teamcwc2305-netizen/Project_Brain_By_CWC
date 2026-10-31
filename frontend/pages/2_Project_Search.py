# frontend/pages/2_Project_Search.py
import os
import sys
import httpx
import streamlit as st

BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Project Search & Intelligence | Project Brain",
    page_icon="🔍",
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

# 3. NOW fetch repositories and data
repos = fetch_repositories()
current_repo = get_active_repo(repos)
repo_id = current_repo["id"] if current_repo else None

try:
    from sidebar_nav import render_sidebar
    render_sidebar(repos=repos, key="search_repo_select")
except Exception:
    pass

repo_name = f"{current_repo['owner']}/{current_repo['name']}" if current_repo else "No repository selected"

if not repo_id:
    st.warning("⚠️ Please select or import a repository on the main dashboard first!")
    st.stop()


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

.stApp,
[data-testid="stAppViewContainer"] {
    background: #f8fafc !important;
    color: #0f172a !important;
    font-family: 'Inter', -apple-system, sans-serif !important;
}

header[data-testid="stHeader"] {
    background: transparent !important;
}

#MainMenu,
footer {
    visibility: hidden;
}

.block-container {
    max-width: 1180px !important;
    padding-top: 1.5rem !important;
    padding-bottom: 3rem !important;
}

/* TOP HEADER */
.top-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 6px 0 18px 0;
    border-bottom: 1.5px solid #e2e8f0;
    margin-bottom: 24px;
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

/* HERO CARD */
.search-hero {
    background: #ffffff;
    border: 1.5px solid #cbd5e1;
    border-radius: 20px;
    padding: 34px 38px;
    margin-bottom: 24px;
    box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.03);
}

.hero-tag {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    background: #eff6ff;
    color: #2563eb;
    border: 1px solid #bfdbfe;
    padding: 5px 13px;
    border-radius: 30px;
    font-size: 10.5px;
    font-weight: 700;
    letter-spacing: 0.6px;
    margin-bottom: 16px;
}

.hero-title {
    color: #0f172a;
    font-size: 30px;
    font-weight: 800;
    letter-spacing: -0.6px;
    line-height: 1.25;
    margin-bottom: 12px;
}

.hero-description {
    color: #64748b;
    font-size: 14px;
    line-height: 1.65;
    max-width: 820px;
    margin: 0;
}

div[data-baseweb="input"] > div {
    background: #1e293b !important;
    border: 1.5px solid #334155 !important;
    border-radius: 12px !important;
    min-height: 48px !important;
    padding: 2px 10px !important;
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08) !important;
    transition: all 0.2s ease !important;
}

div[data-baseweb="input"] > div:focus-within {
    border-color: #2563eb !important;
    background: #0f172a !important;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.30) !important;
}

div[data-baseweb="input"] input {
    color: #f8fafc !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 13.5px !important;
    background: transparent !important;
}

div[data-baseweb="input"] input::placeholder {
    color: #94a3b8 !important;
    font-size: 13px !important;
}

div[data-testid="stButton"] > button {
    background: #0f172a !important;
    color: #ffffff !important;
    border: 1.5px solid #0f172a !important;
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 700 !important;
    font-size: 13.5px !important;
    min-height: 44px !important;
    padding: 10px 24px !important;
    transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1) !important;
    box-shadow: 0 4px 10px rgba(15, 23, 42, 0.15) !important;
}

div[data-testid="stButton"] > button:hover {
    background: #2563eb !important;
    border-color: #2563eb !important;
    color: #ffffff !important;
    transform: translateY(-2px);
    box-shadow: 0 8px 22px -4px rgba(37, 99, 235, 0.40) !important;
}

div[data-testid="stButton"] > button:active {
    background: #1d4ed8 !important;
    border-color: #1d4ed8 !important;
    transform: translateY(0px) !important;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff !important;
    border: 1.5px solid #e2e8f0 !important;
    border-radius: 16px !important;
    box-shadow: 0 4px 18px rgba(15, 23, 42, 0.04) !important;
}

[data-testid="stAlert"] {
    border-radius: 12px !important;
}

[data-testid="stMarkdownContainer"] a {
    color: #2563eb !important;
    font-weight: 600;
    text-decoration: none !important;
}

[data-testid="stMarkdownContainer"] a:hover {
    color: #1d4ed8 !important;
    text-decoration: underline !important;
}

[data-testid="stMarkdownContainer"] code {
    background: #eff6ff !important;
    color: #2563eb !important;
    border: 1px solid #dbeafe !important;
    border-radius: 6px !important;
    padding: 3px 8px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11.5px !important;
}

hr {
    border-color: #e2e8f0 !important;
    margin: 24px 0 !important;
}
</style>
""", unsafe_allow_html=True)


# TOP HEADER BAR

st.markdown(f"""
<div class="top-header">
  <div class="header-left">
    <div class="header-badge">
      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="11" cy="11" r="8"></circle>
        <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
      </svg>
    </div>
    <div>
      <h2 class="header-title">Project Search & Intelligence</h2>
      <div class="header-subtitle">
        Active Repository: <b>{repo_name}</b> &middot; Evidence-backed question answering
      </div>
    </div>
  </div>
  <div>
    <span class="header-pill">
      <span class="pill-dot"></span> Deterministic Search
    </span>
  </div>
</div>
""", unsafe_allow_html=True)


# HERO CARD SECTION

st.markdown("""
<div class="search-hero">
  <div class="hero-tag">
    <span style="width: 7px; height: 7px; border-radius: 50%; background: #2563eb; display: inline-block;"></span>
    PROJECT BRAIN &middot; NEURAL MEMORY
  </div>
  <div class="hero-title">
    Deterministic Question Answering & Search
  </div>
  <p class="hero-description">
    Find developer decisions, commits, file ownership and project relationships using verifiable repository records. Absolutely zero generative AI or hallucinations.
  </p>
</div>
""", unsafe_allow_html=True)


# SEARCH INPUT & ACTION

query = st.text_input(
    "Search Query",
    placeholder='e.g. "What is connected to issue 101?", "Who worked on README.md?", "Commit fa79561", "auth"',
    label_visibility="collapsed",
    key="project_search_query_input"
)

col_btn, _ = st.columns([1, 4])

with col_btn:
    search_btn = st.button(
        "Query Memory",
        type="primary",
        use_container_width=True,
        key="btn_query_memory"
    )


#  SEARCH EXECUTION & RESULTS

if search_btn and query:
    try:
        with st.spinner("Traversing records and knowledge graph..."):
            resp = httpx.post(
                f"{BACKEND_URL}/api/repositories/{repo_id}/search",
                json={"query": query},
                timeout=30.0
            )

        if resp.status_code == 200:
            data = resp.json()

            st.markdown("""
            <div style="display:flex;align-items:center;gap:10px;margin-top:28px;margin-bottom:14px;">
              <div style="width:4px;height:24px;background:#2563eb;border-radius:4px;"></div>
              <span style="font-size:21px;font-weight:800;color:#0f172a;">Answer</span>
            </div>
            """, unsafe_allow_html=True)

            with st.container(border=True):
                if data.get("found"):
                    st.success(data["summary_answer"])
                    st.markdown(f"**Intent Recognized:** `{data.get('intent_detected', 'UNKNOWN')}`")
                    st.divider()

                    st.markdown("""
                    <div style="display:flex;align-items:center;gap:10px;margin:8px 0 16px 0;">
                      <div style="width:4px;height:22px;background:#2563eb;border-radius:4px;"></div>
                      <span style="font-size:18px;font-weight:750;color:#0f172a;">Supporting Evidence & Provenance</span>
                    </div>
                    """, unsafe_allow_html=True)

                    for s in data.get("sources", []):
                        st.markdown(
                            f"- **[{s['type']}]** "
                            f"[{s['identifier']}]({s['url']}): "
                            f"{s['summary']}"
                        )
                else:
                    st.error(data.get("summary_answer", "No relevant records found."))

        else:
            st.error(f"Failed to execute search. Server returned status code: {resp.status_code}")

    except httpx.RequestError as e:
        st.error(f"Failed to connect to backend: {e}")
    except (KeyError, ValueError) as e:
        st.error(f"Unexpected response from backend: {e}")

elif search_btn and not query:
    st.warning("Please enter a search query before continuing.")


# FOOTER

st.divider()

st.markdown("""
<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;padding:4px 0;">
  <span style="font-size:11px;color:#94a3b8;font-weight:600;letter-spacing:0.4px;">
    PROJECT BRAIN &middot; DELIVERY MEMORY
  </span>
  <span style="font-size:11px;color:#94a3b8;font-weight:500;">
    Deterministic Search Engine
  </span>
</div>
""", unsafe_allow_html=True)