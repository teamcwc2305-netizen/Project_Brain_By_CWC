import streamlit as st
import streamlit.components.v1 as components
import httpx
import time

BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Overview | Project Brain",
    page_icon="🧠",
    layout="wide"
)

# Authentication gate
import os
import sys

frontend_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(frontend_dir, ".."))
for p in [frontend_dir, project_root]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from frontend.auth import require_auth
except ImportError:
    from auth import require_auth

require_auth()

try:
    from sidebar_nav import render_sidebar
    render_sidebar()
except Exception:
    pass

# STYLING

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

  .stApp {
    background-color: #f8fafc !important;
    color: #0f172a !important;
    font-family: 'Inter', sans-serif !important;
  }
  header[data-testid="stHeader"] { background: transparent !important; }
  #MainMenu, footer { visibility: hidden; }

  /* SIDEBAR */

  [data-testid="stSidebarNav"] a,
  [data-testid="stSidebarNavLink"],
  [data-testid="stSidebarNavLinkContainer"] a,
  section[data-testid="stSidebar"] nav ul li a {
    border-radius: 10px !important;
    transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1) !important;
    padding: 8px 14px !important;
    margin: 3px 0 !important;
    color: #475569 !important;
    font-weight: 500 !important;
    text-decoration: none !important;
  }

  [data-testid="stSidebarNav"] a:hover,
  [data-testid="stSidebarNavLink"]:hover,
  [data-testid="stSidebarNavLinkContainer"] a:hover,
  section[data-testid="stSidebar"] nav ul li a:hover {
    background: #eff6ff !important;
    color: #1d4ed8 !important;
    transform: translateX(4px) !important;
    box-shadow: 0 2px 10px rgba(37, 99, 235, 0.12) !important;
    border-left: 3.5px solid #2563eb !important;
  }

  [data-testid="stSidebarNav"] a:hover span,
  [data-testid="stSidebarNavLink"]:hover span,
  [data-testid="stSidebarNavLinkContainer"] a:hover span,
  section[data-testid="stSidebar"] nav ul li a:hover span {
    color: #1d4ed8 !important;
    font-weight: 600 !important;
  }

  [data-testid="stSidebarNavLink"][aria-current="page"],
  [data-testid="stSidebarNav"] a[aria-current="page"],
  section[data-testid="stSidebar"] nav ul li a[aria-current="page"] {
    background: #f1f5f9 !important;
    color: #0f172a !important;
    font-weight: 700 !important;
    border-left: 3.5px solid #0f172a !important;
  }

  [data-testid="stSidebarNavLink"][aria-current="page"]:hover,
  [data-testid="stSidebarNav"] a[aria-current="page"]:hover {
    background: #eff6ff !important;
    color: #1d4ed8 !important;
    border-left: 3.5px solid #2563eb !important;
  }

  [data-testid="stSidebarNavItems"] li:first-child [data-testid="stSidebarNavLink"] span,
  [data-testid="stSidebarNavItems"] li:first-child a span,
  [data-testid="stSidebarNav"] ul li:first-child [data-testid="stSidebarNavLink"] span,
  [data-testid="stSidebarNav"] ul li:first-child a span,
  section[data-testid="stSidebar"] nav ul li:first-child a span,
  [data-testid="stSidebarNav"] a[href="/"] span,
  [data-testid="stSidebarNav"] a[href="./"] span,
  [data-testid="stSidebarNav"] a[href=""] span {
    display: none !important;
    visibility: hidden !important;
    font-size: 0 !important;
    line-height: 0 !important;
    width: 0 !important;
    height: 0 !important;
    overflow: hidden !important;
  }

  [data-testid="stSidebarNavItems"] li:first-child [data-testid="stSidebarNavLink"]::after,
  [data-testid="stSidebarNavItems"] li:first-child a::after,
  [data-testid="stSidebarNav"] ul li:first-child [data-testid="stSidebarNavLink"]::after,
  [data-testid="stSidebarNav"] ul li:first-child a::after,
  section[data-testid="stSidebar"] nav ul li:first-child a::after,
  [data-testid="stSidebarNav"] a[href="/"]::after,
  [data-testid="stSidebarNav"] a[href="./"]::after,
  [data-testid="stSidebarNav"] a[href=""]::after {
    content: "Overview" !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    line-height: 1.5 !important;
    visibility: visible !important;
    display: inline-block !important;
    color: inherit !important;
  }

  [data-testid="stSidebarNavItems"] li:first-child [data-testid="stSidebarNavLink"]:hover::after,
  [data-testid="stSidebarNavItems"] li:first-child a:hover::after,
  [data-testid="stSidebarNav"] ul li:first-child [data-testid="stSidebarNavLink"]:hover::after,
  [data-testid="stSidebarNav"] ul li:first-child a:hover::after,
  section[data-testid="stSidebar"] nav ul li:first-child a:hover::after {
    color: #1d4ed8 !important;
    font-weight: 600 !important;
  }

  .metrics-deck {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin: 20px 0 24px 0;
  }
  .metric-card-box {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 20px 22px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
    transition: all 0.28s cubic-bezier(0.16, 1, 0.3, 1);
    cursor: default;
    position: relative;
    overflow: hidden;
  }
  .metric-card-box:hover {
    transform: translateY(-4px);
    border-color: #cbd5e1;
    box-shadow: 0 14px 28px -6px rgba(15, 23, 42, 0.08), 0 0 16px rgba(37, 99, 235, 0.16);
  }
  .metric-title {
    font-size: 13px;
    color: #475569;
    font-weight: 500;
    margin-bottom: 6px;
  }
  .metric-value {
    font-size: 38px;
    font-weight: 700;
    color: #0f172a;
    line-height: 1.1;
    letter-spacing: -0.5px;
    margin-bottom: 10px;
    font-family: 'Inter', sans-serif;
  }
  .metric-pill {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 11px;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 20px;
    background: #ecfdf5;
    color: #059669;
  }

  div[data-testid="stButton"] > button,
  div.stButton > button[kind="primary"],
  div.stButton > button {
    background-color: #0f172a !important; /* Jet Black */
    color: #ffffff !important;
    border: 1.5px solid #0f172a !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 10px 20px !important;
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
    box-shadow: 0 2px 6px rgba(15, 23, 42, 0.15) !important;
  }

  div[data-testid="stButton"] > button:hover,
  div.stButton > button[kind="primary"]:hover,
  div.stButton > button:hover {
    background-color: #2563eb !important; /* Blue on hover */
    border-color: #2563eb !important;
    color: #ffffff !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 22px -4px rgba(37, 99, 235, 0.50) !important;
  }

  div[data-testid="stButton"] > button:active,
  div.stButton > button[kind="primary"]:active {
    background-color: #1d4ed8 !important;
    border-color: #1d4ed8 !important;
    transform: translateY(0px) !important;
  }

  div.st-key-btn_remove_repo > button {
    background-color: #ffffff !important;
    color: #ef4444 !important;
    border: 1.5px solid #fecaca !important;
    box-shadow: 0 1px 3px rgba(239, 68, 68, 0.08) !important;
  }
  div.st-key-btn_remove_repo > button:hover {
    background-color: #ef4444 !important;
    color: #ffffff !important;
    border-color: #ef4444 !important;
    box-shadow: 0 6px 18px rgba(239, 68, 68, 0.35) !important;
    transform: translateY(-2px) !important;
  }

  div.st-key-btn_confirm_remove_yes > button {
    background-color: #dc2626 !important;
    color: #ffffff !important;
    border: 1.5px solid #dc2626 !important;
  }
  div.st-key-btn_confirm_remove_yes > button:hover {
    background-color: #b91c1c !important;
    border-color: #b91c1c !important;
    box-shadow: 0 6px 18px rgba(185, 28, 28, 0.40) !important;
  }

  div.st-key-btn_cancel_remove > button {
    background-color: #f1f5f9 !important;
    color: #475569 !important;
    border: 1.5px solid #cbd5e1 !important;
  }
  div.st-key-btn_cancel_remove > button:hover {
    background-color: #e2e8f0 !important;
    color: #0f172a !important;
    border-color: #94a3b8 !important;
  }

  [data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff !important;
    border: 1.5px solid #e2e8f0 !important;
    border-radius: 14px !important;
    padding: 20px 22px !important;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.02) !important;
  }

  div[data-baseweb="select"] > div {
    border-color: #cbd5e1 !important;
    border-radius: 10px !important;
    background-color: #ffffff !important;
  }
  div[data-baseweb="select"]:focus-within > div {
    border-color: #2563eb !important;
    box-shadow: 0 0 0 1px #2563eb !important;
  }
