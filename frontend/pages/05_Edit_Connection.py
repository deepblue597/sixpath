"""
Connections CRUD Page for SixPaths

Tabs:
- All Connections: list all connections (same behavior as your current page)
- Edit Connection: choose an existing connection and update/delete it (same behavior)
- Create Connection: 3-step wizard with paginated user pickers (no search), prevents same person

Assumptions:
- user_service.get_users(limit: int, offset: int) exists and respects pagination.
- connection_service.get_all_connections(), get_connection(id), update_connection(id, payload),
  delete_connection(id), create_connection(payload) exist.
"""
from __future__ import annotations

from datetime import datetime
import streamlit as st
from styling import apply_custom_css

from frontend.api.service_locator import get_connection_service, get_user_service
from models.response_models import UserResponse, ConnectionResponse
from models.input_models import ConnectionCreate, ConnectionUpdate

st.set_page_config(page_title="Edit Connection - SixPaths", page_icon="✏️", layout="centered")
apply_custom_css()

connection_service = get_connection_service()
user_service = get_user_service()

# -----------------------------
# Auth guard
# -----------------------------
if not st.session_state.get("logged_in"):
    st.warning("⚠️ Please login first")
    st.stop()

token = st.session_state.get("token")
if not token:
    st.error("Authentication token missing. Please login.")
    st.stop()

current_user = st.session_state.get("user_data")
if not current_user:
    st.error("Current user not loaded. Please load your profile first.")
    st.stop()

# Ensure services have token
try:
    connection_service.api_client.set_token(token)
except Exception:
    pass
try:
    user_service.api_client.set_token(token)
except Exception:
    pass

st.title("✏️ Edit Connection")

# -----------------------------
# Helpers
# -----------------------------
def _user_label(u) -> str:
    fn = (getattr(u, "first_name", "") or "").strip()
    ln = (getattr(u, "last_name", "") or "").strip()
    email = (getattr(u, "email", "") or "").strip()
    uid = getattr(u, "id", "")
    name = f"{fn} {ln}".strip()
    return f"{name or email or f'User {uid}'} (id:{uid})"

def _fetch_users_page(*, limit: int, offset: int):
    """
    Fetch limit+1 so we can detect "has_next" reliably without a total count.
    """
    user_service.api_client.set_token(token)
    items = user_service.get_users(limit=limit + 1, offset=offset) or []
    # normalize any dicts to Pydantic model if needed
    items = [UserResponse.model_validate(x) if isinstance(x, dict) else x for x in items]
    has_next = len(items) > limit
    return items[:limit], has_next

def _fetch_connections_cached():
    """
    Cache connections list in session_state (same as your current behavior).
    """
    if st.session_state.get("connections") is None:
        with st.spinner("Loading connections..."):
            try:
                connection_service.api_client.set_token(token)
                raw = connection_service.get_all_connections()
                conns = [ConnectionResponse.model_validate(r) if isinstance(r, dict) else r for r in (raw or [])]
            except Exception:
                conns = []
            st.session_state.connections = conns
    return st.session_state.connections or []

def _clear_edit_selection():
    st.session_state.pop("_edit_connection", None)
    st.session_state.connections = None
    if "select_edit_connection" in st.session_state:
        st.session_state["select_edit_connection"] = "-- none --"

def _init_wizard_state():
    st.session_state.setdefault("conn_wizard_step", 1)
    st.session_state.setdefault("conn_person1_id", None)
    st.session_state.setdefault("conn_person2_id", None)

def _reset_wizard():
    st.session_state.conn_wizard_step = 1
    st.session_state.conn_person1_id = None
    st.session_state.conn_person2_id = None
    # reset paging widgets to page 1 for both pickers
    for k in (
        "p1_limit", "p1_offset", "p1_selected_id", "p1_widget_version",
        "p2_limit", "p2_offset", "p2_selected_id", "p2_widget_version",
    ):
        st.session_state.pop(k, None)

