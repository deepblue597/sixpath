import streamlit as st

# from models.response_models import UserResponse
from styling import apply_custom_css
from models.input_models import UserCreate, UserUpdate
from frontend.api.service_locator import get_api_client, get_auth_service, get_user_service
from frontend.utils import user_label

st.set_page_config(page_title="Edit Profile - SixPaths", page_icon="👤", layout="centered")
apply_custom_css()

api_client = get_api_client()
auth_service = get_auth_service()
user_service = get_user_service()

# -----------------------------
# Auth guard
# -----------------------------
if not st.session_state.get("logged_in"):
    st.warning("Please login first.")
    st.stop()

token = st.session_state.get("token")
if not token:
    st.error("Authentication token missing. Please login again.")
    st.stop()

api_client.set_token(token)

st.title("👤 Edit Profile")
st.caption("Update your profile, manage users, or create a new profile.")

# -----------------------------
# Helpers
# -----------------------------
def _none_if_empty(v: str | None) -> str | None:
    if v is None:
        return None
    v2 = v.strip()
    return v2 if v2 else None

# def user_label(u : UserResponse) -> str:
#     first = (u.first_name or '').strip()
#     last = (u.last_name or "").strip()
#     email = (u.email or "").strip()
#     uid = u.id
#     name = f"{first} {last}".strip()
#     base = name or email or f"User {uid}"
#     return f"{base} (id:{uid})"

def reset_manage_users_state() -> None:
    for k in (
        "_users_page",
        "_users_page_offset",
        "_users_page_limit",
        "_users_has_next",
        "_selected_user_id",
        "_selected_user",
    ):
        st.session_state.pop(k, None)

def load_users_page(limit: int, offset: int):
    """
    Requires backend support: user_service.get_users(limit=?, offset=?)
    If your get_users currently ignores these params, fix the backend route/service/DAO.
    """
    users_page = user_service.get_users(limit=limit, offset=offset)
    users_page = users_page or []
    has_next = len(users_page) == limit
    return users_page, has_next

def load_user(user_id: str):
    return user_service.get_user(user_id)

def update_user_payload(user_id: str, payload: UserUpdate):
    """
    Preferred: user_service.update_user accepts a Pydantic model and serializes internally.
    If yours DOESN'T, change the service to do: payload.model_dump(exclude_none=True). [web:517][web:519]
    """
    return user_service.update_user(user_id, payload)

# -----------------------------
# Load current user
# -----------------------------
with st.spinner("Loading current user..."):
    try:
        current_user = auth_service.get_current_user()
    except Exception:
        current_user = None

if not current_user:
    st.error("Failed to load current user. Please refresh or login again.")
    st.stop()

# -----------------------------
# Tabs
# -----------------------------
tabs = st.tabs(["Edit My Profile", "Edit Users Profile", "Create New Profile"])

# =========================================================
# TAB 0 — Edit My Profile
# =========================================================
with tabs[0]:
    st.subheader("My Profile")

    with st.form("edit_my_profile"):
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("First name", value=getattr(current_user, "first_name", "") or "")
            last_name = st.text_input("Last name", value=getattr(current_user, "last_name", "") or "")
            email = st.text_input("Email", value=getattr(current_user, "email", "") or "")
        with col2:
            company = st.text_input("Company", value=getattr(current_user, "company", "") or "")
            sector = st.text_input("Sector", value=getattr(current_user, "sector", "") or "")
            phone = st.text_input("Phone", value=getattr(current_user, "phone", "") or "")

        linkedin = st.text_input("LinkedIn URL", value=getattr(current_user, "linkedin_url", "") or "")
        save = st.form_submit_button("Save changes")

    if save:
        payload = UserUpdate(
            first_name=_none_if_empty(first_name) or "",  # keep as "" if your model requires str
            last_name=_none_if_empty(last_name) or "",
            email=_none_if_empty(email),
            company=_none_if_empty(company),
            sector=_none_if_empty(sector),
            phone=_none_if_empty(phone),
            linkedin_url=_none_if_empty(linkedin),
        )
        with st.spinner("Saving..."):
            try:
                updated = user_service.update_user(str(getattr(current_user, "id")), payload)
            except Exception:
                updated = None

        if updated:
            st.success("Profile updated.")
            # Refresh current_user view
            try:
                current_user = auth_service.get_current_user()
            except Exception:
                pass
        else:
            st.error("Failed to update profile.")

    st.divider()

    st.subheader("Change My Password")
    with st.form("change_password_form"):
        new_password = st.text_input("New password", type="password")
        confirm = st.text_input("Confirm password", type="password")
        change = st.form_submit_button("Change password")

    if change:
        if not new_password or new_password != confirm:
            st.error("Passwords do not match or are empty.")
        else:
            with st.spinner("Changing password..."):
                try:
                    ok = bool(auth_service.change_password(str(getattr(current_user, "id")), new_password))
                except Exception:
                    ok = False
            if ok:
                st.success("Password changed.")
            else:
                st.error("Failed to change password.")