</style>
""", unsafe_allow_html=True)


# TOP HEADER & NAVIGATION BAR

st.markdown("""
<div style="display: flex; align-items: center; justify-content: space-between; padding: 8px 0 20px 0; border-bottom: 1px solid #e2e8f0; margin-bottom: 20px;">
  <div style="display: flex; align-items: center; gap: 12px;">
    <div style="width: 42px; height: 42px; border-radius: 12px; background: #0f172a; color: #ffffff; display: grid; place-items: center; font-weight: 800; font-size: 16px;">PB</div>
    <div>
      <div style="font-weight: 800; font-size: 16px; letter-spacing: -0.3px;">PROJECT BRAIN</div>
      <div style="font-size: 11px; color: #64748b; font-weight: 600; letter-spacing: 0.5px;">DELIVERY MEMORY & CODE IMPACT</div>
    </div>
  </div>
  <div style="display: flex; align-items: center; gap: 12px;">
    <span style="display: inline-flex; align-items: center; gap: 6px; background: #ecfdf5; border: 1px solid #a7f3d0; padding: 5px 14px; border-radius: 20px; font-size: 12px; color: #047857; font-weight: 600;">
      <span style="width: 8px; height: 8px; border-radius: 50%; background: #10b981;"></span> Local MVP Active
    </span>
  </div>
