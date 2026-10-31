# frontend/pages/3_Impact_Analysis.py
import os
import sys
import httpx
import streamlit as st

BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Impact Analysis | Project Brain",
    page_icon="💥",
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

try:
    from sidebar_nav import render_sidebar
    render_sidebar(repos=repos, key="impact_repo_select")
except Exception:
    pass

repo_name = f"{current_repo['owner']}/{current_repo['name']}" if current_repo else "No repository selected"

if not repo_id:
    st.warning("⚠️ Please select or import a repository on the main dashboard first!")
    st.stop()


# PAGE STYLING

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
    max-width: 1220px !important;
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

/* LEFT SECTION CARD */
.impact-card {
    background: #ffffff;
    border: 1.5px solid #cbd5e1;
    border-radius: 14px;
    padding: 20px 24px;
    margin-bottom: 20px;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.02);
}

.card-title {
    font-size: 16px;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 4px;
}

.card-desc {
    font-size: 13px;
    color: #64748b;
}

.input-method-label {
    font-size: 13.5px;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 8px;
}

/* TARGET FILE INFO BOX */
.target-file-box {
    background: #f0f7ff;
    border: 1.5px solid #bfdbfe;
    border-radius: 10px;
    padding: 12px 18px;
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 13px;
    color: #1e3a8a;
    font-weight: 600;
    margin: 12px 0 18px 0;
}

.file-tag {
    background: #10b981;
    color: #ffffff;
    padding: 3px 8px;
    border-radius: 5px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    font-weight: 700;
}

.scope-card {
    background: #ffffff;
    border: 1.5px solid #e2e8f0;
    border-radius: 14px;
    padding: 24px 26px;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.03);
}

.scope-title {
    font-size: 16px;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 4px;
}

.scope-desc {
    font-size: 12.5px;
    color: #64748b;
    margin-bottom: 20px;
}

.scope-list {
    display: flex;
    flex-direction: column;
    gap: 14px;
    margin-bottom: 24px;
}

.scope-item {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    font-size: 12.5px;
    color: #334155;
    line-height: 1.45;
}

.scope-icon {
    font-weight: 800;
    font-size: 13px;
    line-height: 1.3;
}

.scope-icon.check {
    color: #10b981;
}

.scope-icon.warn {
    color: #f59e0b;
}

.scope-footer {
    font-size: 11px;
    color: #94a3b8;
    border-top: 1px solid #f1f5f9;
    padding-top: 14px;
}

div[data-testid="stButton"] > button {
    background-color: #2563eb !important;
    color: #ffffff !important;
    border: 1.5px solid #2563eb !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    padding: 12px 24px !important;
    transition: all 0.22s ease !important;
    box-shadow: 0 4px 14px rgba(37, 99, 235, 0.35) !important;
    width: 100% !important;
}

div[data-testid="stButton"] > button:hover {
    background-color: #1d4ed8 !important;
    border-color: #1d4ed8 !important;
    color: #ffffff !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px -4px rgba(37, 99, 235, 0.55) !important;
}

div[data-testid="stButton"] > button:active {
    background-color: #1e40af !important;
    transform: translateY(0px) !important;
}

/* WIDGET CUSTOMIZATION */
div[data-baseweb="select"] > div {
    background: #ffffff !important;
    border: 1.5px solid #cbd5e1 !important;
    border-radius: 10px !important;
    min-height: 44px !important;
}

div[data-baseweb="select"]:focus-within > div {
    border-color: #2563eb !important;
    box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.20) !important;
}

div[data-baseweb="textarea"] > div {
    background: #ffffff !important;
    border: 1.5px solid #cbd5e1 !important;
    border-radius: 10px !important;
}

/* RADIO BUTTONS */
div[data-testid="stRadio"] > div {
    display: flex;
    gap: 24px;
    align-items: center;
    margin-bottom: 12px;
}