# =========================================================
# TAB 1 — Manage Users (PRO layout)
# =========================================================
with tabs[1]:
    st.subheader("Manage Users")
    st.caption("Browse users on the left, edit details on the right.")

    # init state
    st.session_state.setdefault("_users_page_limit", 50)
    st.session_state.setdefault("_users_page_offset", 0)
    st.session_state.setdefault("_users_page", [])
    st.session_state.setdefault("_users_has_next", False)
    st.session_state.setdefault("_selected_user_id", None)
    st.session_state.setdefault("_selected_user", None)

    # --- Top controls card ---
    with st.container(border=True):
        top = st.columns([1, 1, 2], vertical_alignment="center")
        with top[0]:
            page_limit = st.selectbox(
                "Rows per page",
                options=[25, 50, 100],
                index=[25, 50, 100].index(st.session_state._users_page_limit),
            )
        with top[1]:
            current_page_num = (st.session_state._users_page_offset // st.session_state._users_page_limit) + 1
            go_page = st.number_input("Page", min_value=1, value=int(current_page_num), step=1)
        with top[2]:
            r1, r2, r3 = st.columns(3)
            prev_clicked = r1.button("Previous", width='stretch', disabled=st.session_state._users_page_offset == 0)
            next_clicked = r2.button("Next", width='stretch', disabled=not st.session_state._users_has_next)
            reload_clicked = r3.button("Reload", width='stretch')

    if reload_clicked:
        reset_manage_users_state()
        st.rerun()

    # apply limit change
    if page_limit != st.session_state._users_page_limit:
        st.session_state._users_page_limit = page_limit
        st.session_state._users_page_offset = 0
        st.session_state._users_page = []
        st.session_state._selected_user_id = None
        st.session_state._selected_user = None

    # apply go-to-page change
    desired_offset = (int(go_page) - 1) * st.session_state._users_page_limit
    if desired_offset != st.session_state._users_page_offset:
        st.session_state._users_page_offset = desired_offset
        st.session_state._users_page = []
        st.session_state._selected_user_id = None
        st.session_state._selected_user = None

    if prev_clicked:
        st.session_state._users_page_offset = max(0, st.session_state._users_page_offset - st.session_state._users_page_limit)
        st.session_state._users_page = []
        st.session_state._selected_user_id = None
        st.session_state._selected_user = None
        st.rerun()

    if next_clicked:
        st.session_state._users_page_offset = st.session_state._users_page_offset + st.session_state._users_page_limit
        st.session_state._users_page = []
        st.session_state._selected_user_id = None
        st.session_state._selected_user = None
        st.rerun()

    # load current page
    if not st.session_state._users_page:
        with st.spinner("Loading users..."):
            try:
                users_page, has_next = load_users_page(
                    limit=st.session_state._users_page_limit,
                    offset=st.session_state._users_page_offset,
                )
            except TypeError:
                st.error("Backend user_service.get_users must accept limit and offset for pagination.")
                users_page, has_next = [], False
            except Exception:
                users_page, has_next = [], False

        st.session_state._users_page = users_page
        st.session_state._users_has_next = has_next

    users_page = st.session_state._users_page

    # --- Two panel layout ---
    left, right = st.columns([2, 3], gap="large")

    with left:
        with st.container(border=True):
            st.markdown("### Users on this page")
            st.caption(f"Showing {len(users_page)} users (page {int(go_page)}).")

            if not users_page:
                st.info("No users found on this page.")
            else:
                id_by_label = {
                    user_label(u): str(getattr(u, "id"))
                    for u in users_page
                    if getattr(u, "id", None) is not None
                }

                selected_label = st.selectbox(
                    "Select a user",
                    options=[""] + sorted(id_by_label.keys()),
                )
                selected_id = id_by_label.get(selected_label) if selected_label else None

                if selected_id and selected_id != st.session_state.get("_selected_user_id"):
                    st.session_state._selected_user_id = selected_id
                    st.session_state._selected_user = None
                    st.rerun()

                with st.expander("Debug (optional)", expanded=False):
                    st.write(
                        {
                            "offset": st.session_state._users_page_offset,
                            "limit": st.session_state._users_page_limit,
                            "has_next": st.session_state._users_has_next,
                        }
                    )

    with right:
        with st.container(border=True):
            st.markdown("### Details & actions")

            selected_id = st.session_state.get("_selected_user_id")
            if not selected_id:
                st.info("Pick a user on the left to edit their profile.")
            else:
                # Load selected user details
                selected_user = st.session_state.get("_selected_user")
                if selected_user is None:
                    with st.spinner("Loading user details..."):
                        try:
                            selected_user = load_user(selected_id)
                        except Exception:
                            selected_user = None
                    st.session_state._selected_user = selected_user

                if not selected_user:
                    st.error("Could not load selected user.")
                else:
                    st.caption(f"Editing: {user_label(selected_user)}")

                    # --- Edit form card ---
                    with st.form("edit_other_user_form"):
                        c1, c2 = st.columns(2)
                        with c1:
                            o_first = st.text_input("First name", value=getattr(selected_user, "first_name", "") or "")
                            o_last = st.text_input("Last name", value=getattr(selected_user, "last_name", "") or "")
                            o_email = st.text_input("Email", value=getattr(selected_user, "email", "") or "")
                        with c2:
                            o_company = st.text_input("Company", value=getattr(selected_user, "company", "") or "")
                            o_sector = st.text_input("Sector", value=getattr(selected_user, "sector", "") or "")
                            o_phone = st.text_input("Phone", value=getattr(selected_user, "phone", "") or "")

                        o_linkedin = st.text_input("LinkedIn URL", value=getattr(selected_user, "linkedin_url", "") or "")
                        save_other = st.form_submit_button("Save changes", width='stretch')

                    if save_other:
                        payload = UserUpdate(
                            first_name=_none_if_empty(o_first) or "",
                            last_name=_none_if_empty(o_last) or "",
                            email=_none_if_empty(o_email),
                            company=_none_if_empty(o_company),
                            sector=_none_if_empty(o_sector),
                            phone=_none_if_empty(o_phone),
                            linkedin_url=_none_if_empty(o_linkedin),
                        )
                        with st.spinner("Saving user..."):
                            try:
                                updated = update_user_payload(str(getattr(selected_user, "id")), payload)
                            except Exception:
                                updated = None

                        if updated:
                            st.success("User updated.")
                            st.session_state._selected_user = updated
                            st.session_state._users_page = []  # reload list
                            st.rerun()
                        else:
                            st.error("Failed to update user.")

                    # --- Danger zone card ---
                    st.divider()
                    st.markdown("### Danger zone")
                    st.caption("Deleting a user is permanent.")

                    confirm = st.checkbox("I understand this will permanently delete this user.", value=False)
                    delete_clicked = st.button("Delete user", width='stretch', disabled=not confirm)

                    if delete_clicked:
                        with st.spinner("Deleting user..."):
                            try:
                                ok = user_service.delete_user(str(getattr(selected_user, "id")))
                            except Exception:
                                ok = False

                        if ok:
                            st.success("User deleted.")
                            st.session_state._selected_user_id = None
                            st.session_state._selected_user = None
                            st.session_state._users_page = []
                            st.rerun()
                        else:
                            st.error("Failed to delete user.")


# =========================================================
# TAB 2 — Create New Profile
# =========================================================
with tabs[2]:
    st.subheader("Create New Profile")

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
        create_btn = st.form_submit_button("Create user")

    if create_btn:
        payload = UserCreate(
            first_name=_none_if_empty(n_first) or "",
            last_name=_none_if_empty(n_last) or "",
            email=_none_if_empty(n_email),
            company=_none_if_empty(n_company),
            sector=_none_if_empty(n_sector),
            phone=_none_if_empty(n_phone),
            linkedin_url=_none_if_empty(n_linkedin),
        )

        with st.spinner("Creating contact..."):
            try:
                created = user_service.create_user(payload)
            except Exception:
                created = None

        if created:
            st.success("Contact created.")
            st.session_state._users_page = []
            st.session_state._selected_user = created
            st.session_state._selected_user_id = str(getattr(created, "id", ""))
        else:
            st.error("Failed to create contact.")