</div>
""", unsafe_allow_html=True)

# HERO SHOWCASE CARD

HERO_SCI_FI_BRAIN_HTML = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
  <style>
    * { box-sizing: border-box; }
    body { margin: 0; padding: 0; overflow: hidden; font-family: 'Inter', sans-serif; background: transparent; }
    .hero-panel {
      position: relative;
      width: 100%;
      height: 330px;
      background: linear-gradient(135deg, #ffffff 0%, #f8fafc 55%, #f1f5f9 100%);
      border: 1.5px solid #cbd5e1;
      border-radius: 20px;
      overflow: hidden;
      box-shadow: 0 4px 24px -2px rgba(0, 0, 0, 0.04);
      display: flex;
      align-items: center;
    }
    #brain-canvas-container {
      position: absolute;
      inset: 0;
      width: 100%;
      height: 100%;
      z-index: 1;
      pointer-events: none;
    }
    .glow-orb {
      position: absolute;
      right: 18%;
      top: 50%;
      transform: translateY(-50%);
      width: 280px;
      height: 280px;
      border-radius: 50%;
      background: radial-gradient(circle, rgba(15, 23, 42, 0.10) 0%, rgba(0, 0, 0, 0.03) 50%, transparent 75%);
      filter: blur(40px);
      pointer-events: none;
    }
    .hero-text-box {
      position: relative;
      z-index: 10;
      padding: 36px 42px;
      max-width: 440px;
    }
    .hero-pill {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: #f1f5f9;
      border: 1px solid #e2e8f0;
      padding: 5px 12px;
      border-radius: 20px;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: #475569;
      margin-bottom: 14px;
    }
    .pill-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #0284c7;
      box-shadow: 0 0 6px #0284c7;
    }
    .hero-title {
      font-size: 28px;
      font-weight: 800;
      color: #0f172a;
      line-height: 1.22;
      margin: 0;
      letter-spacing: -0.5px;
    }
    .highlight-blue {
      color: #2563eb;
    }
    .hero-desc {
      font-size: 14px;
      color: #64748b;
      line-height: 1.5;
      margin-top: 12px;
    }
  </style>
</head>
<body>
  <div class="hero-panel">
    <div class="glow-orb"></div>
    <div id="brain-canvas-container"></div>
    <div class="hero-text-box">
      <div class="hero-pill">
        <span class="pill-dot"></span>
        PROJECT BRAIN · NEURAL MEMORY
      </div>
      <h1 class="hero-title">
        Institutional memory.<br>
        <span class="highlight-black">Connected to your code.</span>
      </h1>
      <p class="hero-desc">
        Trace developer decisions, blast radius impact, and file ownership backed strictly by git history.
      </p>
    </div>
  </div>

  <script>
    (function() {
      const container = document.getElementById('brain-canvas-container');
      const scene = new THREE.Scene();
      const camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 1, 1000);
      camera.position.set(0, 0, 150);

      const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
      renderer.setSize(container.clientWidth, container.clientHeight);
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      container.appendChild(renderer.domElement);

      const brainGroup = new THREE.Group();
      brainGroup.position.x = 42;
      scene.add(brainGroup);

      const points = [];
      for (let side of [-1, 1]) {
        for (let i = 0; i < 360; i++) {
          const u = Math.random() * Math.PI;
          const v = (Math.random() - 0.5) * Math.PI;
          const fold = 1 + 0.12 * Math.sin(u * 6) * Math.cos(v * 6) + 0.08 * Math.sin(u * 12);
          const r = 36 * fold;
          let x = r * Math.sin(u) * Math.cos(v) * 0.78 + (side * 12);
          let y = r * Math.cos(u) * 0.90;
          let z = r * Math.sin(u) * Math.sin(v) * 1.15;
          if (y < 0 && z < -8) { y *= 0.82; z *= 0.88; }
          points.push(new THREE.Vector3(x, y, z));
        }
      }

      const linePositions = [];
      for (let i = 0; i < points.length; i++) {
        for (let j = i + 1; j < points.length; j++) {
          if (points[i].distanceTo(points[j]) < 13.5) {
            linePositions.push(points[i].x, points[i].y, points[i].z, points[j].x, points[j].y, points[j].z);
          }
        }
      }
      const lineGeo = new THREE.BufferGeometry();
      lineGeo.setAttribute('position', new THREE.Float32BufferAttribute(linePositions, 3));
      const lineMat = new THREE.LineBasicMaterial({
        color: 0x020617, // Jet Black
        transparent: true,
        opacity: 0.55,
        blending: THREE.NormalBlending
      });
      brainGroup.add(new THREE.LineSegments(lineGeo, lineMat));

      const pointGeo = new THREE.BufferGeometry().setFromPoints(points);
      const pointMat = new THREE.PointsMaterial({
        color: 0x000000, // Pitch Black
        size: 3.2,
        transparent: true,
        opacity: 0.95,
        blending: THREE.NormalBlending
      });
      brainGroup.add(new THREE.Points(pointGeo, pointMat));

      const coreGeo = new THREE.SphereGeometry(18, 20, 20);
      const coreMat = new THREE.MeshBasicMaterial({
        color: 0x1e293b,
        transparent: true,
        opacity: 0.22,
        wireframe: true,
        blending: THREE.NormalBlending
      });
      const coreMesh = new THREE.Mesh(coreGeo, coreMat);
      brainGroup.add(coreMesh);

      // 4. FLOATING PARTICLES
      const dustPoints = [];
      for (let i = 0; i < 45; i++) {
        dustPoints.push(new THREE.Vector3(
          (Math.random() - 0.5) * 110,
          (Math.random() - 0.5) * 100,
          (Math.random() - 0.5) * 110
        ));
      }
      const dustGeo = new THREE.BufferGeometry().setFromPoints(dustPoints);
      const dustMat = new THREE.PointsMaterial({
        color: 0x334155,
        size: 2.2,
        transparent: true,
        opacity: 0.55,
        blending: THREE.NormalBlending
      });
      brainGroup.add(new THREE.Points(dustGeo, dustMat));

      let t = 0;
      function render() {
        requestAnimationFrame(render);
        t += 0.015;
        brainGroup.rotation.y += 0.007; // Smooth 3D rotation
        brainGroup.rotation.x = Math.sin(t * 0.4) * 0.08;
        coreMesh.scale.setScalar(1 + Math.sin(t * 2.0) * 0.06);
        renderer.render(scene, camera);
      }
      render();

      window.addEventListener('resize', () => {
        camera.aspect = container.clientWidth / container.clientHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(container.clientWidth, container.clientHeight);
      });
    })();
  </script>
</body>
</html>
"""
components.html(HERO_SCI_FI_BRAIN_HTML, height=345)