div[data-testid="stRadio"] label {
    font-size: 13.5px !important;
    font-weight: 600 !important;
    color: #1e293b !important;
}

/* RESULTS SECTION */
.result-box {
    background: #ffffff;
    border: 1.5px solid #e2e8f0;
    border-radius: 14px;
    padding: 22px 24px;
    margin-top: 24px;
    box-shadow: 0 2px 10px rgba(15, 23, 42, 0.03);
}
</style>
""", unsafe_allow_html=True)


# TOP HEADER BAR

st.markdown(f"""
<div class="top-header">
  <div class="header-left">
    <div class="header-badge">
      <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round">
        <path d="M3 3v18h18"></path>
        <path d="m19 9-5 5-4-4-3 3"></path>
      </svg>
    </div>
    <div>
      <h2 class="header-title">Rule-Based Code Change Impact Analysis</h2>
      <div class="header-subtitle">
        Active Repository: <b>{repo_name}</b> &middot; Deterministic Blast Radius Engine
      </div>
    </div>
  </div>
  <div>
    <span class="header-pill">
      <span class="pill-dot"></span> Deterministic Impact
    </span>
  </div>
</div>
""", unsafe_allow_html=True)


# FETCH FILES FROM REPOSITORY

repo_files = []
try:
    resp = httpx.get(f"{BACKEND_URL}/api/repositories/{repo_id}/history/commits?limit=100", timeout=10.0)
    if resp.status_code == 200:
        raw_commits = resp.json()
        seen = set()
        for c in raw_commits:
            for f in c.get("changed_files", []):
                if f not in seen:
                    seen.add(f)
                    repo_files.append(f)
except Exception:
    pass

if not repo_files:
    repo_files = ["README.md"]


# MAIN CONTENT

col_main, col_scope = st.columns([1.8, 1], gap="large")

with col_main:
    st.markdown("""
<div class="impact-card">
  <div class="card-title">1. Select or Paste Changes</div>
  <div class="card-desc">Inspect the blast radius of single files, diffs, or unified diffs.</div>
</div>
""", unsafe_allow_html=True)

    st.markdown('<div class="input-method-label">Input method:</div>', unsafe_allow_html=True)

    input_type = st.radio(
        "Input method:",
        ["Direct File Selection", "Git Diff", "File Paths List"],
        horizontal=True,
        label_visibility="collapsed",
        key="impact_input_type_radio"
    )

    diff_content = ""
    file_list = []
    selected_file = repo_files[0] if repo_files else "README.md"

    if input_type == "Direct File Selection":
        selected_file = st.selectbox(
            "Select a file recorded in this repository:",
            repo_files,
            label_visibility="collapsed",
            key="impact_file_selector"
        )
        file_list = [selected_file] if selected_file else []

        st.markdown(f"""
<div class="target-file-box">
  <span>Target file for blast radius analysis:</span>
  <span class="file-tag">{selected_file}</span>
</div>
""", unsafe_allow_html=True)

    elif input_type == "Git Diff":
        sample_diff = f"--- a/{selected_file}\n+++ b/{selected_file}\n@@ -1,3 +1,4 @@\n+# Delivery Memory Update"
        diff_content = st.text_area(
            "Paste Unified Git Diff:",
            value=sample_diff,
            height=160,
            key="impact_diff_textarea"
        )

    else:
        raw_files = st.text_area(
            "Enter file paths (one per line):",
            value=selected_file,
            height=130,
            key="impact_paths_textarea"
        )
        file_list = [f.strip() for f in raw_files.splitlines() if f.strip()]

    run_btn = st.button(
        "Run Blast Radius Analysis",
        type="primary",
        use_container_width=True,
        key="btn_run_blast_analysis"
    )

with col_scope:
    st.markdown("""
