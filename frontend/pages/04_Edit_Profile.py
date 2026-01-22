import os
import json
import requests
import streamlit as st
from styling import apply_custom_css
from api.service_locator import get_api_client , get_auth_service , get_user_service
st.set_page_config(page_title="Edit Profile - SixPaths", page_icon="👤", layout="centered")

apply_custom_css()

api_client = get_api_client()
auth_service = get_auth_service()
user_service = get_user_service()


if not st.session_state.get("logged_in"):
    st.warning("⚠️ Please login first")
    st.stop()

token = st.session_state.get("token")
if not token:
    st.error("Authentication token missing. Please login again.")
    st.stop()

st.title("👤 Edit Profile")
st.markdown("Update user settings for yourself or other users")

# with st.sidebar:
#     if st.button("🏠 Home", use_container_width=True):
#         st.experimental_set_query_params(page="home")
#         st.switch_page("streamlit_app.py")
#     if st.button("🚪 Logout", use_container_width=True):
#         st.session_state.logged_in = False
#         st.session_state.token = None
#         st.session_state.user_data = None
#         st.switch_page("pages/01_Login.py")

# Load current user
with st.spinner("Loading current user..."):
    # ensure API client has token for auth headers
    api_client.set_token(token)
    try:
        current_user = auth_service.get_current_user()
    except Exception:
        current_user = None

if not current_user:
    st.error("Failed to load current user. Please refresh or login again.")
    st.stop()

tabs = st.tabs(["Edit My Settings", "Edit Other Users"])

with tabs[0]:
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
                try:
                    updated = user_service.update_user(str(user.get("id")), payload)
                except Exception:
                    updated = None
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
                    try:
                        resp = auth_service.change_password(str(user.get("id")), new_password)
                        ok = bool(resp)
                    except Exception:
                        ok = False
                if ok:
                    st.success("✅ Password changed")
                else:
                    st.error("❌ Failed to change password")

with tabs[1]:
    st.markdown("---")
    st.subheader("Manage Other Users")

    if st.button("Reload users list"):
        st.session_state._users = None

    users = st.session_state.get("_users")
    if users is None:
        with st.spinner("Loading users..."):
            try:
                users = user_service.get_users()
            except Exception:
                users = []
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
                try:
                    selected_user = user_service.get_user(str(selected_id))
                except Exception:
                    selected_user = None
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
                    try:
                        updated = user_service.update_user(str(selected_user.get("id")), payload)
                    except Exception:
                        updated = None
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
                        try:
                            ok = user_service.delete_user(str(selected_user.get("id")))
                        except Exception:
                            ok = False
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
                    try:
                        created = auth_service.register_user(payload)
                    except Exception:
                        created = None
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
                try:
                    created = user_service.create_user(payload)
                except Exception:
                    created = None
            if created:
                st.success("✅ Contact created")
                st.session_state._users = None
                st.session_state._selected_user = created
            else:
                st.error("❌ Failed to create contact")
