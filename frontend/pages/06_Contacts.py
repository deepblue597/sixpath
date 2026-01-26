"""
Contacts page — paginated user browser + detail view (card UI)

- Pagination uses user_service.get_users(limit, offset)
- Detail uses user_service.get_user(id)
- No "search across pages" (not reliable without backend search param)
"""

from __future__ import annotations

import streamlit as st
from typing import Any, List, Optional

from frontend.api.service_locator import get_api_client, get_user_service, get_auth_service
from styling import apply_custom_css


# -----------------------------
# Page config MUST be first
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

def fetch_users_page(limit: int, offset: int) -> tuple[List[Any], bool]:
    """
    Fetch limit+1 to reliably detect "has next" without needing total_count.
    """
    try:
        rows = user_service.get_users(limit=limit + 1, offset=offset) or []
    except Exception:
        rows = []

    has_next = len(rows) > limit
    return rows[:limit], has_next

def clear_page_cache():
    st.session_state.pop("contacts_users_page", None)
    st.session_state.pop("contacts_has_next", None)

# -----------------------------
# Session state
# -----------------------------
st.session_state.setdefault("contacts_limit", 24)      # good for 3-column grid
st.session_state.setdefault("contacts_offset", 0)
st.session_state.setdefault("contacts_selected_id", None)

# -----------------------------
# Sidebar controls
# -----------------------------
st.sidebar.header("Contacts")

limit = st.sidebar.selectbox(
    "Users per page",
    options=[12, 24, 48, 96],
    index=[12, 24, 48, 96].index(st.session_state.contacts_limit),
)

if limit != st.session_state.contacts_limit:
    st.session_state.contacts_limit = limit
    st.session_state.contacts_offset = 0
    clear_page_cache()

col_prev, col_next = st.sidebar.columns(2)
if col_prev.button("Previous", disabled=(st.session_state.contacts_offset == 0)):
    st.session_state.contacts_offset = max(0, st.session_state.contacts_offset - st.session_state.contacts_limit)
    clear_page_cache()

# We'll enable/disable Next after fetch; this button click is handled below.

if st.sidebar.button("Reload"):
    clear_page_cache()
    st.rerun()

# Optional: search on current page only (kept minimal)
search_text = st.sidebar.text_input("Filter current page (name/email/company/sector)").strip()

# -----------------------------
# Title + layout
# -----------------------------
st.title("📇 Contacts")
st.caption("Pick a contact card to view details on the right.")

left, right = st.columns([2, 3], gap="large")

# -----------------------------
# Load users page (cached)
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

# Next button AFTER we know has_next
if col_next.button("Next", disabled=not bool(st.session_state.get("contacts_has_next", False))):
    st.session_state.contacts_offset = st.session_state.contacts_offset + st.session_state.contacts_limit
    clear_page_cache()
    st.rerun()

# Filter within current page only
def matches(u: Any, q: str) -> bool:
    ql = q.lower()
    for attr in ("first_name", "last_name", "email", "company", "sector"):
        v = safe_text(getattr(u, attr, "")).lower()
        if ql in v:
            return True
    return False

display_users = users_page
if search_text:
    display_users = [u for u in users_page if matches(u, search_text)]

# -----------------------------
# Left: contact cards grid
# -----------------------------
with left:
    st.subheader("Contacts")

    start = st.session_state.contacts_offset + 1
    end = st.session_state.contacts_offset + len(users_page)
    st.caption(f"Showing {start}–{end}")

    if not display_users:
        st.info("No contacts to show (try clearing the filter).")
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
                    with st.container(border=True):
                        if is_selected:
                            st.markdown("**Selected**")
                        st.markdown(f"**{title}**")
                        if subtitle:
                            st.caption(subtitle)

                        # Small, clear action button
                        if st.button("View details", key=f"view_{uid}", use_container_width=True):
                            st.session_state.contacts_selected_id = uid
                            st.rerun()

# -----------------------------
# Right: detail card
# -----------------------------
with right:
    st.subheader("Details")

    selected_id = st.session_state.get("contacts_selected_id")
    if not selected_id:
        st.info("Select a contact card to see details.")
        st.stop()

    with st.spinner("Loading contact details..."):
        try:
            detail = user_service.get_user(str(selected_id))
        except Exception:
            detail = None

    if not detail:
        st.error("Failed to load user details.")
        st.stop()

    name = user_label(detail)
    company = safe_text(getattr(detail, "company", ""))
    sector = safe_text(getattr(detail, "sector", ""))
    email = safe_text(getattr(detail, "email", ""))
    phone = safe_text(getattr(detail, "phone", ""))
    linkedin = safe_text(getattr(detail, "linkedin_url", ""))

    with st.container(border=True):
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

    # actions = st.columns([1, 1, 2])
    # with actions[0]:
    #     if st.button("Edit", use_container_width=True):
    #         # Keep consistent with your existing edit profile page patterns
    #         st.session_state["_selected_user"] = detail
    #         st.session_state["_selected_user_id"] = getattr(detail, "id", None)
    #         st.switch_page("pages/04_Edit_Profile.py")
    # with actions[1]:
    #     if st.button("Clear", use_container_width=True):
    #         st.session_state.contacts_selected_id = None
    #         st.rerun()
