"""
Login Page — SixPaths (clean, production-style)

- Centered auth card
- Sign in + optional Create account in tabs
- Primary button for submit
- Minimal custom HTML; relies on theme/CSS
"""

from __future__ import annotations

import time
import streamlit as st

from models.input_models import AccountCreate
from styling import apply_custom_css
from frontend.api.service_locator import get_api_client, get_auth_service


# -----------------------------
# Page configuration (must be first)
# -----------------------------
st.set_page_config(page_title="Login - SixPaths", page_icon="🔗", layout="centered")
apply_custom_css()

api_client = get_api_client()
auth_service = get_auth_service()


# -----------------------------
# Session state defaults
# -----------------------------
st.session_state.setdefault("logged_in", False)
st.session_state.setdefault("login_attempts", 0)
st.session_state.setdefault("token", None)
st.session_state.setdefault("user_data", None)

# If already logged in, redirect
if st.session_state.logged_in:
    st.switch_page("pages/02_Dashboard.py")


# -----------------------------
# Decide whether account creation is allowed
# -----------------------------
try:
    account_creation_allowed = not bool(auth_service.account_user_exist())
except Exception:
    account_creation_allowed = False


# -----------------------------
# Header
# -----------------------------
st.markdown(
    """
    <div style="text-align:center; padding: 0.75rem 0 1.25rem 0;">
      <h1 style="margin-bottom:0.25rem;">SixPaths</h1>
      <div style="color:#64748B; font-size:1rem;">Professional Networking Visualization</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Center card
# -----------------------------
col_l, col_c, col_r = st.columns([1, 2, 1])
with col_c:
    with st.container(border=True):
        if account_creation_allowed:
            tab_login, tab_create = st.tabs(["Sign in", "Create account"])
        else:
            tab_login = st.container()
            tab_create = None

        # -------------------------
        # Tab: Sign in
        # -------------------------
        with tab_login:
            st.subheader("Sign in")
            st.caption("Enter your credentials to access your network.")

            with st.form("login_form", clear_on_submit=False):
                username = st.text_input("Username", placeholder="e.g. john")
                password = st.text_input("Password", type="password", placeholder="Your password")

                submitted = st.form_submit_button(
                    "Sign in",
                    type="primary",                 # button emphasis [web:743]
                    width='stretch',       # full width [web:757]
                )

            if submitted:
                if not username or not password:
                    st.warning("Please enter both username and password.")
                else:
                    with st.spinner("Authenticating..."):
                        try:
                            result = auth_service.login(username, password)
                        except Exception as e:
                            result = None
                            err = str(e)

                    if result and getattr(result, "access_token", None):
                        token = str(result.access_token)
                        api_client.set_token(token)

                        st.session_state.token = token
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.login_attempts = 0

                        # Preload user profile (optional)
                        try:
                            user_data = auth_service.get_current_user()
                            st.session_state.user_data = user_data
                            st.session_state.connections = None
                            st.session_state.referrals = None
                        except Exception:
                            # Don’t block login if profile load fails; show later in dashboard
                            st.session_state.user_data = None

                        st.success("Signed in successfully.")
                        time.sleep(0.3)
                        st.switch_page("pages/02_Dashboard.py")
                    else:
                        st.session_state.login_attempts += 1
                        st.error("Login failed. Check your credentials and try again.")

            # Small, professional footer area (not two info boxes)
            st.divider()
            st.caption("Tip: If you forgot your password, change it from Profile (personal mode).")

        # -------------------------
        # Tab: Create account
        # -------------------------
        if tab_create is not None:
            with tab_create:
                st.subheader("Create account")
                st.caption("Only available during initial setup.")

                with st.form("create_account_form", clear_on_submit=False):
                    c1, c2 = st.columns(2)
                    with c1:
                        ca_first = st.text_input("First name")
                        ca_username = st.text_input("Username")
                    with c2:
                        ca_last = st.text_input("Last name")
                        ca_email = st.text_input("Email (optional)")

                    ca_password = st.text_input("Password", type="password")

                    ca_submit = st.form_submit_button(
                        "Create account",
                        type="primary",
                        width='stretch',
                    )

                if ca_submit:
                    if not ca_username or not ca_password or not ca_first or not ca_last:
                        st.error("First name, last name, username, and password are required.")
                    else:
                        payload = AccountCreate(
                            username=ca_username,
                            password=ca_password,
                            first_name=ca_first,
                            last_name=ca_last,
                            email=(ca_email.strip() or None) if isinstance(ca_email, str) else None,
                            is_me=True,
                        )

                        with st.spinner("Creating account..."):
                            try:
                                created = auth_service.register_user(payload)
                            except Exception as e:
                                created = None
                                err = str(e)

                        if not created:
                            st.error(f"Failed to create account: {locals().get('err', 'Unknown error')}")
                        else:
                            # Auto-login after creation
                            with st.spinner("Logging in..."):
                                try:
                                    login_res = auth_service.login(ca_username, ca_password)
                                except Exception:
                                    login_res = None

                            if login_res and getattr(login_res, "access_token", None):
                                token = str(login_res.access_token)
                                api_client.set_token(token)
                                st.session_state.token = token
                                st.session_state.logged_in = True
                                st.session_state.username = ca_username
                                st.session_state.login_attempts = 0
                                st.session_state.connections = None
                                st.session_state.referrals = None
                                st.success("Account created. Welcome!")
                                time.sleep(0.3)
                                st.switch_page("pages/02_Dashboard.py")
                            else:
                                st.warning("Account created, but auto-login failed. Please sign in.")

# Page footer (simple, not loud)
st.caption("SixPaths © 2026")
