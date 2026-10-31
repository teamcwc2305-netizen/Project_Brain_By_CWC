# frontend/sidebar_nav.py
"""
Shared sidebar navigation styling and page label utilities for Project Brain.
Pure CSS instant styling — zero iframe delay and zero flash of old interface.
"""

import streamlit as st

SIDEBAR_NAV_CSS = """
<style>
  /* =========================================================
     INSTANT SIDEBAR NAVIGATION: NO FLASH, PURE CSS
     ========================================================= */

  /* Immediately format the navigation container */
  [data-testid="stSidebarNav"] {
    padding-top: 0.5rem !important;
  }

  /* Navigation Links Base Style */
  [data-testid="stSidebarNav"] a,
  [data-testid="stSidebarNavLink"],
  [data-testid="stSidebarNavLinkContainer"] a,
  section[data-testid="stSidebar"] nav ul li a {
    border-radius: 10px !important;
    transition: all 0.18s cubic-bezier(0.16, 1, 0.3, 1) !important;
    padding: 8px 14px !important;
    margin: 3px 0 !important;
    color: #475569 !important;
    font-weight: 500 !important;
    text-decoration: none !important;
  }

  /* Hover effect for ALL pages */
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

  /* Active page link styling */
  [data-testid="stSidebarNavLink"][aria-current="page"],
  [data-testid="stSidebarNav"] a[aria-current="page"],
  section[data-testid="stSidebar"] nav ul li a[aria-current="page"] {
    background: #f1f5f9 !important;
    color: #0f172a !important;
    font-weight: 700 !important;
    border-left: 3.5px solid #0f172a !important;
  }

  /* Active item on hover */
  [data-testid="stSidebarNavLink"][aria-current="page"]:hover,
  [data-testid="stSidebarNav"] a[aria-current="page"]:hover {
    background: #eff6ff !important;
    color: #1d4ed8 !important;
    border-left: 3.5px solid #2563eb !important;
  }

  /* =========================================================
     INSTANT ZERO-FLASH REPLACEMENT OF "streamlit app" -> "Overview"
     ========================================================= */
  [data-testid="stSidebarNavItems"] li:first-child [data-testid="stSidebarNavLink"] span,
  [data-testid="stSidebarNavItems"] li:first-child a span,
  [data-testid="stSidebarNav"] ul li:first-child a span,
  section[data-testid="stSidebar"] nav ul li:first-child a span,
  [data-testid="stSidebarNav"] a[href="/"] span,
  [data-testid="stSidebarNav"] a[href="./"] span,
  [data-testid="stSidebarNav"] a[href=""] span {
    font-size: 0 !important;
    visibility: hidden !important;
    display: inline-block !important;
    line-height: 0 !important;
    height: 0 !important;
    width: 0 !important;
    overflow: hidden !important;
  }

  [data-testid="stSidebarNavItems"] li:first-child [data-testid="stSidebarNavLink"]::after,
  [data-testid="stSidebarNavItems"] li:first-child a::after,
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
  section[data-testid="stSidebar"] nav ul li:first-child a:hover::after {
    color: #1d4ed8 !important;
    font-weight: 600 !important;
  }
</style>
"""


def render_sidebar():
    # Inject styling at the top of the stream immediately
    st.markdown(SIDEBAR_NAV_CSS, unsafe_allow_html=True)

    # Optional User Profile & Sign Out Widget
    if st.session_state.get("authenticated", False):
        user = st.session_state.get("user") or {}
        user_name = user.get("full_name") or user.get("email") or "User"
        user_email = user.get("email") or ""
        with st.sidebar:
            st.markdown(f"""
            <div style="margin-top: 20px; margin-bottom: 8px; padding: 10px 12px; background: #ffffff; border: 1.5px solid #e2e8f0; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">
              <div style="display: flex; align-items: center; gap: 10px;">
                <div style="width: 32px; height: 32px; border-radius: 8px; background: linear-gradient(135deg, #2563eb, #16a34a); color: white; display: grid; place-items: center; font-weight: 700; font-size: 13px; flex-shrink: 0;">
                  {user_name[:1].upper()}
                </div>
                <div style="min-width: 0; flex: 1;">
                  <div style="font-weight: 700; font-size: 13px; color: #0f172a; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{user_name}</div>
                  <div style="font-size: 11px; color: #64748b; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{user_email}</div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Sign Out", key="btn_sidebar_signout", use_container_width=True):
                st.session_state["authenticated"] = False
                st.session_state["user"] = None
                st.rerun()