"""
Contacts — SixPaths (clean app layout)

- Pagination uses user_service.get_users(limit, offset) (limit+1 to detect has_next)
- Detail uses user_service.get_user(id)
- Filter is current-page only (no backend search endpoint yet)
"""

from __future__ import annotations

import streamlit as st
from typing import Any, List, Tuple

from frontend.api.service_locator import get_api_client, get_user_service, get_auth_service
from styling import apply_custom_css

# -----------------------------
# Page setup
# -----------------------------
st.set_page_config(page_title="Contacts - SixPaths", page_icon="📇", layout="wide")
apply_custom_css()

api_client = get_api_client()
auth_service = get_auth_service()
user_service = get_user_service()

# -----------------------------
# Auth guard
# -----------------------------
if not st.session_state.get("logged_in"):
    st.warning("Please login first")
    st.stop()

token = st.session_state.get("token")
if not token:
    st.error("Authentication token missing. Please login.")
    st.stop()

api_client.set_token(token)
try:
    user_service.api_client.set_token(token)
except Exception:
    pass

# -----------------------------
# UI helpers
# -----------------------------
def user_label(u: Any) -> str:
    first = (getattr(u, "first_name", "") or "").strip()
    last = (getattr(u, "last_name", "") or "").strip()
    email = (getattr(u, "email", "") or "").strip()
    full = f"{first} {last}".strip()
    return full or email or f"User {getattr(u, 'id', '')}"

def user_subtitle(u: Any) -> str:
    company = (getattr(u, "company", "") or "").strip()
    sector = (getattr(u, "sector", "") or "").strip()
    if company and sector:
        return f"{company} • {sector}"
    return company or sector or ""

def safe_text(v: Any) -> str:
    return (v or "").strip() if isinstance(v, str) else (str(v) if v is not None else "")

def matches(u: Any, q: str) -> bool:
    ql = q.lower()
    for attr in ("first_name", "last_name", "email", "company", "sector"):
        v = safe_text(getattr(u, attr, "")).lower()
        if ql in v:
            return True
    return False

def fetch_users_page(limit: int, offset: int) -> Tuple[List[Any], bool]:
    """Fetch limit+1 to detect has_next without a total count."""
    try:
        rows = user_service.get_users(limit=limit + 1, offset=offset) or []
    except Exception:
        rows = []
    has_next = len(rows) > limit
    return rows[:limit], has_next

def clear_page_cache():
    st.session_state.pop("contacts_users_page", None)
    st.session_state.pop("contacts_has_next", None)