# REPOSITORY DATA FETCHING

import sys
import os
frontend_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(frontend_dir, ".."))
for p in [frontend_dir, project_root]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from frontend.repo_manager import (
        fetch_repositories,
        get_active_repo,
        render_repo_selector,
        set_active_repo_id,
        remove_repository
    )
except ImportError:
    from repo_manager import (
        fetch_repositories,
        get_active_repo,
        render_repo_selector,
        set_active_repo_id,
        remove_repository
    )

repos = fetch_repositories()
current_repo = get_active_repo(repos)
repo_id = current_repo["id"] if current_repo else None

# FOUR METRIC TILES

stats = {"commits_count": 0, "files_count": 0, "issues_count": 0, "pull_requests_count": 0, "relationships_count": 0}
if repo_id:
    try:
        s_resp = httpx.get(f"{BACKEND_URL}/api/repositories/{repo_id}/stats", timeout=5.0)
        if s_resp.status_code == 200:
            stats = s_resp.json()
    except Exception:
        pass

commits_val = stats.get("total_commits") or stats.get("commits_count", 0)
commits_analyzed = stats.get("commits_count", 0)
files_val = stats.get("files_count", 0)
issues_val = stats.get("open_issues_count") if stats.get("open_issues_count") is not None else stats.get("issues_count", 0)
prs_val = stats.get("open_prs_count") if stats.get("open_prs_count") is not None else stats.get("pull_requests_count", 0)
rels_val = stats.get("relationships_count", 0)

