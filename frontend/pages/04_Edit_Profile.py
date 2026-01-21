import os
import json
import requests
import streamlit as st
from styling import apply_custom_css

st.set_page_config(page_title="Edit Profile - SixPaths", page_icon="👤", layout="centered")

apply_custom_css()

def _get_api_base() -> str:
    try:
        return st.secrets.get("API_BASE_URL") or os.getenv("API_BASE_URL", "http://localhost:8000")
    except Exception:
        return os.getenv("API_BASE_URL", "http://localhost:8000")

def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

def get_current_user(token: str) -> dict | None:
    url = _get_api_base().rstrip("/") + "/users/me"
    try:
        resp = requests.get(url, headers=_auth_headers(token), timeout=6)
        if resp.status_code == 200:
            return resp.json()
    except requests.RequestException:
        pass
    return None

def get_all_users(token: str) -> list:
    url = _get_api_base().rstrip("/") + "/users"
    try:
        resp = requests.get(url, headers=_auth_headers(token), timeout=8)
        if resp.status_code == 200:
            return resp.json()
    except requests.RequestException:
        pass
    return []

def get_user_by_id(user_id: int, token: str) -> dict | None:
    url = _get_api_base().rstrip("/") + f"/users/{user_id}"
    try:
        resp = requests.get(url, headers=_auth_headers(token), timeout=6)
        if resp.status_code == 200:
            return resp.json()
    except requests.RequestException:
        pass
    return None

def update_user(user_id: int, payload: dict, token: str) -> dict | None:
    url = _get_api_base().rstrip("/") + f"/users/{user_id}"
    try:
        resp = requests.put(url, headers=_auth_headers(token), json=payload, timeout=8)
        if resp.status_code in (200, 201):
            return resp.json()
    except requests.RequestException:
        pass
    return None

def change_password(new_password: str, token: str) -> bool:
    user = get_current_user(token)
    if not user:
        return False
    user_id = user.get("id")
    if not user_id:
        return False
    url = _get_api_base().rstrip("/") + f"/users/{user_id}/change-password"
    try:
        resp = requests.post(url, headers=_auth_headers(token), json={"new_password": new_password}, timeout=8)
        return resp.status_code == 200
    except requests.RequestException:
        return False

def create_user(payload: dict, token: str) -> dict | None:
    url = _get_api_base().rstrip("/") + "/users"
    try:
        resp = requests.post(url, headers=_auth_headers(token), json=payload, timeout=8)
        if resp.status_code in (200, 201):
            return resp.json()
    except requests.RequestException:
        pass
    return None


def create_user_account(payload: dict) -> dict | None:
    """Register a new user account via /users/register_user (no auth required)."""
    url = _get_api_base().rstrip("/") + "/users/register_user"
    try:
        # This endpoint does not require an Authorization header in the original backend
        resp = requests.post(url, json=payload, timeout=8)
        if resp.status_code in (200, 201):
            return resp.json()
    except requests.RequestException:
        pass
    return None

def delete_user(user_id: int, token: str) -> bool:
    url = _get_api_base().rstrip("/") + f"/users/{user_id}"
    try:
        resp = requests.delete(url, headers=_auth_headers(token), timeout=8)
        return resp.status_code in (200, 204)
    except requests.RequestException:
        return False

if not st.session_state.get("logged_in"):
    st.warning("⚠️ Please login first")
    st.stop()

token = st.session_state.get("token")
if not token:
    st.error("Authentication token missing. Please login again.")
    st.stop()

st.title("👤 Edit Profile")
st.markdown("Update user settings for yourself or other users")

with st.sidebar:
    if st.button("🏠 Home", use_container_width=True):
        st.experimental_set_query_params(page="home")
        st.switch_page("streamlit_app.py")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.token = None
        st.session_state.user_data = None
        st.switch_page("pages/01_Login.py")

# Load current user
with st.spinner("Loading current user..."):
    current_user = get_current_user(token)

if not current_user:
    st.error("Failed to load current user. Please refresh or login again.")
    st.stop()

st.subheader("My Profile")

with st.expander("View / Edit My Profile", expanded=True):
    user = current_user
    with st.form("edit_my_profile"):
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("First name", value=user.get("first_name", ""))
            last_name = st.text_input("Last name", value=user.get("last_name", ""))
            email = st.text_input("Email", value=user.get("email", ""))
        with col2:
            company = st.text_input("Company", value=user.get("company", ""))
            sector = st.text_input("Sector", value=user.get("sector", ""))
            phone = st.text_input("Phone", value=user.get("phone", ""))

        linkedin = st.text_input("LinkedIn URL", value=user.get("linkedin_url", ""))
        save = st.form_submit_button("Save changes")
    if save:
        payload = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "company": company,
            "sector": sector,
            "phone": phone,
            "linkedin_url": linkedin,
        }
        with st.spinner("Saving..."):
            updated = update_user(user.get("id"), payload, token)
        if updated:
            st.success("✅ Profile updated")
            st.session_state.user_data = updated
        else:
            st.error("❌ Failed to update profile")

