"""
Connections Page — SixPaths (clean layout)

Tabs:
- Overview: metrics + connections table (same data)
- Edit: left = select connection, right = edit form + danger zone
- Create: wizard in a card + clear progress

Notes:
- Uses st.container(border=True) to create "cards". [web:720]
- Uses st.columns for two-panel layout. [web:608]
"""

from __future__ import annotations

from datetime import datetime
import streamlit as st
from styling import apply_custom_css

from frontend.api.service_locator import get_connection_service, get_user_service
from models.response_models import UserResponse, ConnectionResponse
from models.input_models import ConnectionCreate, ConnectionUpdate
from frontend.utils import user_label


# -----------------------------
# Setup
# -----------------------------
st.set_page_config(page_title="Connections - SixPaths", page_icon="🔗", layout="wide")
apply_custom_css()

connection_service = get_connection_service()
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

current_user = st.session_state.get("user_data")
if not current_user:
    st.error("Current user not loaded. Please load your profile first.")
    st.stop()

# Ensure services have token
try:
    connection_service.api_client.set_token(token)
    user_service.api_client.set_token(token)
except Exception:
    pass


# -----------------------------
# Helpers (yours + minor additions)
# -----------------------------
def _fetch_users_page(*, limit: int, offset: int):
    """Fetch limit+1 so we can detect 'has_next' without total count."""
    items = user_service.get_users(limit=limit + 1, offset=offset) or []
    items = [UserResponse.model_validate(x) if isinstance(x, dict) else x for x in items]
    has_next = len(items) > limit
    return items[:limit], has_next

def _fetch_connections_cached():
    """Cache connections list in session_state."""
    if st.session_state.get("connections") is None:
        with st.spinner("Loading connections..."):
            try:
                raw = connection_service.get_all_connections()
                conns = [ConnectionResponse.model_validate(r) if isinstance(r, dict) else r for r in (raw or [])]
            except Exception:
                conns = []
            st.session_state.connections = conns
    return st.session_state.connections or []

def _clear_edit_selection():
    st.session_state.pop("_edit_connection", None)
    st.session_state.connections = None
    st.session_state["select_edit_connection"] = "-- none --"

def _init_wizard_state():
    st.session_state.setdefault("conn_wizard_step", 1)
    st.session_state.setdefault("conn_person1_id", None)
    st.session_state.setdefault("conn_person2_id", None)

def _reset_wizard():
    st.session_state.conn_wizard_step = 1
    st.session_state.conn_person1_id = None
    st.session_state.conn_person2_id = None
    for k in (
        "p1_limit", "p1_offset", "p1_selected_id", "p1_widget_version",
        "p2_limit", "p2_offset", "p2_selected_id", "p2_widget_version",
        "p1_limit_select", "p1_page_go",
        "p2_limit_select", "p2_page_go",
    ):
        st.session_state.pop(k, None)

def _kpi_card(title: str, value: str, caption: str = ""):
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