<div class="scope-card">
  <div class="scope-title">Analysis Scope</div>
  <div class="scope-desc">Deterministic blast radius methodology</div>

  <div class="scope-list">
    <div class="scope-item">
      <span class="scope-icon check">✔</span>
      <span>Modified paths extracted from payload</span>
    </div>
    <div class="scope-item">
      <span class="scope-icon check">✔</span>
      <span>Recorded file history &amp; co-change relationships</span>
    </div>
    <div class="scope-item">
      <span class="scope-icon check">✔</span>
      <span>Key historical author reviewers recommended</span>
    </div>
    <div class="scope-item">
      <span class="scope-icon check">✔</span>
      <span>Test suite targets inferred from naming patterns</span>
    </div>
    <div class="scope-item">
      <span class="scope-icon warn">!</span>
      <span style="color:#64748b;font-size:12px;">Historical links are evidence-backed, not proof of runtime execution.</span>
    </div>
  </div>

  <div class="scope-footer">
    LLM-Free &middot; Deterministic commit co-occurrence graph
  </div>
</div>
""", unsafe_allow_html=True)


# EXECUTION & RESULTS

if run_btn:
    payload = {"diff_text": diff_content, "changed_files": file_list}
    with st.spinner("Analyzing co-change graph and regression patterns..."):
        try:
            resp = httpx.post(f"{BACKEND_URL}/api/repositories/{repo_id}/impact", json=payload, timeout=30.0)
            if resp.status_code == 200:
                res = resp.json()

                st.markdown(f"""
<div class="result-box">
  <div style="font-weight: 800; font-size: 17px; color: #0f172a; margin-bottom: 6px;">Impact Analysis Summary</div>
  <div style="font-size: 13.5px; color: #334155; line-height: 1.6;">{res.get('summary', 'Analysis completed.')}</div>
</div>
""", unsafe_allow_html=True)

                col1, col2 = st.columns(2, gap="medium")
                with col1:
                    st.markdown("""
                    <div style="display:flex;align-items:center;gap:8px;margin:20px 0 10px 0;">
                      <div style="width:4px;height:20px;background:#2563eb;border-radius:4px;"></div>
                      <span style="font-size:16px;font-weight:800;color:#0f172a;">Directly Modified Files</span>
                    </div>
                    """, unsafe_allow_html=True)
                    for f in res.get("directly_modified_files", []):
                        st.markdown(f"- `{f}`")

                with col2:
                    st.markdown("""
                    <div style="display:flex;align-items:center;gap:8px;margin:20px 0 10px 0;">
                      <div style="width:4px;height:20px;background:#2563eb;border-radius:4px;"></div>
                      <span style="font-size:16px;font-weight:800;color:#0f172a;">Suggested Regression Tests</span>
                    </div>
                    """, unsafe_allow_html=True)
                    suggested = res.get("suggested_tests", [])
                    if suggested:
                        for t in suggested:
                            st.warning(f"🧪 Test Target: `{t}`")
                    else:
                        st.caption("No connected test suites recorded for these files.")

                st.markdown("""
                <div style="display:flex;align-items:center;gap:8px;margin:24px 0 12px 0;">
                  <div style="width:4px;height:20px;background:#2563eb;border-radius:4px;"></div>
                  <span style="font-size:16px;font-weight:800;color:#0f172a;">Detailed Blast Radius &amp; Historical Dependencies</span>
                </div>
                """, unsafe_allow_html=True)

                affected = res.get("affected_components", [])
                if affected:
                    table_data = []
                    for comp in affected:
                        table_data.append({
                            "Component": comp.get("component_name"),
                            "Category": comp.get("impact_category"),
                            "Risk Level": comp.get("impact_level"),
                            "Classification": comp.get("classification"),
                            "Reason": comp.get("reason")
                        })
                    st.table(table_data)
                else:
                    st.info("No transitive or indirect components affected outside the modified paths.")

            else:
                st.error(f"Error analyzing impact. Backend status code: {resp.status_code}")
        except Exception as e:
            st.error(f"Failed to communicate with backend: {e}")