with st.expander("Change My Password"):
    with st.form("change_password_form"):
        new_password = st.text_input("New password", type="password")
        confirm = st.text_input("Confirm password", type="password")
        change = st.form_submit_button("Change password")
    if change:
        if not new_password or new_password != confirm:
            st.error("Passwords do not match or are empty")
        else:
            with st.spinner("Changing password..."):
                ok = change_password(new_password, token)
            if ok:
                st.success("✅ Password changed")
            else:
                st.error("❌ Failed to change password")

st.markdown("---")

st.subheader("Manage Other Users")

if st.button("Reload users list"):
    st.session_state._users = None

users = st.session_state.get("_users")
if users is None:
    with st.spinner("Loading users..."):
        users = get_all_users(token)
    st.session_state._users = users

user_options = []
for u in users:
    display = f"{u.get('first_name','') or u.get('email','')} {u.get('last_name','')} (id:{u.get('id')})"
    user_options.append((display, u.get('id')))

if user_options:
    labels = [t[0] for t in user_options]
    selection = st.selectbox("Select user to edit", labels)
    selected_id = user_options[labels.index(selection)][1]
    if st.button("Load selected user"):
        st.session_state._selected_user = None
    selected_user = st.session_state.get("_selected_user")
    if selected_user is None or selected_user.get("id") != selected_id:
        with st.spinner("Loading user..."):
            selected_user = get_user_by_id(selected_id, token)
        st.session_state._selected_user = selected_user

    if selected_user:
        with st.form("edit_other_user"):
            col1, col2 = st.columns(2)
            with col1:
                o_first = st.text_input("First name", value=selected_user.get("first_name", ""))
                o_last = st.text_input("Last name", value=selected_user.get("last_name", ""))
                o_email = st.text_input("Email", value=selected_user.get("email", ""))
            with col2:
                o_company = st.text_input("Company", value=selected_user.get("company", ""))
                o_sector = st.text_input("Sector", value=selected_user.get("sector", ""))
                o_phone = st.text_input("Phone", value=selected_user.get("phone", ""))

            o_linkedin = st.text_input("LinkedIn URL", value=selected_user.get("linkedin_url", ""))
            save_other = st.form_submit_button("Save user")
        if save_other:
            payload = {
                "first_name": o_first,
                "last_name": o_last,
                "email": o_email,
                "company": o_company,
                "sector": o_sector,
                "phone": o_phone,
                "linkedin_url": o_linkedin,
            }
            with st.spinner("Saving user..."):
                updated = update_user(selected_user.get("id"), payload, token)
            if updated:
                st.success("✅ User updated")
                # refresh list and selected
                st.session_state._selected_user = updated
                st.session_state._users = None
            else:
                st.error("❌ Failed to update user")
        # Deletion controls
        st.markdown("---")
        st.markdown("### Delete user")
        confirm = st.checkbox("I understand this will permanently delete the selected user")
        if confirm:
            if st.button("Delete user", key=f"delete_{selected_user.get('id')}"):
                with st.spinner("Deleting user..."):
                    ok = delete_user(selected_user.get("id"), token)
                if ok:
                    st.success("✅ User deleted")
                    st.session_state._selected_user = None
                    st.session_state._users = None
                else:
                    st.error("❌ Failed to delete user")
else:
    st.info("No other users available")

st.markdown("---")
st.subheader("Create New User")
with st.form("create_user_form"):
    n_col1, n_col2 = st.columns(2)
    with n_col1:
        n_first = st.text_input("First name")
        n_last = st.text_input("Last name")
        n_email = st.text_input("Email")
    with n_col2:
        n_company = st.text_input("Company")
        n_sector = st.text_input("Sector")
        n_phone = st.text_input("Phone")
    n_linkedin = st.text_input("LinkedIn URL")
    create_as_account = st.checkbox("Create as user account (requires username & password)")
    n_username = st.text_input("Username") if create_as_account else None
    n_password = st.text_input("Temporary password", type="password") if create_as_account else st.text_input("Temporary password", type="password")
    create_btn = st.form_submit_button("Create user")

if create_btn:
    if create_as_account:
        # require username, email, password
        if not n_email or not n_username or not n_password:
            st.error("Email, username and password are required for account creation")
        else:
            payload = {
                "first_name": n_first,
                "last_name": n_last,
                "email": n_email,
                "company": n_company,
                "sector": n_sector,
                "phone": n_phone,
                "linkedin_url": n_linkedin,
                "username": n_username,
                "password": n_password,
                "is_me": False
            }
            with st.spinner("Registering user account..."):
                created = create_user_account(payload)
            if created:
                st.success("✅ User account created")
                st.session_state._users = None
                st.session_state._selected_user = created
            else:
                st.error("❌ Failed to create user account")
    else:
        if not n_email:
            st.error("Email is recommended for contacts but not required")
        payload = {
            "first_name": n_first,
            "last_name": n_last,
            "email": n_email,
            "company": n_company,
            "sector": n_sector,
            "phone": n_phone,
            "linkedin_url": n_linkedin,
        }
        with st.spinner("Creating contact..."):
            created = create_user(payload, token)
        if created:
            st.success("✅ Contact created")
            st.session_state._users = None
            st.session_state._selected_user = created
        else:
            st.error("❌ Failed to create contact")
