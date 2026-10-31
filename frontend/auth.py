import hashlib
import hmac
from pathlib import Path
import re
import secrets
import sqlite3

import streamlit as st

DB_PATH = Path(__file__).resolve().parent / "users.db"

_EMAIL_PATTERN = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.-]+$")
_CLEAN_USER_ID_PATTERN = re.compile(r"[^A-Za-z0-9_.-]")

_SCRYPT_N = 2**14
_SCRYPT_R = 8
_SCRYPT_P = 1


def get_connection() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def initialize_database() -> None:
    conn = get_connection()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                user_id TEXT NOT NULL COLLATE NOCASE UNIQUE,
                email TEXT NOT NULL COLLATE NOCASE UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    finally:
        conn.close()


initialize_database()


# Password Security & Validation

def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    password_hash = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=_SCRYPT_N,
        r=_SCRYPT_R,
        p=_SCRYPT_P,
    )
    return f"{salt.hex()}:{password_hash.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt_hex, hash_hex = stored_hash.split(":")
        salt = bytes.fromhex(salt_hex)
        original_hash = bytes.fromhex(hash_hex)

        computed_hash = hashlib.scrypt(
            password.encode("utf-8"),
            salt=salt,
            n=_SCRYPT_N,
            r=_SCRYPT_R,
            p=_SCRYPT_P,
        )
        return hmac.compare_digest(computed_hash, original_hash)
    except (ValueError, TypeError):
        return False


def valid_email(email: str) -> bool:
    return _EMAIL_PATTERN.fullmatch(email) is not None


# User Registration & Authentication

def register_user(full_name: str, email: str, password: str):
    cleaned_name = full_name.strip()
    cleaned_email = email.strip().lower()

    if not all([cleaned_name, cleaned_email, password]):
        return False, "Please fill in all fields."

    if not valid_email(cleaned_email):
        return False, "Please enter a valid email address."

    if len(password) < 8:
        return False, "Password must contain at least 8 characters."

    base_user_id = _CLEAN_USER_ID_PATTERN.sub("", cleaned_email.split("@")[0])
    if len(base_user_id) < 3:
        base_user_id = f"user_{secrets.token_hex(3)}"

    password_hash = hash_password(password)
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM users WHERE email = ? COLLATE NOCASE", (cleaned_email,))
        if cursor.fetchone():
            return False, "Email address is already registered."

        user_id = base_user_id
        count = 1
        while True:
            cursor.execute("SELECT id FROM users WHERE user_id = ? COLLATE NOCASE", (user_id,))
            if not cursor.fetchone():
                break
            user_id = f"{base_user_id}{count}"
            count += 1

        cursor.execute(
            """
            INSERT INTO users (full_name, user_id, email, password_hash)
            VALUES (?, ?, ?, ?)
            """,
            (cleaned_name, user_id, cleaned_email, password_hash),
        )
        conn.commit()
        return True, "Account created successfully! Please sign in."
    except sqlite3.Error:
        return False, "Unable to create your account. Please try again."
    finally:
        conn.close()