def paginated_picker(*, title: str, state_prefix: str, exclude_id: int | None = None) -> int | None:
    """No search. User navigates pages and selects from current page."""
    st.session_state.setdefault(f"{state_prefix}_limit", 25)
    st.session_state.setdefault(f"{state_prefix}_offset", 0)
    st.session_state.setdefault(f"{state_prefix}_selected_id", None)
    st.session_state.setdefault(f"{state_prefix}_widget_version", 0)

    limit = st.session_state[f"{state_prefix}_limit"]
    offset = st.session_state[f"{state_prefix}_offset"]

    # Controls row
    c1, c2 = st.columns([1, 1])
    with c1:
        new_limit = st.selectbox(
            "Rows per page",
            [25, 50, 100],
            index=[25, 50, 100].index(limit),
            key=f"{state_prefix}_limit_select",
        )
    with c2:
        page_num = (offset // limit) + 1
        go_to = st.number_input("Page", min_value=1, value=page_num, step=1, key=f"{state_prefix}_page_go")

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

    # Fetch page
    limit = st.session_state[f"{state_prefix}_limit"]
    offset = st.session_state[f"{state_prefix}_offset"]
    users_page, has_next = _fetch_users_page(limit=limit, offset=offset)

    if exclude_id is not None:
        users_page = [u for u in users_page if getattr(u, "id", None) != exclude_id]

    # Pager row
    n1, n2, n3 = st.columns([1, 1, 2], vertical_alignment="center")
    with n1:
        if st.button("Previous", key=f"{state_prefix}_prev", width='stretch', disabled=(offset == 0)):
            st.session_state[f"{state_prefix}_offset"] = max(0, offset - limit)
            st.session_state[f"{state_prefix}_selected_id"] = None
            st.session_state[f"{state_prefix}_widget_version"] += 1
            st.rerun()
    with n2:
        if st.button("Next", key=f"{state_prefix}_next", width='stretch', disabled=(not has_next)):
            st.session_state[f"{state_prefix}_offset"] = offset + limit
            st.session_state[f"{state_prefix}_selected_id"] = None
            st.session_state[f"{state_prefix}_widget_version"] += 1
            st.rerun()
    with n3:
        st.caption(f"Page {(offset // limit) + 1}")

    options = {user_label(u): int(getattr(u, "id")) for u in users_page if getattr(u, "id", None) is not None}

    widget_key = f"{state_prefix}_select_{st.session_state[f'{state_prefix}_widget_version']}"
    choice = st.selectbox("Select user (this page)", [""] + list(options.keys()), key=widget_key)

    if choice:
        st.session_state[f"{state_prefix}_selected_id"] = options[choice]

    selected_id = st.session_state.get(f"{state_prefix}_selected_id")
    return selected_id


# -----------------------------
# Header + quick summary
# -----------------------------
st.title("🔗 Connections")
st.caption("Create, edit, and review relationships in your network.")

connections = _fetch_connections_cached()

k1, k2, k3 = st.columns([1, 1, 2], gap="medium")
with k1:
    _kpi_card("Connections", str(len(connections)), "Total relationships")
with k2:
    # very rough count of unique people referenced in edges
    ids = set()
    for c in connections:
        if getattr(c, "person1_id", None): ids.add(int(c.person1_id))
        if getattr(c, "person2_id", None): ids.add(int(c.person2_id))
    _kpi_card("People in graph", str(len(ids)), "Unique user IDs in edges")
with k3:
    with st.container(border=True):
        st.markdown("**Quick actions**")
        a1, a2 = st.columns(2)
        with a1:
            if st.button("Reload connections", width='stretch'):
                st.session_state.connections = None
                st.rerun()
        with a2:
            if st.button("Start new connection", width='stretch'):
                _reset_wizard()
                st.session_state.conn_wizard_step = 1
                st.rerun()

st.divider()


# -----------------------------
# Tabs
# -----------------------------
tab_all, tab_edit, tab_create = st.tabs(["Overview", "Edit", "Create"])


# =========================================================
# TAB: Overview
# =========================================================
with tab_all:
    with st.container(border=True):
        st.subheader("All connections")
        st.caption("Tip: Use the Edit tab to update details or delete a connection.")

        if not connections:
            st.info("No connections found. Use Create to add one.")
        else:
            import pandas as pd

            rows = []
            for c in connections:
                # NOTE: still N+1; keep it behind try/except for now.
                try:
                    names = connection_service.get_first_last_name_by_connection_id(c.id)
                    p1_name = getattr(names, "user1_full_name", None) if names else None
                    p2_name = getattr(names, "user2_full_name", None) if names else None
                except Exception:
                    p1_name, p2_name = None, None

                rows.append({
                    "ID": c.id,
                    "Person 1": p1_name or f"id:{c.person1_id}",
                    "Person 2": p2_name or f"id:{c.person2_id}",
                    "Relationship": c.relationship,
                    "Strength": c.strength,
                    "Last interaction": c.last_interaction,
                    "Context": c.context,
                    "Notes": c.notes,
                })

            st.dataframe(pd.DataFrame(rows), width='stretch', hide_index=True)


# =========================================================
# TAB: Edit (two-panel)
# =========================================================
with tab_edit:
    left, right = st.columns([2, 3], gap="large")

    with left:
        with st.container(border=True):
            st.subheader("Select connection")
            connections = _fetch_connections_cached()

            if not connections:
                st.info("No connections available to edit.")
            else:
                # Build labels (still calls names endpoint; acceptable for now)
                ids = [c.id for c in connections]
                labels = []
                for c in connections:
                    try:
                        names = connection_service.get_first_last_name_by_connection_id(c.id)
                        p1 = getattr(names, "user1_full_name", None) if names else None
                        p2 = getattr(names, "user2_full_name", None) if names else None
                    except Exception:
                        p1, p2 = None, None

                    p1_disp = p1 or f"id:{c.person1_id}"
                    p2_disp = p2 or f"id:{c.person2_id}"
                    labels.append(f"{p1_disp} ↔ {p2_disp} (id:{c.id})")

                sel = st.selectbox("Connection", ["-- none --"] + labels, key="select_edit_connection")
                if sel != "-- none --":
                    idx = labels.index(sel)
                    selected_id = ids[idx]
                    if st.button("Load details", width='stretch'):
                        with st.spinner("Loading connection..."):
                            try:
                                edit_conn = connection_service.get_connection(str(selected_id))
                            except Exception:
                                edit_conn = None
                        st.session_state._edit_connection = edit_conn
                        st.rerun()

                if st.button("Clear selection", width='stretch'):
                    _clear_edit_selection()
                    st.rerun()

    with right:
        with st.container(border=True):
            st.subheader("Details & actions")

            edit_conn = st.session_state.get("_edit_connection")
            if not edit_conn:
                st.info("Select a connection on the left.")
            else:
                # Replace raw st.json with a small summary card
                st.markdown(f"**Connection ID:** {getattr(edit_conn, 'id', '')}")
                st.caption(f"Person1 id: {getattr(edit_conn, 'person1_id', '')}  •  Person2 id: {getattr(edit_conn, 'person2_id', '')}")

                st.divider()

                with st.form("edit_connection_form"):
                    relationship = st.text_input("Relationship", value=getattr(edit_conn, "relationship", "") or "")
                    strength = st.slider("Strength", min_value=0, max_value=5, value=int(getattr(edit_conn, "strength", 0) or 0), step=1)
                    context = st.text_input("Context", value=getattr(edit_conn, "context", "") or "")

                    last_interaction_val = getattr(edit_conn, "last_interaction", None)
                    last_interaction = st.date_input("Last interaction", value=last_interaction_val)
                    notes = st.text_area("Notes", value=getattr(edit_conn, "notes", "") or "")

                    submitted = st.form_submit_button("Save changes", width='stretch')

                if submitted:
                    payload = ConnectionUpdate(
                        relationship=relationship,
                        strength=float(strength),
                        context=context,
                        last_interaction=last_interaction.strftime("%Y-%m-%d"),
                        notes=notes,
                    )
                    with st.spinner("Updating connection..."):
                        try:
                            updated = connection_service.update_connection(str(getattr(edit_conn, "id")), payload)
                        except Exception:
                            updated = None

                    if updated:
                        st.success("Connection updated.")
                        st.session_state.connections = None
                        st.session_state._edit_connection = None
                        st.rerun()
                    else:
                        st.error("Failed to update connection.")

                st.divider()
                st.markdown("### Danger zone")
                confirm = st.checkbox("I understand this will permanently delete this connection.", value=False)
                if st.button("Delete connection", width='stretch', disabled=not confirm):
                    with st.spinner("Deleting..."):
                        try:
                            deleted = connection_service.delete_connection(str(getattr(edit_conn, "id")))
                        except Exception:
                            deleted = False

                    if deleted:
                        st.success("Connection deleted.")
                        _clear_edit_selection()
                        st.rerun()
                    else:
                        st.error("Failed to delete connection.")


# =========================================================
# TAB: Create (wizard in cards)
# =========================================================
with tab_create:
    _init_wizard_state()
    step = st.session_state.conn_wizard_step

    with st.container(border=True):
        st.subheader("Create connection")
        st.caption(f"Step {step}/3")

        # Step 1
        if step == 1:
            st.markdown("### 1) Pick Person 1")
            p1 = paginated_picker(title="Person 1", state_prefix="p1")

            a, b = st.columns(2)
            with a:
                if st.button("Next →", width='stretch', disabled=(p1 is None)):
                    st.session_state.conn_person1_id = p1
                    st.session_state.conn_wizard_step = 2
                    st.rerun()
            with b:
                if st.button("Reset", width='stretch'):
                    _reset_wizard()
                    st.rerun()

        # Step 2
        elif step == 2:
            p1 = st.session_state.conn_person1_id
            st.markdown("### 2) Pick Person 2")
            st.caption("Person 2 cannot be the same as Person 1.")
            p2 = paginated_picker(title="Person 2", state_prefix="p2", exclude_id=p1)

            a, b = st.columns(2)
            with a:
                if st.button("← Back", width='stretch'):
                    st.session_state.conn_wizard_step = 1
                    st.rerun()
            with b:
                if st.button("Next →", width='stretch', disabled=(p2 is None)):
                    st.session_state.conn_person2_id = p2
                    st.session_state.conn_wizard_step = 3
                    st.rerun()

        # Step 3
        else:
            p1 = st.session_state.conn_person1_id
            p2 = st.session_state.conn_person2_id

            if not p1 or not p2 or int(p1) == int(p2):
                st.error("Invalid selection. Go back and re-select users.")
                if st.button("← Back to Step 2", width='stretch'):
                    st.session_state.conn_wizard_step = 2
                    st.rerun()
            else:
                st.markdown("### 3) Fill connection details")

                # Small summary (more professional than raw ids scattered)
                summary = st.columns(2)
                summary[0].metric("Person 1 ID", str(p1))
                summary[1].metric("Person 2 ID", str(p2))

                with st.form("create_connection_form"):
                    relationship = st.text_input("Relationship", value="")
                    strength = st.slider("Strength", min_value=0, max_value=5, value=3, step=1)
                    context = st.text_input("Context", value="")
                    last_interaction = st.date_input("Last interaction", value=datetime.now().date())
                    notes = st.text_area("Notes", value="")
                    submitted = st.form_submit_button("Create connection", width='stretch')

                a, b = st.columns(2)
                with a:
                    if st.button("← Back", width='stretch'):
                        st.session_state.conn_wizard_step = 2
                        st.rerun()
                with b:
                    if st.button("Start over", width='stretch'):
                        _reset_wizard()
                        st.rerun()

                if submitted:
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
                        try:
                            created = connection_service.create_connection(payload)
                        except Exception:
                            created = None

                    if created:
                        st.success("Connection created.")
                        st.session_state.connections = None
                        _reset_wizard()
                        st.rerun()
                    else:
                        st.error("Failed to create connection.")