def paginated_picker(*, title: str, state_prefix: str, exclude_id: int | None = None) -> int | None:
    """
    No search. User navigates pages and selects from current page.
    exclude_id removes a user from the current page list (prevents same-person selection).
    """
    st.session_state.setdefault(f"{state_prefix}_limit", 25)
    st.session_state.setdefault(f"{state_prefix}_offset", 0)
    st.session_state.setdefault(f"{state_prefix}_selected_id", None)
    st.session_state.setdefault(f"{state_prefix}_widget_version", 0)

    limit = st.session_state[f"{state_prefix}_limit"]
    offset = st.session_state[f"{state_prefix}_offset"]

    top1, top2 = st.columns([1, 1])
    with top1:
        new_limit = st.selectbox(
            f"{title}: rows per page",
            [25, 50, 100],
            index=[25, 50, 100].index(limit),
            key=f"{state_prefix}_limit_select",
        )
    with top2:
        page_num = (offset // limit) + 1
        go_to = st.number_input(
            f"{title}: page",
            min_value=1,
            value=page_num,
            step=1,
            key=f"{state_prefix}_page_go",
        )

    # apply limit / page changes
    if new_limit != limit:
        st.session_state[f"{state_prefix}_limit"] = new_limit
        st.session_state[f"{state_prefix}_offset"] = 0
        st.session_state[f"{state_prefix}_selected_id"] = None
        st.session_state[f"{state_prefix}_widget_version"] += 1
        st.rerun()

    desired_offset = (int(go_to) - 1) * st.session_state[f"{state_prefix}_limit"]
    if desired_offset != st.session_state[f"{state_prefix}_offset"]:
        st.session_state[f"{state_prefix}_offset"] = desired_offset
        st.session_state[f"{state_prefix}_selected_id"] = None
        st.session_state[f"{state_prefix}_widget_version"] += 1
        st.rerun()

    # fetch page
    limit = st.session_state[f"{state_prefix}_limit"]
    offset = st.session_state[f"{state_prefix}_offset"]
    users_page, has_next = _fetch_users_page(limit=limit, offset=offset)

    if exclude_id is not None:
        users_page = [u for u in users_page if getattr(u, "id", None) != exclude_id]

    nav1, nav2, nav3 = st.columns([1, 1, 2])
    with nav1:
        if st.button("Previous", key=f"{state_prefix}_prev", disabled=(offset == 0)):
            st.session_state[f"{state_prefix}_offset"] = max(0, offset - limit)
            st.session_state[f"{state_prefix}_selected_id"] = None
            st.session_state[f"{state_prefix}_widget_version"] += 1
            st.rerun()
    with nav2:
        if st.button("Next", key=f"{state_prefix}_next", disabled=(not has_next)):
            st.session_state[f"{state_prefix}_offset"] = offset + limit
            st.session_state[f"{state_prefix}_selected_id"] = None
            st.session_state[f"{state_prefix}_widget_version"] += 1
            st.rerun()
    with nav3:
        st.caption(f"Page {(offset // limit) + 1}")

    options = {_user_label(u): int(getattr(u, "id")) for u in users_page if getattr(u, "id", None) is not None}

    # Important: change widget key when paging changes to avoid stale selection
    widget_key = f"{state_prefix}_select_{st.session_state[f'{state_prefix}_widget_version']}"
    choice = st.selectbox(f"Select {title} (this page)", [""] + list(options.keys()), key=widget_key)

    if choice:
        st.session_state[f"{state_prefix}_selected_id"] = options[choice]

    selected_id = st.session_state.get(f"{state_prefix}_selected_id")
    if selected_id:
        st.success(f"Selected {title}: id={selected_id}")
    else:
        st.info(f"No {title} selected yet.")

    return selected_id

# -----------------------------
# Tabs
# -----------------------------
tab_all, tab_edit, tab_create = st.tabs(["All Connections", "Edit Connection", "Create Connection"])

# =========================================================
# TAB: All Connections
# =========================================================
with tab_all:
    st.markdown("---")
    if st.button("Reload connections"):
        st.session_state.connections = None

    connections = _fetch_connections_cached()

    st.markdown("### All Connections")
    if connections:
        import pandas as pd

        rows = []
        for c in connections:
            # Note: This makes 1 request per row in your current backend design.
            # Consider a backend endpoint that returns names in the list response later.
            try:
                names = connection_service.get_first_last_name_by_connection_id(c.id)
                p1_name = names.user1_full_name if names else None
                p2_name = names.user2_full_name if names else None
            except Exception:
                p1_name = None
                p2_name = None

            rows.append({
                "id": c.id,
                "person1_name": p1_name or f"id:{c.person1_id}",
                "person2_name": p2_name or f"id:{c.person2_id}",
                "relationship": c.relationship,
                "strength": c.strength,
                "last_interaction": c.last_interaction,
                "notes": c.notes,
                "context": c.context,
                "created_at": c.created_at,
                "updated_at": c.updated_at,
            })

        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No connections found. Use the Create Connection tab to add one.")

# =========================================================
# TAB: Edit Connection
# =========================================================
with tab_edit:
    st.markdown("---")
    st.subheader("Edit Connection")

    edit_conn = st.session_state.get("_edit_connection")

    if edit_conn is None:
        connections = _fetch_connections_cached()

        if connections:
            ids = [c.id for c in connections]
            labels = []
            for c in connections:
                try:
                    names = connection_service.get_first_last_name_by_connection_id(c.id)
                    p1 = names.user1_full_name if names else None
                    p2 = names.user2_full_name if names else None
                except Exception:
                    p1 = None
                    p2 = None

                p1_disp = p1 or f"id:{c.person1_id}"
                p2_disp = p2 or f"id:{c.person2_id}"
                labels.append(f"{p1_disp} ↔ {p2_disp} (id:{c.id})")

            sel = st.selectbox("Select connection to edit", ["-- none --"] + labels, key="select_edit_connection")
            if sel != "-- none --":
                idx = labels.index(sel)
                selected_id = ids[idx]
                with st.spinner("Loading connection..."):
                    try:
                        connection_service.api_client.set_token(token)
                        edit_conn = connection_service.get_connection(str(selected_id))
                        st.session_state._edit_connection = edit_conn
                    except Exception:
                        edit_conn = None
        else:
            st.info("No connections available to edit.")

    if edit_conn:
        st.markdown("#### Editing")
        st.json(edit_conn)

        with st.form("edit_connection_form"):
            relationship = st.text_input("Relationship", value=edit_conn.relationship or "")
            strength = st.slider("Strength", min_value=0, max_value=5, value=int(edit_conn.strength or 0), step=1)
            context = st.text_input("Context", value=edit_conn.context or "")
            # If your model returns a date object, this works; if it returns a string, adjust conversion.
            last_interaction = st.date_input("Last interaction", value=edit_conn.last_interaction)
            notes = st.text_area("Notes", value=edit_conn.notes or "")
            submitted = st.form_submit_button("Save")

        if submitted:
            connection_service.api_client.set_token(token)
            payload = ConnectionUpdate(
                relationship=relationship,
                strength=float(strength),
                context=context,
                last_interaction=last_interaction.strftime("%Y-%m-%d"),
                notes=notes,
            )
            with st.spinner("Updating connection..."):
                try:
                    updated = connection_service.update_connection(str(edit_conn.id), payload)
                except Exception:
                    updated = None

            if updated:
                st.success("✅ Connection updated")
                st.session_state.connections = None
                st.session_state._edit_connection = None
                st.rerun()
            else:
                st.error("❌ Failed to update connection")

        st.markdown("---")
        if st.button("Clear edit selection"):
            _clear_edit_selection()
            st.rerun()

        st.markdown("#### Delete Connection")
        if st.button("Delete this connection", key="delete_connection_btn"):
            connection_service.api_client.set_token(token)
            with st.spinner("Deleting connection..."):
                try:
                    deleted = connection_service.delete_connection(str(edit_conn.id))
                except Exception:
                    deleted = False

            if deleted:
                st.success("✅ Connection deleted")
                _clear_edit_selection()
                st.rerun()
            else:
                st.error("❌ Failed to delete connection")

# =========================================================
# TAB: Create Connection (Wizard)
# =========================================================
with tab_create:
    st.markdown("---")
    st.subheader("Create Connection (wizard)")

    _init_wizard_state()
    step = st.session_state.conn_wizard_step

    st.caption(f"Step {step}/3 (no search, paginated selection)")

    # Step 1
    if step == 1:
        st.write("Pick Person 1.")
        p1 = paginated_picker(title="Person 1", state_prefix="p1")
        c1, c2 = st.columns([1, 1])
        with c1:
            if st.button("Next →", disabled=(p1 is None)):
                st.session_state.conn_person1_id = p1
                st.session_state.conn_wizard_step = 2
                st.rerun()
        with c2:
            if st.button("Reset"):
                _reset_wizard()
                st.rerun()

    # Step 2
    elif step == 2:
        p1 = st.session_state.conn_person1_id
        st.write("Pick Person 2 (cannot be the same as Person 1).")
        p2 = paginated_picker(title="Person 2", state_prefix="p2", exclude_id=p1)

        back, next_ = st.columns([1, 1])
        with back:
            if st.button("← Back"):
                st.session_state.conn_wizard_step = 1
                st.rerun()
        with next_:
            if st.button("Next →", disabled=(p2 is None)):
                st.session_state.conn_person2_id = p2
                st.session_state.conn_wizard_step = 3
                st.rerun()

    # Step 3
    else:
        p1 = st.session_state.conn_person1_id
        p2 = st.session_state.conn_person2_id

        if not p1 or not p2 or p1 == p2:
            st.error("Invalid selection. Go back and re-select users.")
            if st.button("← Back to Step 2"):
                st.session_state.conn_wizard_step = 2
                st.rerun()
        else:
            st.write(f"Person 1 id: {p1}")
            st.write(f"Person 2 id: {p2}")

            with st.form("create_connection_form"):
                relationship = st.text_input("Relationship", value="")
                strength = st.slider("Strength", min_value=0, max_value=5, value=3, step=1)
                notes = st.text_area("Notes", value="")
                last_interaction = st.date_input("Last interaction", value=datetime.now().date())
                context = st.text_input("Context", value="")
                submitted = st.form_submit_button("Create connection")

            back, reset = st.columns([1, 1])
            with back:
                if st.button("← Back"):
                    st.session_state.conn_wizard_step = 2
                    st.rerun()
            with reset:
                if st.button("Start over"):
                    _reset_wizard()
                    st.rerun()

            if submitted:
                if int(p1) == int(p2):
                    st.error("Person 1 and Person 2 must be different.")
                else:
                    payload = ConnectionCreate(
                        person1_id=int(p1),
                        person2_id=int(p2),
                        relationship=relationship,
                        strength=strength,
                        context=context,
                        last_interaction=last_interaction.strftime("%Y-%m-%d"),
                        notes=notes,
                    )
                    with st.spinner("Creating connection..."):
                        connection_service.api_client.set_token(token)
                        try:
                            created = connection_service.create_connection(payload)
                        except Exception:
                            created = None

                    if created:
                        st.success("✅ Connection created")
                        st.session_state.connections = None
                        _reset_wizard()
                        st.rerun()
                    else:
                        st.error("❌ Failed to create connection")
