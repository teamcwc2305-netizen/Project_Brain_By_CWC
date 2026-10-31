# frontend/pages/5_About_Us.py
import os
import sys
import streamlit as st

st.set_page_config(
    page_title="About Us | Project Brain",
    page_icon="👥",
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


# Page Styles

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

.stApp {
    background: #f8fafc !important;
    color: #0f172a !important;
    font-family: 'Inter', sans-serif !important;
}

header[data-testid="stHeader"] { 
    background: transparent !important; 
}

#MainMenu, footer { 
    visibility: hidden; 
}

.block-container {
    max-width: 1180px !important;
    padding-top: 1.5rem !important;
    padding-bottom: 3rem !important;
}

/* Hero Section */
.about-hero {
    background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%);
    border: 1.5px solid #cbd5e1;
    border-radius: 20px;
    padding: 36px 30px;
    text-align: center;
    margin-bottom: 32px;
    box-shadow: 0 4px 16px rgba(15, 23, 42, 0.04);
}

.hero-tag {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    background: #eff6ff;
    color: #2563eb;
    border: 1px solid #bfdbfe;
    padding: 5px 14px;
    border-radius: 30px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.5px;
    margin-bottom: 14px;
}

.hero-title {
    color: #0f172a;
    font-size: 32px;
    font-weight: 800;
    letter-spacing: -0.5px;
    margin-bottom: 12px;
}

.hero-description {
    color: #475569;
    font-size: 14.5px;
    line-height: 1.7;
    max-width: 760px;
    margin: 0 auto;
}

/* Section Headings */
.section-title {
    color: #0f172a;
    font-size: 24px;
    font-weight: 800;
    text-align: center;
    margin-top: 30px;
    margin-bottom: 6px;
    letter-spacing: -0.4px;
}

.section-subtitle {
    color: #64748b;
    text-align: center;
    font-size: 13.5px;
    margin-bottom: 24px;
}

/* Team Member Cards */
.team-card {
    background: linear-gradient(135deg, #14532d, #166534, #15803d);
    border: 1px solid #22c55e;
    border-radius: 16px;
    padding: 22px 16px;
    text-align: center;
    min-height: 120px;
    transition: all 0.28s cubic-bezier(0.16, 1, 0.3, 1);
    box-shadow: 0 4px 14px rgba(22, 101, 52, 0.18);
}

.team-card:hover {
    transform: translateY(-6px);
    box-shadow: 0 12px 28px rgba(22, 163, 74, 0.30);
    border-color: #86efac;
}

.member-avatar {
    width: 44px;
    height: 44px;
    margin: 0 auto 10px auto;
    border-radius: 13px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 14px;
    font-weight: 800;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}

.member-name {
    color: #ffffff;
    font-size: 14px;
    font-weight: 700;
    margin-bottom: 4px;
}

.member-team {
    color: #bbf7d0;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.5px;
}

/* Identity Card */
.identity-card {
    background: #ffffff;
    border: 1.5px solid #e2e8f0;
    border-radius: 18px;
    padding: 26px 30px;
    text-align: center;
    margin-top: 32px;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.03);
}

.identity-title {
    color: #0f172a;
    font-size: 20px;
    font-weight: 800;
    margin-bottom: 8px;
}

.identity-description {
    color: #475569;
    font-size: 14px;
    line-height: 1.7;
    max-width: 760px;
    margin: 0 auto;
}

/* Mission Card */
.mission-card {
    background: #ffffff !important;
    border: 1.5px solid #e2e8f0 !important;
    border-radius: 18px !important;
    padding: 30px 32px !important;
    text-align: center !important;
    margin-top: 20px !important;
    box-shadow: 0 4px 16px rgba(15, 23, 42, 0.04) !important;
}

.mission-title {
    color: #0f172a !important;
    font-size: 20px !important;
    font-weight: 800 !important;
    margin-bottom: 10px !important;
}