st.markdown(f"""
<div class="metrics-deck">
  <div class="metric-card-box">
    <div class="metric-title">Repository Commits</div>
    <div class="metric-value">{commits_val}</div>
    <div class="metric-pill">↑ {commits_analyzed} analyzed in graph</div>
  </div>

  <div class="metric-card-box">
    <div class="metric-title">Files tracked</div>
    <div class="metric-value">{files_val}</div>
    <div class="metric-pill">↑ Unique changed paths</div>
  </div>

  <div class="metric-card-box">
    <div class="metric-title">Issues / PRs (Open)</div>
    <div class="metric-value">{issues_val} / {prs_val}</div>
    <div class="metric-pill">↑ Open on GitHub</div>
  </div>

  <div class="metric-card-box">
    <div class="metric-title">Relationships</div>
    <div class="metric-value">{rels_val}</div>
    <div class="metric-pill">↑ Provenance preserved</div>
  </div>
</div>
""", unsafe_allow_html=True)

# REPOSITORY CONFIGURATION & IMPORT

col_config, col_import = st.columns(2, gap="medium")

with col_config:
    with st.container(border=True):
        st.markdown("""
        <div style="font-weight: 700; font-size: 15px; color: #0f172a;">Repository Configuration</div>
        <div style="font-size: 12px; color: #64748b; margin: 3px 0 14px 0;">Active Repository for delivery analysis and search</div>
        """, unsafe_allow_html=True)

        if repos and repo_id:
            render_repo_selector(repos, key="main_active_repo_select", label_visibility="collapsed")

            col_btn1, col_btn2 = st.columns([1, 1], gap="small")
            with col_btn1:
                if st.button("Refresh Data", use_container_width=True, key="btn_refresh_main"):
                    st.rerun()
            with col_btn2:
                if st.button("🗑️ Remove Repo", use_container_width=True, key="btn_remove_repo"):
                    st.session_state["confirm_delete_repo_id"] = repo_id
                    st.rerun()

            if st.session_state.get("confirm_delete_repo_id") == repo_id:
                st.markdown(f"""
                <div style="margin: 12px 0 10px 0; padding: 12px 14px; background: #fef2f2; border: 1.5px solid #fecaca; border-radius: 10px; font-size: 12.5px; color: #991b1b; line-height: 1.5;">
                  <b>⚠️ Remove Repository?</b><br>
                  Are you sure you want to remove <b>{current_repo.get('owner', '')}/{current_repo.get('name', '')}</b> (#{repo_id}) and all its analyzed commits, issues, and graph memory?
                </div>
                """, unsafe_allow_html=True)
                conf_c1, conf_c2 = st.columns([1, 1], gap="small")
                with conf_c1:
                    if st.button("Yes, Remove", use_container_width=True, key="btn_confirm_remove_yes"):
                        success, msg = remove_repository(repo_id)
                        if success:
                            st.session_state.pop("confirm_delete_repo_id", None)
                            st.toast(f"✅ Removed repository #{repo_id} successfully!", icon="🗑️")
                            st.rerun()
                        else:
                            st.error(f"❌ {msg}")
                with conf_c2:
                    if st.button("Cancel", use_container_width=True, key="btn_cancel_remove"):
                        st.session_state.pop("confirm_delete_repo_id", None)
                        st.rerun()
        else:
            st.info("No repositories available. Import a repository on the right.")
            if st.button("Refresh Data", use_container_width=True, key="btn_refresh_main"):
                st.rerun()

