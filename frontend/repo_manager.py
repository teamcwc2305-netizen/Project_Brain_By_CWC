import os
import httpx
import streamlit as st

BACKEND_URL = "http://127.0.0.1:8000"
ACTIVE_REPO_FILE = ".active_repo_id"

ALL_SELECT_KEYS = [
    "main_active_repo_select",
    "desc_repo_select",
    "graph_repo_selector",
    "history_repo_select",
    "search_repo_select",
    "impact_repo_select",
    "about_repo_select",
    "sidebar_active_repo_select",
]


def fetch_repositories(timeout: float = 5.0) -> list:
    """Fetch all repositories from backend API ordered by recently imported first."""
    try:
        resp = httpx.get(f"{BACKEND_URL}/api/repositories", timeout=timeout)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return []


def read_persisted_repo_id() -> int | None:
    try:
        if os.path.exists(ACTIVE_REPO_FILE):
            with open(ACTIVE_REPO_FILE, "r", encoding="utf-8") as f:
                val = f.read().strip()
                if val.isdigit():
                    return int(val)
    except Exception:
        pass
    return None


def write_persisted_repo_id(repo_id: int):
    try:
        with open(ACTIVE_REPO_FILE, "w", encoding="utf-8") as f:
            f.write(str(repo_id))
    except Exception:
        pass


def set_active_repo_id(repo_id: int):
    """
    Set active repository globally:
    Updates session state and disk marker, bumps revision, and synchronizes selection.
    """
    st.session_state["active_repo_id"] = repo_id
    write_persisted_repo_id(repo_id)
    st.session_state["repo_selector_rev"] = st.session_state.get("repo_selector_rev", 0) + 1


def remove_repository(repo_id: int) -> tuple[bool, str]:
    """
    Deletes the repository from backend and cleans up global active repository state.
    Returns (success: bool, message: str).
    """
    try:
        resp = httpx.delete(f"{BACKEND_URL}/api/repositories/{repo_id}", timeout=10.0)
        if resp.status_code == 200:
            persisted = read_persisted_repo_id()
            if persisted == repo_id and os.path.exists(ACTIVE_REPO_FILE):
                try:
                    os.remove(ACTIVE_REPO_FILE)
                except Exception:
                    pass

            st.session_state.pop("active_repo_id", None)

            # Immediately fetch remaining repositories from backend
            fresh_repos = fetch_repositories()
            if fresh_repos:
                next_id = fresh_repos[0]["id"]
                st.session_state["active_repo_id"] = next_id
                write_persisted_repo_id(next_id)
            else:
                if os.path.exists(ACTIVE_REPO_FILE):
                    try:
                        os.remove(ACTIVE_REPO_FILE)
                    except Exception:
                        pass

            st.session_state["repo_selector_rev"] = st.session_state.get("repo_selector_rev", 0) + 1

            return True, resp.json().get("message", "Repository removed successfully.")
        else:
            return False, f"Server error: {resp.text}"
    except Exception as e:
        return False, f"Connection failed: {e}"


def get_active_repo(repos: list) -> dict | None:
    """
    Returns the authoritative active repository record.
    Guarantees consistency between session_state and .active_repo_id file.
    """
    if not repos:
        return None

    repo_ids = [r["id"] for r in repos]

    current_id = st.session_state.get("active_repo_id")
    if not current_id or current_id not in repo_ids:
        persisted = read_persisted_repo_id()
        if persisted and persisted in repo_ids:
            current_id = persisted
        else:
            current_id = repos[0]["id"]

    st.session_state["active_repo_id"] = current_id
    write_persisted_repo_id(current_id)

    return next((r for r in repos if r["id"] == current_id), repos[0])


def render_repo_selector(repos: list, key: str, label_visibility: str = "visible") -> int | None:
    """
    Renders a synchronized repository selectbox with versioned widget keys.
    Prevents browser client caching of deleted or stale repository selections.
    """
    if not repos:
        return None

    active_repo = get_active_repo(repos)
    active_id = active_repo["id"]

    repo_ids = [r["id"] for r in repos]
    labels = [f"{r['owner']}/{r['name']} (#{r['id']})" for r in repos]
    target_idx = repo_ids.index(active_id) if active_id in repo_ids else 0
    target_label = labels[target_idx]

    rev = st.session_state.get("repo_selector_rev", 0)
    actual_key = f"{key}_v{rev}"

    if st.session_state.get(actual_key) != target_label:
        st.session_state[actual_key] = target_label

    def _on_repo_selection_change():
        selected_label = st.session_state.get(actual_key)
        if selected_label in labels:
            new_id = repo_ids[labels.index(selected_label)]
            if new_id != st.session_state.get("active_repo_id"):
                st.session_state["active_repo_id"] = new_id
                write_persisted_repo_id(new_id)
                current_rev = st.session_state.get("repo_selector_rev", 0)
                for other_k in ALL_SELECT_KEYS:
                    other_actual = f"{other_k}_v{current_rev}"
                    st.session_state[other_actual] = selected_label

    st.selectbox(
        "Select Repository",
        labels,
        key=actual_key,
        index=target_idx,
        on_change=_on_repo_selection_change,
        label_visibility=label_visibility
    )

    return st.session_state.get("active_repo_id", active_id)