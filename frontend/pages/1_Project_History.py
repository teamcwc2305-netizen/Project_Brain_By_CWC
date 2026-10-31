import os
import sys
import httpx
import pandas as pd
import streamlit as st

BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Project History & Delivery Audit | Project Brain",
    page_icon="📜",
    layout="wide"
)

# Path setup
pages_dir = os.path.dirname(os.path.abspath(__file__))
frontend_dir = os.path.abspath(os.path.join(pages_dir, ".."))
project_root = os.path.abspath(os.path.join(frontend_dir, ".."))
for p in [pages_dir, frontend_dir, project_root]:
    if p not in sys.path:
        sys.path.insert(0, p)

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

# NOW fetch repositories and data
repos = fetch_repositories()
current_repo = get_active_repo(repos)
repo_id = current_repo["id"] if current_repo else None

try:
    from sidebar_nav import render_sidebar
    render_sidebar(repos=repos, key="history_repo_select")
except Exception:
    pass

repo_name = f"{current_repo['owner']}/{current_repo['name']}" if current_repo else "No repository selected"

if not repo_id:
    st.warning("⚠️ Please select or import a repository on the main dashboard first!")
    st.stop()


# PAGE STYLES MATCHING TARGET THEME

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
    max-width: 1200px !important;
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

/* 4 METRIC TILES */
.metric-deck {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 22px;
}

.metric-card-box {
    background: #ffffff;
    border: 1.5px solid #e2e8f0;
    border-radius: 14px;
    padding: 18px 22px;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.03);
    transition: all 0.22s ease;
}

.metric-card-box:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 18px rgba(15, 23, 42, 0.06);
    border-color: #cbd5e1;
}

.metric-header-tag {
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    color: #64748b;
    margin-bottom: 8px;
    font-family: 'JetBrains Mono', monospace;
}

.metric-big-num {
    font-size: 30px;
    font-weight: 800;
    color: #0f172a;
    line-height: 1.1;
    margin-bottom: 8px;
    font-family: 'Inter', sans-serif;
}

.metric-big-num.green {
    color: #059669;
}

.metric-sub-pill {
    font-size: 11.5px;
    font-weight: 600;
    color: #2563eb;
    display: inline-flex;
    align-items: center;
    gap: 5px;
}

.metric-sub-pill.green {
    color: #059669;
}

.metric-sub-pill.amber {
    color: #d97706;
}

div[data-baseweb="input"] > div {
    background: #ffffff !important;
    border: 1.5px solid #cbd5e1 !important;
    border-radius: 10px !important;
    min-height: 44px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02) !important;
}

div[data-baseweb="input"] > div:focus-within {
    border-color: #2563eb !important;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15) !important;
}

div[data-baseweb="input"] input {
    color: #0f172a !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 13.5px !important;
}

div[data-baseweb="select"] > div {
    background: #ffffff !important;
    border: 1.5px solid #cbd5e1 !important;
    border-radius: 10px !important;
    min-height: 44px !important;
}

.record-card {
    background: #ffffff;
    border: 1.5px solid #e2e8f0;
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 12px;
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 16px;
    box-shadow: 0 2px 6px rgba(15, 23, 42, 0.02);
    transition: all 0.2s ease;
}

.record-card:hover {
    transform: translateY(-2px);
    border-color: #cbd5e1;
    box-shadow: 0 6px 16px rgba(15, 23, 42, 0.06);
}

.rc-left {
    flex-grow: 1;
}

.rc-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 6px;
    flex-wrap: wrap;
}

.rc-sha-badge {
    background: #eff6ff;
    color: #2563eb !important;
    border: 1px solid #bfdbfe;
    padding: 3px 8px;
    border-radius: 6px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    font-weight: 700;
    text-decoration: none !important;
    display: inline-flex;
    align-items: center;
    gap: 4px;
}

.rc-sha-badge:hover {
    background: #dbeafe;
    color: #1d4ed8 !important;
}

.rc-title {
    font-weight: 700;
    font-size: 14.5px;
    color: #0f172a;
    line-height: 1.35;
}

.rc-meta {
    font-size: 12.5px;
    color: #64748b;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
}

.rc-files {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
}

.rc-file-badge {
    background: #f1f5f9;
    border: 1px solid #e2e8f0;
    color: #475569;
    padding: 2px 8px;
    border-radius: 6px;
    font-size: 11px;
    font-family: 'JetBrains Mono', monospace;
}

.rc-right {
    flex-shrink: 0;
}