.mission-description {
    color: #475569 !important;
    font-size: 14px !important;
    line-height: 1.75 !important;
    max-width: 760px !important;
    margin: 0 auto !important;
}
</style>
""", unsafe_allow_html=True)


# Top Header

st.markdown("""
<div style="display:flex;align-items:center;justify-content:space-between;padding:6px 0 18px 0;border-bottom:1px solid #e2e8f0;margin-bottom:24px;">
  <div style="display:flex;align-items:center;gap:12px;">
    <div style="width:42px;height:42px;border-radius:12px;background:#0f172a;display:grid;place-items:center;flex-shrink:0;">
      <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/>
        <circle cx="9" cy="7" r="4"/>
        <path d="M22 21v-2a4 4 0 0 0-3-3.87"/>
        <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
      </svg>
    </div>
    <div>
      <div style="font-weight:800;font-size:18px;letter-spacing:-0.3px;color:#0f172a;">About Us & Engineering Team</div>
      <div style="font-size:12px;color:#64748b;font-weight:500;">
        Team Code with Caos · Builders of Project Brain
      </div>
    </div>
  </div>
  <div style="display:flex;align-items:center;gap:8px;">
    <span style="display:inline-flex;align-items:center;gap:6px;background:#eff6ff;border:1px solid #bfdbfe;padding:5px 14px;border-radius:20px;font-size:12px;color:#1d4ed8;font-weight:600;">
      <span style="width:8px;height:8px;border-radius:50%;background:#2563eb;"></span> Core Contributors
    </span>
  </div>
</div>
""", unsafe_allow_html=True)


# Hero Section

st.markdown("""
<div class="about-hero">
<div class="hero-tag">
<span style="width:7px;height:7px;border-radius:50%;background:#2563eb;display:inline-block;"></span>
MISSION & PHILOSOPHY
</div>
<div class="hero-title">About Project Brain</div>
<div class="hero-description">
Project Brain is designed to eliminate institutional amnesia, preserve developer context, 
and make complex repository histories intuitively accessible. Our goal is to make engineering intelligence deterministic, transparent, and actionable.
</div>
</div>
""", unsafe_allow_html=True)


# Team Section

st.markdown("""
<div class="section-title">Meet the Team</div>
<div class="section-subtitle">The engineers behind Project Brain</div>
""", unsafe_allow_html=True)

members = [
    {"name": "Divyanshu Mehta", "initials": "DM", "color": "#2563eb"},
    {"name": "Vivek Joshi", "initials": "VJ", "color": "#9333ea"},
    {"name": "Neelabh Raj Singh", "initials": "NS", "color": "#0891b2"},
    {"name": "Kamal Pandey", "initials": "KP", "color": "#ea580c"},
    {"name": "Ashish Pandey", "initials": "AP", "color": "#db2777"},
]

for start_idx in range(0, len(members), 3):
    cols = st.columns(3, gap="medium")
    for i, member in enumerate(members[start_idx : start_idx + 3]):
        with cols[i]:
            st.markdown(f"""
<div class="team-card">
<div class="member-avatar" style="background:{member['color']};">{member['initials']}</div>
<div class="member-name">{member['name']}</div>
<div class="member-team">CODE WITH CAOS</div>
</div>
""", unsafe_allow_html=True)

# Team Identity

st.markdown("""
<div class="identity-card">
<div class="identity-title">CODE WITH CAOS</div>
<div class="identity-description">
We are a team of passionate developers who believe in learning, collaboration, creativity, and solving real-world software engineering challenges through high-quality architecture.
</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="mission-card">
<div class="mission-title">Our Mission</div>
<div class="mission-description">
Our mission is to build meaningful technology solutions that simplify complex development workflows, preserve critical institutional knowledge, and improve cross-team collaboration. Through Project Brain, we ensure valuable project context is never lost.
</div>
</div>
""", unsafe_allow_html=True)