with col_import:
    with st.container(border=True):
        st.markdown("""
        <div style="font-weight: 700; font-size: 15px; color: #0f172a;">Import a repository</div>
        <div style="font-size: 12px; color: #64748b; margin: 3px 0 14px 0;">Public GitHub URL · optional token configured in backend environment</div>
        """, unsafe_allow_html=True)

        new_repo_url = st.text_input(
            "Repository URL",
            placeholder="https://github.com/owner/repository",
            label_visibility="collapsed",
            key="input_repo_url_main"
        )

        if st.button("Validate & import", type="primary", use_container_width=True, key="btn_validate_import"):
            if new_repo_url:
                try:
                    r_resp = httpx.post(f"{BACKEND_URL}/api/repositories/import", json={"url": new_repo_url.strip()}, timeout=15.0)
                    if r_resp.status_code == 200:
                        imported_repo = r_resp.json()
                        new_id = imported_repo.get("id")
                        if new_id:
                            set_active_repo_id(new_id)
                        st.success(f"✅ Imported {imported_repo.get('owner', '')}/{imported_repo.get('name', '')} (#{new_id}) successfully! Refreshing...")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"Error: {r_resp.text}")
                except Exception as e:
                    st.error(f"Failed to connect to backend: {e}")

        
# LATEST RECORDED ACTIVITY

items_html = ""
if repo_id:
    try:
        c_resp = httpx.get(f"{BACKEND_URL}/api/repositories/{repo_id}/history/commits?limit=5", timeout=5.0)
        if c_resp.status_code == 200 and c_resp.json():
            commits_list = c_resp.json()[:5]
            for c in commits_list:
                msg = (c.get("message") or "Untitled commit").split("\n")[0]
                if len(msg) > 75:
                    msg = msg[:72] + "..."
                sha = c.get("sha", "")[:7]
                author = c.get("author") or "Unknown"
                
                items_html += f"""<div style="display: flex; align-items: flex-start; justify-content: space-between; gap: 14px; padding: 14px 6px; border-bottom: 1px solid #f1f5f9;">
  <div style="flex: 1; min-width: 0;">
    <div style="font-size: 13.5px; font-weight: 600; color: #0f172a; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{msg}</div>
    <div style="font-size: 11px; color: #64748b; margin-top: 4px; display: flex; align-items: center; gap: 8px;">
      <span>commit</span>
      <span>·</span>
      <code style="background: #eff6ff; color: #2563eb; padding: 2px 6px; border-radius: 4px; font-size: 11px; font-family: 'JetBrains Mono', monospace; font-weight: 600;">{sha}</code>
      <span>by</span>
      <b style="color: #334155;">{author}</b>
    </div>
  </div>
  <span style="font-size: 10px; font-weight: 700; padding: 4px 10px; border-radius: 20px; background: #f1f5f9; color: #475569; text-transform: uppercase;">commit</span>
</div>"""
    except Exception:
        pass

if not items_html:
    items_html = """<div style="padding: 40px 10px; text-align: center; color: #94a3b8; font-size: 13px;">
  <div style="font-size: 26px; margin-bottom: 8px;">📂</div>
  Import a repository to display commits, issues, and pull requests.
</div>"""

activity_card_html = f"""<div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.02); margin-top: 24px;">
  <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; padding-bottom: 12px; border-bottom: 1px solid #f1f5f9;">
    <span style="font-weight: 700; font-size: 15px; color: #0f172a;">Latest recorded activity</span>
    <span style="font-size: 12px; color: #2563eb; font-weight: 600;">Live Stream →</span>
  </div>
  <div>{items_html}</div>
</div>"""

st.markdown(activity_card_html, unsafe_allow_html=True)