.rc-pill {
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

.rc-pill.commit {
    background: #ecfdf5;
    color: #059669;
    border: 1px solid #a7f3d0;
}

.rc-pill.issue {
    background: #fff1f2;
    color: #e11d48;
    border: 1px solid #fecdd3;
}

.rc-pill.issue-closed {
    background: #f1f5f9;
    color: #64748b;
    border: 1px solid #e2e8f0;
}

.rc-pill.pr {
    background: #f5f3ff;
    color: #7c3aed;
    border: 1px solid #ddd6fe;
}

button[data-baseweb="tab"] {
    font-size: 13.5px !important;
    font-weight: 700 !important;
    color: #64748b !important;
    padding: 10px 18px !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #0f172a !important;
    border-bottom-color: #0f172a !important;
}

.results-count-label {
    font-size: 13px;
    color: #64748b;
    margin: 14px 0 16px 0;
    font-weight: 500;
}
</style>
""", unsafe_allow_html=True)


# TOP HEADER BAR

st.markdown(f"""
<div class="top-header">
  <div class="header-left">
    <div class="header-badge">
      <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="10"></circle>
        <polyline points="12 6 12 12 16 14"></polyline>
      </svg>
    </div>
    <div>
      <h2 class="header-title">Project History & Delivery Audit</h2>
      <div class="header-subtitle">
        Active Repository: <b>{repo_name}</b> &middot; Evidence-backed provenance
      </div>
    </div>
  </div>
  <div>
    <span class="header-pill">
      <span class="pill-dot"></span> Deterministic Audit
    </span>
  </div>
</div>
""", unsafe_allow_html=True)


# DATA FETCHING

stats = {}
try:
    s_resp = httpx.get(f"{BACKEND_URL}/api/repositories/{repo_id}/stats", timeout=5.0)
    if s_resp.status_code == 200:
        stats = s_resp.json()
except Exception:
    pass

commits = []
issues = []
prs = []
risks = []

try:
    c_resp = httpx.get(f"{BACKEND_URL}/api/repositories/{repo_id}/history/commits?limit=100", timeout=10.0)
    if c_resp.status_code == 200:
        commits = c_resp.json()
except Exception:
    pass

try:
    i_resp = httpx.get(f"{BACKEND_URL}/api/repositories/{repo_id}/history/issues", timeout=10.0)
    if i_resp.status_code == 200:
        issues = i_resp.json()
except Exception:
    pass

try:
    p_resp = httpx.get(f"{BACKEND_URL}/api/repositories/{repo_id}/history/pull-requests", timeout=10.0)
    if p_resp.status_code == 200:
        prs = p_resp.json()
except Exception:
    pass

try:
    k_resp = httpx.get(f"{BACKEND_URL}/api/repositories/{repo_id}/history/knowledge-risk", timeout=10.0)
    if k_resp.status_code == 200:
        risks = k_resp.json()
except Exception:
    pass

total_commits_val = stats.get("total_commits") or len(commits)
commits_analyzed = stats.get("commits_count") or len(commits)

open_issues_count = stats.get("open_issues_count")
if open_issues_count is None:
    open_issues_count = len([i for i in issues if i.get("state") == "open"])

open_prs_count = stats.get("open_prs_count")
if open_prs_count is None:
    open_prs_count = len([p for p in prs if p.get("state") == "open"])

total_issues_count = stats.get("issues_count") or len(issues)
total_prs_count = stats.get("pull_requests_count") or len(prs)

authors_set = set(c.get("author") for c in commits if c.get("author"))
distinct_authors_count = len(authors_set)

high_risks = [r for r in risks if "HIGH" in r.get("risk_level", "")]
low_risks = [r for r in risks if "LOW" in r.get("risk_level", "")]
risk_files_count = len(high_risks)


# FOUR METRIC DECK TILES 

st.markdown(f"""
<div class="metric-deck">
  <div class="metric-card-box">
    <div class="metric-header-tag">RECORDED COMMITS</div>
    <div class="metric-big-num">{total_commits_val}</div>
    <div class="metric-sub-pill green">✔ {commits_analyzed} analyzed in graph</div>
  </div>

  <div class="metric-card-box">
    <div class="metric-header-tag">ACTIVE CONTRIBUTORS</div>
    <div class="metric-big-num">{distinct_authors_count}</div>
    <div class="metric-sub-pill">👤 Distinct authors</div>
  </div>

  <div class="metric-card-box">
    <div class="metric-header-tag">ISSUES / PULL REQUESTS (OPEN)</div>
    <div class="metric-big-num">{open_issues_count} / {open_prs_count}</div>
    <div class="metric-sub-pill">🔗 {total_issues_count} issues &middot; {total_prs_count} PRs recorded</div>
  </div>

  <div class="metric-card-box">
    <div class="metric-header-tag">KNOWLEDGE RISK</div>
    <div class="metric-big-num green">{risk_files_count} files</div>
    <div class="metric-sub-pill amber">⚠️ Single author bottlenecks</div>
  </div>
</div>
""", unsafe_allow_html=True)


# FILTER BAR

col_search, col_author = st.columns([3.5, 1], gap="medium")

with col_search:
    search_query = st.text_input(
        "Filter records",
        placeholder="Filter by message, author name, commit SHA, or path...",
        label_visibility="collapsed",
        key="history_filter_input"
    )

with col_author:
    author_options = ["All Authors"] + sorted(list(authors_set))
    selected_author = st.selectbox(
        "Filter by Author",
        author_options,
        label_visibility="collapsed",
        key="history_author_filter_select"
    )


# Filter helper logic
def matches_filter(text_candidates: list, author: str = None) -> bool:
    if selected_author != "All Authors" and author and author != selected_author:
        return False
    if not search_query:
        return True
    q = search_query.strip().lower()
    return any(q in str(t).lower() for t in text_candidates if t)


filtered_commits = [
    c for c in commits
    if matches_filter([c.get("message"), c.get("sha"), c.get("author")] + c.get("changed_files", []), c.get("author"))
]

filtered_issues = [
    iss for iss in issues
    if matches_filter([iss.get("title"), iss.get("description"), str(iss.get("issue_number")), iss.get("state")])
]

filtered_prs = [
    pr for pr in prs
    if matches_filter([pr.get("title"), pr.get("description"), str(pr.get("pr_number")), pr.get("state")])
]


# TABS SECTION WITH DETAILED AUDIT CARDS

tab_commits, tab_issues, tab_prs, tab_risk = st.tabs([
    f"Commits ({total_commits_val})",
    f"Issues ({open_issues_count} Open / {len(filtered_issues)})",
    f"Pull Requests ({open_prs_count} Open / {len(filtered_prs)})",
    f"Knowledge Risk ({len(risks)})"
])

# --- COMMITS ---
with tab_commits:
    st.markdown(f"<div class='results-count-label'>Showing <b>{len(filtered_commits)}</b> analyzed commit(s) from repository history (<b>{total_commits_val}</b> total commits on GitHub):</div>", unsafe_allow_html=True)

    if not filtered_commits:
        st.info("No commits match your filter criteria.")
    else:
        for c in filtered_commits:
            sha_short = c.get("sha", "")[:7]
            sha_full = c.get("sha", "")
            raw_msg = c.get("message", "Untitled commit")
            first_line = raw_msg.split("\n")[0]
            if len(first_line) > 100:
                first_line = first_line[:97] + "..."
            
            author = c.get("author") or "Unknown"
            raw_ts = c.get("timestamp") or ""
            date_str = raw_ts.split("T")[0] if "T" in raw_ts else (raw_ts[:10] if raw_ts else "Unknown date")
            source_url = c.get("source_url") or f"https://github.com/{repo_name}/commit/{sha_full}"
            changed_files = c.get("changed_files", [])

            files_html = "".join([f"<span class='rc-file-badge'>📄 {f}</span>" for f in changed_files[:8]])
            if len(changed_files) > 8:
                files_html += f"<span class='rc-file-badge'>+{len(changed_files)-8} more</span>"
            if not files_html:
                files_html = "<span style='font-size:11px;color:#94a3b8;'>No modified file details recorded</span>"

            st.markdown(f"""
<div class="record-card">
  <div class="rc-left">
    <div class="rc-header">
      <a href="{source_url}" target="_blank" class="rc-sha-badge" title="View commit on GitHub">
        {sha_short} ↗
      </a>
      <span class="rc-title">{first_line}</span>
    </div>
    <div class="rc-meta">
      Authored by <b style="color:#0f172a;">{author}</b> &middot; 📅 {date_str} &middot; {len(changed_files)} file(s) modified
    </div>
    <div class="rc-files">
      {files_html}
    </div>
  </div>
  <div class="rc-right">
    <span class="rc-pill commit">COMMIT</span>
  </div>
</div>
""", unsafe_allow_html=True)


# --- ISSUES ---
with tab_issues:
    col_iss_header, col_iss_filter = st.columns([2.5, 1])
    with col_iss_header:
        st.markdown(f"<div class='results-count-label'>Showing <b>{open_issues_count}</b> open issue(s) &middot; <b>{len(filtered_issues)}</b> total recorded issue(s):</div>", unsafe_allow_html=True)
    with col_iss_filter:
        iss_view = st.radio("State Filter", ["All", "Open Only", "Closed Only"], horizontal=True, label_visibility="collapsed", key="issue_state_filter_radio")

    display_issues = filtered_issues
    if iss_view == "Open Only":
        display_issues = [i for i in filtered_issues if (i.get("state") or "").lower() == "open"]
    elif iss_view == "Closed Only":
        display_issues = [i for i in filtered_issues if (i.get("state") or "").lower() == "closed"]

    if not display_issues:
        st.info("No issues match your filter criteria.")
    else:
        for iss in display_issues:
            num = iss.get("issue_number")
            title = iss.get("title") or "Untitled issue"
            state = (iss.get("state") or "open").lower()
            source_url = iss.get("source_url") or f"https://github.com/{repo_name}/issues/{num}"
            desc = iss.get("description") or ""
            desc_snip = (desc[:140] + "...") if len(desc) > 140 else desc
            pill_class = "issue" if state == "open" else "issue-closed"

            st.markdown(f"""
<div class="record-card">
  <div class="rc-left">
    <div class="rc-header">
      <a href="{source_url}" target="_blank" class="rc-sha-badge">
        #{num} ↗
      </a>
      <span class="rc-title">{title}</span>
    </div>
    <div class="rc-meta">
      Status: <b style="text-transform:uppercase;color:{'#e11d48' if state=='open' else '#64748b'};">{state}</b>
      {f"&middot; {desc_snip}" if desc_snip else ""}
    </div>
  </div>
  <div class="rc-right">
    <span class="rc-pill {pill_class}">{state.upper()}</span>
  </div>
</div>
""", unsafe_allow_html=True)


# --- PULL REQUESTS ---
with tab_prs:
    col_pr_header, col_pr_filter = st.columns([2.5, 1])
    with col_pr_header:
        st.markdown(f"<div class='results-count-label'>Showing <b>{open_prs_count}</b> open PR(s) &middot; <b>{len(filtered_prs)}</b> total recorded PR(s):</div>", unsafe_allow_html=True)
    with col_pr_filter:
        pr_view = st.radio("State Filter", ["All", "Open Only", "Closed/Merged Only"], horizontal=True, label_visibility="collapsed", key="pr_state_filter_radio")

    display_prs = filtered_prs
    if pr_view == "Open Only":
        display_prs = [p for p in filtered_prs if (p.get("state") or "").lower() == "open"]
    elif pr_view == "Closed/Merged Only":
        display_prs = [p for p in filtered_prs if (p.get("state") or "").lower() != "open"]

    if not display_prs:
        st.info("No pull requests match your filter criteria.")
    else:
        for pr in display_prs:
            num = pr.get("pr_number")
            title = pr.get("title") or "Untitled PR"
            state = (pr.get("state") or "open").lower()
            source_url = pr.get("source_url") or f"https://github.com/{repo_name}/pull/{num}"
            desc = pr.get("description") or ""
            desc_snip = (desc[:140] + "...") if len(desc) > 140 else desc

            st.markdown(f"""
<div class="record-card">
  <div class="rc-left">
    <div class="rc-header">
      <a href="{source_url}" target="_blank" class="rc-sha-badge">
        PR #{num} ↗
      </a>
      <span class="rc-title">{title}</span>
    </div>
    <div class="rc-meta">
      Status: <b style="text-transform:uppercase;color:#7c3aed;">{state}</b>
      {f"&middot; {desc_snip}" if desc_snip else ""}
    </div>
  </div>
  <div class="rc-right">
    <span class="rc-pill pr">{state.upper()}</span>
  </div>
</div>
""", unsafe_allow_html=True)


# --- KNOWLEDGE RISK ---
with tab_risk:
    st.markdown(f"<div class='results-count-label'>Knowledge Concentration & Bus Factor Analysis for <b>{repo_name}</b>:</div>", unsafe_allow_html=True)

    if not risks:
        st.info("No file risk analysis records available yet.")
    else:
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Total Files Analyzed", len(risks))
        with m2:
            st.metric("🚨 High Risk (Single Author)", len(high_risks), delta=f"{len(high_risks)} files at risk", delta_color="inverse")
        with m3:
            st.metric("✅ Distributed (Multiple Authors)", len(low_risks))

        if len(risks) > 0:
            pct_high = len(high_risks) / len(risks)
            st.write(f"**Knowledge Concentration Ratio:** `{pct_high*100:.1f}%` of codebase depends on sole contributors.")
            st.progress(pct_high)

        view_filter = st.radio("Display files:", ["All Files", "Only High Risk (Sole Contributor)", "Distributed"], horizontal=True)

        display_list = risks
        if view_filter == "Only High Risk (Sole Contributor)":
            display_list = high_risks
        elif view_filter == "Distributed":
            display_list = low_risks

        df = pd.DataFrame(display_list)
        if not df.empty:
            df = df.rename(columns={
                "file_path": "File Path",
                "commit_count": "Total Commits",
                "unique_authors_count": "Distinct Authors",
                "sole_contributor": "Sole Contributor",
                "risk_level": "Risk Level"
            })
            st.dataframe(df, use_container_width=True)
        else:
            st.success("No files match the selected filter criteria.")