def kpi_card(title: str, value: str, caption: str = "") -> None:
    st.markdown(
        f"""
        <div class="six-card">
          <div style="font-size:0.85rem;color:#64748B;font-weight:650;">{title}</div>
          <div style="font-size:1.9rem;font-weight:850;color:#0F172A;line-height:1.15;">{value}</div>
          <div class="muted">{caption}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# -----------------------------
# Session state
# -----------------------------
st.session_state.setdefault("contacts_limit", 24)
st.session_state.setdefault("contacts_offset", 0)
st.session_state.setdefault("contacts_selected_id", None)

# -----------------------------
# Sidebar (clear sections)
# -----------------------------
st.sidebar.title("Contacts")

limit = st.sidebar.selectbox(
    "Users per page",
    options=[12, 24, 48, 96],
    index=[12, 24, 48, 96].index(st.session_state.contacts_limit),
)
if limit != st.session_state.contacts_limit:
    st.session_state.contacts_limit = limit
    st.session_state.contacts_offset = 0
    st.session_state.contacts_selected_id = None
    clear_page_cache()

search_text = st.sidebar.text_input("Filter this page", placeholder="Name, email, company, sector").strip()

nav1, nav2 = st.sidebar.columns(2)
if nav1.button("Previous", type="primary" ,width='stretch', disabled=(st.session_state.contacts_offset == 0)):
    st.session_state.contacts_offset = max(0, st.session_state.contacts_offset - st.session_state.contacts_limit)
    st.session_state.contacts_selected_id = None
    clear_page_cache()
    st.rerun()

# Next is handled after we know has_next, but we still render the button here.
next_clicked = nav2.button("Next", width='stretch',  type="primary")

if st.sidebar.button("Reload", width='stretch',  type="primary"):
    clear_page_cache()
    st.rerun()

with st.sidebar.expander("Advanced", expanded=False ):
    st.caption("This filter only applies to the currently loaded page.")
    if st.button("Clear selection", width='stretch', key="sidebar_clear_selection", type="primary"):
        st.session_state.contacts_selected_id = None
        st.rerun()

# -----------------------------
# Load users page (cached in session_state)
# -----------------------------
users_page = st.session_state.get("contacts_users_page")
has_next = st.session_state.get("contacts_has_next")

if users_page is None or has_next is None:
    with st.spinner("Loading contacts..."):
        users_page, has_next = fetch_users_page(
            limit=st.session_state.contacts_limit,
            offset=st.session_state.contacts_offset,
        )
    st.session_state.contacts_users_page = users_page
    st.session_state.contacts_has_next = has_next

# Now handle Next safely
if next_clicked:
    if bool(st.session_state.get("contacts_has_next", False)):
        st.session_state.contacts_offset = st.session_state.contacts_offset + st.session_state.contacts_limit
        st.session_state.contacts_selected_id = None
        clear_page_cache()
        st.rerun()
    else:
        st.sidebar.info("No more pages.")

display_users = users_page
if search_text:
    display_users = [u for u in users_page if matches(u, search_text)]

# -----------------------------
# Header + KPIs
# -----------------------------
st.title("📇 Contacts")
st.caption("Browse your contacts and view profile details.")

start = st.session_state.contacts_offset + 1
end = st.session_state.contacts_offset + len(users_page)

k1, k2, k3 = st.columns([1, 1, 2], gap="medium")  # clean KPI row [web:608]
with k1:
    kpi_card("On this page", str(len(users_page)), f"Showing {start}–{end}")
with k2:
    kpi_card("Filtered", str(len(display_users)), "Matches current filter")
with k3:
    with st.container(border=True):  # card container [web:720]
        st.markdown("**Quick actions**")
        a1, a2, a3 = st.columns(3)
        if a1.button("Reload", width='stretch'):
            clear_page_cache()
            st.rerun()
        if a2.button("Clear filter", width='stretch'):
            st.session_state["__tmp_clear_filter"] = True
        if a3.button("Clear selection", width='stretch', key="quick_clear_selection"):
            st.session_state.contacts_selected_id = None
            st.rerun()

# Clear filter via rerun-friendly pattern
if st.session_state.pop("__tmp_clear_filter", False):
    # There isn't a stable way to programmatically clear a text_input without a key;
    # simplest: re-render with a keyed text_input if you want that behavior.
    st.sidebar.warning("To clear the filter, delete the text in the sidebar input.")
    # (If you want, I can change the sidebar filter to use a key and reset it.)

st.divider()

# -----------------------------
# Main layout: list + details
# -----------------------------
left, right = st.columns([2, 3], gap="large")  # side-by-side layout [web:608]

# ---- Left: grid of contact cards ----
with left:
    with st.container(border=True):  # list panel card [web:720]
        st.subheader("Contacts list")
        st.caption("Select a card to open details.")

        if not display_users:
            st.info("No contacts match this filter on the current page.")
        else:
            cols_per_row = 3
            rows = (len(display_users) + cols_per_row - 1) // cols_per_row

            i = 0
            for _ in range(rows):
                row_cols = st.columns(cols_per_row, gap="small")
                for c in row_cols:
                    if i >= len(display_users):
                        break

                    u = display_users[i]
                    i += 1

                    uid = getattr(u, "id", None)
                    title = user_label(u)
                    subtitle = user_subtitle(u)
                    is_selected = (uid is not None and uid == st.session_state.contacts_selected_id)

                    with c:
                        with st.container(border=True):  # each card [web:720]
                            if is_selected:
                                st.caption("Selected")

                            st.markdown(f"**{title}**")
                            if subtitle:
                                st.caption(subtitle)

                            # Keeping an explicit button is clearer than “whole card click” in Streamlit
                            if st.button("View", key=f"view_{uid}", width='stretch'):
                                st.session_state.contacts_selected_id = uid
                                st.rerun()

# ---- Right: detail card ----
with right:
    with st.container(border=True):  # details panel card [web:720]
        st.subheader("Profile")

        selected_id = st.session_state.get("contacts_selected_id")
        if not selected_id:
            st.info("Select a contact from the list to view details.")
        else:
            with st.spinner("Loading contact details..."):
                try:
                    detail = user_service.get_user(str(selected_id))
                except Exception:
                    detail = None

            if not detail:
                st.error("Failed to load user details.")
            else:
                name = user_label(detail)
                company = safe_text(getattr(detail, "company", ""))
                sector = safe_text(getattr(detail, "sector", ""))
                email = safe_text(getattr(detail, "email", ""))
                phone = safe_text(getattr(detail, "phone", ""))
                linkedin = safe_text(getattr(detail, "linkedin_url", ""))

                st.markdown(f"### {name}")
                if company or sector:
                    st.caption(" • ".join([x for x in [company, sector] if x]))

                a, b = st.columns(2)
                with a:
                    st.markdown("**Email**")
                    st.write(email or "—")
                    st.markdown("**Phone**")
                    st.write(phone or "—")
                with b:
                    st.markdown("**Company**")
                    st.write(company or "—")
                    st.markdown("**Sector**")
                    st.write(sector or "—")

                if linkedin:
                    st.markdown("**LinkedIn**")
                    st.write(linkedin)

                st.divider()
                act1, act2 = st.columns(2)
                if act1.button("Edit", width='stretch'):
                    st.session_state["_selected_user"] = detail
                    st.session_state["_selected_user_id"] = getattr(detail, "id", None)
                    st.switch_page("pages/04_Edit_Profile.py")

                if act2.button("Clear selection", width='stretch', key="detail_clear_selection"):
                    st.session_state.contacts_selected_id = None
                    st.rerun()
