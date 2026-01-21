"""
Connections CRUD Page for SixPaths
Uses standalone functions (requests) to call backend /connections routes.
"""
import os
from datetime import datetime
import requests
import streamlit as st
from styling import apply_custom_css

st.set_page_config(page_title="Edit Connection - SixPaths", page_icon="✏️", layout="centered")
apply_custom_css()

def _get_api_base() -> str:
    try:
        return st.secrets.get("API_BASE_URL") or os.getenv("API_BASE_URL", "http://localhost:8000")
    except Exception:
        return os.getenv("API_BASE_URL", "http://localhost:8000")

def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

def get_connection(connection_id: int, token: str) -> dict | None:
    url = _get_api_base().rstrip("/") + f"/connections/{connection_id}"
    try:
        resp = requests.get(url, headers=_auth_headers(token), timeout=6)
        if resp.status_code == 200:
            return resp.json()
    except requests.RequestException:
        pass
    return None

def get_connections_for_user(user_id: int, token: str) -> list[dict]:
    url = _get_api_base().rstrip("/") + f"/connections/user/{user_id}"
    try:
        resp = requests.get(url, headers=_auth_headers(token), timeout=8)
        if resp.status_code == 200:
            return resp.json()
    except requests.RequestException:
        pass
    return []

def create_connection(payload: dict, token: str) -> dict | None:
    url = _get_api_base().rstrip("/") + "/connections"
    try:
        resp = requests.post(url, headers=_auth_headers(token), json=payload, timeout=8)
        if resp.status_code in (200, 201):
            return resp.json()
    except requests.RequestException:
        pass
    return None

def update_connection(connection_id: int, payload: dict, token: str) -> dict | None:
    url = _get_api_base().rstrip("/") + f"/connections/{connection_id}"
    try:
        resp = requests.put(url, headers=_auth_headers(token), json=payload, timeout=8)
        if resp.status_code in (200, 201):
            return resp.json()
    except requests.RequestException:
        pass
    return None

def delete_connection(connection_id: int, token: str) -> bool:
    url = _get_api_base().rstrip("/") + f"/connections/{connection_id}"
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
    st.error("Authentication token missing. Please login.")
    st.stop()

current_user = st.session_state.get("user_data")
if not current_user:
    st.error("Current user not loaded. Please load your profile first.")
    st.stop()

user_id = current_user.get("id")

st.title("✏️ Edit Connection")

with st.sidebar:
    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("streamlit_app.py")
    if st.button("👤 Profile", use_container_width=True):
        st.switch_page("pages/04_Edit_Profile.py")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.token = None
        st.session_state.user_data = None
        st.switch_page("pages/01_Login.py")

st.markdown("### My Connections")

if st.button("Reload connections"):
    st.session_state._connections = None

connections = st.session_state.get("_connections")
if connections is None:
    with st.spinner("Loading connections..."):
        connections = get_connections_for_user(user_id, token)
    st.session_state._connections = connections

if connections:
    # Build display labels
    options = []
    for c in connections:
        cid = c.get("connection_id") or c.get("id") or c.get("connectionId")
        label = f"{c.get('person_name', c.get('name', ''))} (conn:{cid})"
        options.append((label, cid))

    labels = [o[0] for o in options]
    selected_label = st.selectbox("Select connection to edit", ["-- New Connection --"] + labels)
    selected_id = None
    if selected_label != "-- New Connection --":
        idx = labels.index(selected_label)
        selected_id = options[idx][1]

else:
    st.info("No connections found. Create one below.")
    selected_label = "-- New Connection --"
    selected_id = None

st.markdown("---")

if selected_id:
    with st.spinner("Loading connection..."):
        conn = get_connection(selected_id, token)
else:
    conn = None

st.subheader("Create / Edit Connection")

with st.form("connection_crud_form"):
    col1, col2 = st.columns(2)
    with col1:
        person1_id = st.number_input("Person 1 ID", value=(conn.get("person1_id") if conn else user_id), min_value=1, step=1)
        person2_id = st.number_input("Person 2 ID", value=(conn.get("person2_id") if conn else 0), min_value=0, step=1)
    with col2:
        relationship = st.text_input("Relationship", value=(conn.get("relationship") if conn else ""))
        # Constrain strength to match DB check constraint (max 6 to avoid violations)
        strength = st.slider("Strength", min_value=0.0, max_value=6.0, value=float(conn.get("strength", 5.0) if conn else 5.0), step=0.5)

    last_interaction = st.date_input("Last interaction", value=(datetime.fromisoformat(conn.get("last_interaction")).date() if conn and conn.get("last_interaction") else datetime.now().date()))
    notes = st.text_area("Notes", value=(conn.get("notes") if conn else ""))
    submitted = st.form_submit_button("Save")

if submitted:
    payload = {
        "person1_id": int(person1_id),
        "person2_id": int(person2_id),
        "relationship": relationship,
        "strength": float(strength),
        "context": "",
        "last_interaction": last_interaction.strftime("%Y-%m-%d"),
        "notes": notes,
    }
    if conn and selected_id:
        with st.spinner("Updating connection..."):
            updated = update_connection(selected_id, payload, token)
        if updated:
            st.success("✅ Connection updated")
            st.session_state._connections = None
        else:
            st.error("❌ Failed to update connection")
    else:
        with st.spinner("Creating connection..."):
            created = create_connection(payload, token)
        if created:
            st.success("✅ Connection created")
            st.session_state._connections = None
        else:
            st.error("❌ Failed to create connection")

st.markdown("---")

st.subheader("Delete Connection")
if conn and selected_id:
    if st.checkbox("Confirm deletion of this connection"):
        if st.button("Delete connection"):
            with st.spinner("Deleting..."):
                ok = delete_connection(selected_id, token)
            if ok:
                st.success("✅ Connection deleted")
                st.session_state._connections = None
            else:
                st.error("❌ Failed to delete connection")

st.markdown("---")

st.markdown("### Connections Snapshot")
if connections:
    # show a simplified table
    display_rows = []
    for c in connections:
        display_rows.append({
            "connection_id": c.get("connection_id") or c.get("id"),
            "person1_id": c.get("person1_id"),
            "person2_id": c.get("person2_id"),
            "relationship": c.get("relationship"),
            "strength": c.get("strength"),
            "last_interaction": c.get("last_interaction"),
        })
    st.table(display_rows)
else:
    st.info("No connections to display")

with st.expander("💡 Connection Tips"):
    st.markdown("""
    - Use numeric IDs for `person1_id` and `person2_id` (or load them from your Users page)
    - `strength` is a float between 0 and 10
    - `last_interaction` should be ISO date (YYYY-MM-DD)
    """)