def authenticate_user(identifier: str, password: str):
    cleaned_identifier = identifier.strip()
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT id, full_name, user_id, email, password_hash
            FROM users
            WHERE email = ? COLLATE NOCASE OR user_id = ? COLLATE NOCASE
            """,
            (cleaned_identifier, cleaned_identifier),
        )
        user = cursor.fetchone()
    finally:
        conn.close()

    if user and verify_password(password, user[4]):
        return {
            "id": user[0],
            "full_name": user[1],
            "user_id": user[2],
            "email": user[3],
        }
    return None


# Login & Registration View

def render_login_screen() -> None:
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

.stApp {
    background: #f8fafc !important;
    font-family: 'Inter', sans-serif !important;
}

header[data-testid="stHeader"], footer, #MainMenu, [data-testid="stStatusWidget"], div[class^="viewerBadge_"] {
    display: none !important;
    visibility: hidden !important;
}
[data-testid="stSidebar"] { display: none !important; }

.block-container {
    max-width: 1080px !important;
    padding-top: 3.5rem !important;
    padding-bottom: 2rem !important;
    margin: 0 auto !important;
}

div[data-testid="stHorizontalBlock"] {
    display: flex !important;
    align-items: stretch !important;
}

div[data-testid="stColumn"] {
    display: flex !important;
    flex-direction: column !important;
}

div[data-testid="stColumn"] > div {
    height: 100% !important;
    display: flex !important;
    flex-direction: column !important;
}

.brand-panel,
div[data-testid="stVerticalBlockBorderWrapper"] {
    min-height: 640px !important;
    height: 100% !important;
    border-radius: 24px !important;
    box-sizing: border-box !important;
}

.brand-panel {
    background: linear-gradient(145deg, #eff6ff 0%, #eef2ff 50%, #ecfdf5 100%);
    border: 1.5px solid #dbeafe;
    padding: 38px 34px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff !important;
    border: 1.5px solid #e2e8f0 !important;
    padding: 32px 30px !important;
    box-shadow: 0 12px 32px rgba(15, 23, 42, 0.05) !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: flex-start !important;
}

div[data-testid="stVerticalBlockBorderWrapper"] > div {
    height: 100% !important;
    display: flex !important;
    flex-direction: column !important;
}

.brand-logo {
    width: 50px;
    height: 50px;
    border-radius: 14px;
    background: linear-gradient(135deg, #2563eb, #16a34a);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    font-weight: 800;
    margin-bottom: 14px;
}
.brand-title {
    font-size: 28px;
    font-weight: 800;
    color: #0f172a;
    letter-spacing: -0.5px;
    margin: 0;
}
.brand-title span { color: #2563eb; }
.brand-subtitle {
    font-size: 12px;
    font-weight: 700;
    color: #64748b;
    letter-spacing: 2px;
    margin-top: 4px;
}
.brand-heading {
    font-size: 24px;
    font-weight: 800;
    line-height: 1.35;
    color: #0f172a;
    margin-top: 26px;
    margin-bottom: 10px;
    letter-spacing: -0.4px;
}
.brand-description {
    font-size: 15px;
    line-height: 1.6;
    color: #475569;
    margin-bottom: 22px;
}

.feature-item {
    display: flex;
    align-items: center;
    gap: 16px;
    margin: 14px 0;
}
.feature-icon-box {
    width: 44px;
    height: 44px;
    min-width: 44px;
    border-radius: 12px;
    background-color: #dbeafe;
    display: flex;
    align-items: center;
    justify-content: center;
}
.feature-icon-box::before {
    content: "";
    display: block;
    width: 20px;
    height: 20px;
    background-color: #2563eb;
    -webkit-mask-repeat: no-repeat;
    mask-repeat: no-repeat;
    -webkit-mask-size: contain;
    mask-size: contain;
    -webkit-mask-position: center;
    mask-position: center;
}
.feature-icon-box.icon-search::before {
    -webkit-mask-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="black" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>');
    mask-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="black" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>');
}
.feature-icon-box.icon-graph::before {
    -webkit-mask-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="black" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" x2="15.42" y1="13.51" y2="17.49"/><line x1="15.41" x2="8.59" y1="6.51" y2="10.49"/></svg>');
    mask-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="black" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" x2="15.42" y1="13.51" y2="17.49"/><line x1="15.41" x2="8.59" y1="6.51" y2="10.49"/></svg>');
}
.feature-icon-box.icon-impact::before {
    -webkit-mask-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="black" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/></svg>');
    mask-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="black" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/></svg>');
}
.feature-title {
    font-size: 15px;
    font-weight: 700;
    color: #0f172a;
}
.feature-text {
    font-size: 13.5px;
    color: #64748b;
    margin-top: 2px;
}

.auth-heading {
    color: #0f172a;
    font-size: 25px;
    font-weight: 800;
    text-align: center;
    letter-spacing: -0.4px;
    margin-top: 6px;
}
.auth-description {
    color: #64748b;
    font-size: 14.5px;
    text-align: center;
    margin-bottom: 14px;
}

/* Segmented Tabs */
div[data-testid="stRadio"] > div {
    background: #f1f5f9 !important;
    padding: 4px !important;
    border-radius: 12px !important;
    border: 1px solid #e2e8f0 !important;
    display: flex !important;
    justify-content: space-around !important;
    gap: 6px !important;
    margin-bottom: 12px !important;
}
div[data-testid="stRadio"] label {
    flex: 1 !important;
    text-align: center !important;
    justify-content: center !important;
    padding: 8px 16px !important;
    border-radius: 9px !important;
    font-size: 14.5px !important;
    font-weight: 700 !important;
    cursor: pointer !important;
    margin: 0 !important;
}
div[data-testid="stRadio"] div[data-baseweb="radio"] > div:first-child,
div[data-testid="stRadio"] label > div:first-child,
div[data-testid="stRadio"] label > span:first-child,
div[data-testid="stRadio"] input[type="radio"] {
    display: none !important;
    visibility: hidden !important;
    width: 0 !important;
    height: 0 !important;
    margin: 0 !important;
}
div[data-testid="stRadio"] label:has(input:checked) {
    background: #ffffff !important;
    color: #0f172a !important;
    box-shadow: 0 2px 6px rgba(15, 23, 42, 0.08) !important;
}
div[data-testid="stRadio"] label:not(:has(input:checked)) {
    color: #64748b !important;
}

/* White Form Inputs */
div[data-testid="stForm"] {
    border: none !important;
    padding: 0 !important;
    display: flex !important;
    flex-direction: column !important;
    gap: 4px !important;
}

.stTextInput {
    margin-bottom: 6px !important;
}
.stTextInput label {
    color: #1e293b !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    margin-bottom: 4px !important;
}

div[data-testid="stTextInputRootElement"],
div[data-testid="stTextInputRootElement"] > div,
div[data-baseweb="input"],
div[data-baseweb="input"] > div,
div[data-baseweb="base-input"],
div[data-baseweb="base-input"] > input,
.stTextInput input,
.stTextInput > div > div {
    background-color: #ffffff !important;
    background: #ffffff !important;
    color: #0f172a !important;
    -webkit-text-fill-color: #0f172a !important;
}

div[data-baseweb="input"] {
    border: 1.5px solid #cbd5e1 !important;
    border-radius: 10px !important;
    min-height: 44px !important;
    padding: 0 10px !important;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02) !important;
}

div[data-baseweb="input"]:focus-within {
    border-color: #2563eb !important;
    box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.18) !important;
}

.stTextInput input {
    font-size: 14.5px !important;
    caret-color: #0f172a !important;
    border: none !important;
}

.stTextInput input::placeholder {
    color: #94a3b8 !important;
    -webkit-text-fill-color: #94a3b8 !important;
}

div[data-baseweb="input"] button {
    color: #64748b !important;
    background: transparent !important;
}

div[data-testid="stCheckbox"] label span {
    font-size: 14px !important;
    font-weight: 500 !important;
    color: #334155 !important;
}

div[data-testid="stFormSubmitButton"] > button {
    width: 100% !important;
    min-height: 46px !important;
    border-radius: 10px !important;
    border: none !important;
    background: #0f172a !important;
    color: white !important;
    font-weight: 700 !important;
    font-size: 15px !important;
    transition: all 0.2s ease !important;
    margin-top: 10px !important;
}
div[data-testid="stFormSubmitButton"] > button:hover {
    background: #2563eb !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 18px rgba(37, 99, 235, 0.35) !important;
}
</style>
""", unsafe_allow_html=True)

    left_col, right_col = st.columns([1.1, 0.9], gap="large")

    with left_col:
        st.markdown("""<div class="brand-panel">
<div>
<div class="brand-logo">PB</div>
<div class="brand-title">PROJECT <span>BRAIN</span></div>
<div class="brand-subtitle">CODE WITH CHAOS</div>
<div class="brand-heading">Institutional Memory Construct</div>
<div class="brand-description">Deterministic delivery intelligence, developer ownership mapping, and blast radius analysis backed strictly by git history.</div>
<div class="feature-item">
<div class="feature-icon-box icon-search"></div>
<div>
<div class="feature-title">Repository Intelligence</div>
<div class="feature-text">Deterministic commit and ownership discovery</div>
</div>
</div>
<div class="feature-item">
<div class="feature-icon-box icon-graph"></div>
<div>
<div class="feature-title">Relational Knowledge Graph</div>
<div class="feature-text">Interconnected code architectural maps</div>
</div>
</div>
<div class="feature-item">
<div class="feature-icon-box icon-impact"></div>
<div>
<div class="feature-title">Deterministic Blast Radius</div>
<div class="feature-text">Zero AI hallucinations · Ground-truth diffs</div>
</div>
</div>
</div>
</div>""", unsafe_allow_html=True)

    with right_col:
        with st.container(border=True):
            if st.session_state.pop("switch_to_login", False):
                st.session_state["auth_mode"] = "Login"
            elif "auth_mode" not in st.session_state:
                st.session_state["auth_mode"] = "Login"

            mode = st.radio(
                "Authentication Mode",
                ["Login", "Sign Up"],
                horizontal=True,
                label_visibility="collapsed",
                key="auth_mode",
            )

            if mode == "Login":
                if "signup_success" in st.session_state:
                    st.success(st.session_state.pop("signup_success"))

                st.markdown(
                    """<div class="auth-heading">Welcome Back</div>"""
                    """<div class="auth-description">Sign in to access your repository intelligence.</div>""",
                    unsafe_allow_html=True,
                )

                if "registered_email" in st.session_state:
                    st.session_state["login_email"] = st.session_state.pop("registered_email")

                with st.form("login_form"):
                    identifier = st.text_input("Email", key="login_email", placeholder="name@email.com")
                    password = st.text_input(
                        "Password",
                        type="password",
                        key="login_password",
                        placeholder="Enter your password",
                    )
                    st.checkbox("Remember me", value=True, key="login_remember")
                    login_button = st.form_submit_button("Sign In →", use_container_width=True)

                    if login_button:
                        if not identifier or not password:
                            st.error("Please enter both email and password.")
                        else:
                            user = authenticate_user(identifier, password)
                            if user:
                                st.session_state["authenticated"] = True
                                st.session_state["user"] = user
                                st.rerun()
                            else:
                                st.error("Invalid email or password.")
            else:
                st.markdown(
                    """<div class="auth-heading">Create Account</div>"""
                    """<div class="auth-description">Register with your email to get started.</div>""",
                    unsafe_allow_html=True,
                )

                with st.form("signup_form"):
                    full_name = st.text_input("Full Name", key="signup_name", placeholder="CWC")
                    email = st.text_input("Email Address", key="signup_email", placeholder="name@email.com")
                    password = st.text_input(
                        "Password",
                        type="password",
                        key="signup_password",
                        placeholder="At least 8 characters",
                    )
                    confirm_password = st.text_input(
                        "Confirm Password",
                        type="password",
                        key="signup_confirm_password",
                        placeholder="Repeat password",
                    )
                    signup_button = st.form_submit_button("Create Account →", use_container_width=True)

                    if signup_button:
                        if not all([full_name, email, password, confirm_password]):
                            st.error("Please fill in all fields.")
                        elif password != confirm_password:
                            st.error("Passwords do not match.")
                        else:
                            success, message = register_user(full_name, email, password)
                            if success:
                                st.session_state["switch_to_login"] = True
                                st.session_state["signup_success"] = message
                                st.session_state["registered_email"] = email
                                st.rerun()
                            else:
                                st.error(message)


# Authentication

def logout():
    """Clear authenticated session."""
    st.session_state["authenticated"] = False
    st.session_state["user"] = None
    st.rerun()


def require_auth() -> None:
    """Call this on any page to protect it."""
    if not st.session_state.get("authenticated", False):
        render_login_screen()
        st.stop()


if __name__ == "__main__":
    require_auth()