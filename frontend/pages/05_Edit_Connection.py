"""
Connections CRUD Page for SixPaths
Uses standalone functions (requests) to call backend /connections routes.
"""
import os
from datetime import datetime
import requests
import streamlit as st
from styling import apply_custom_css
from api.service_locator import get_connection_service 

st.set_page_config(page_title="Edit Connection - SixPaths", page_icon="✏️", layout="centered")
apply_custom_css()

connection_service = get_connection_service()

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

# with st.sidebar:
#     if st.button("🏠 Home", use_container_width=True):
#         st.switch_page("streamlit_app.py")
#     if st.button("👤 Profile", use_container_width=True):
#         st.switch_page("pages/04_Edit_Profile.py")
#     if st.button("🚪 Logout", use_container_width=True):
#         st.session_state.logged_in = False
#         st.session_state.token = None
#         st.session_state.user_data = None
#         st.switch_page("pages/01_Login.py")

tabs = st.tabs(["My Connections", "Create Connection"])

with tabs[0]:
    st.markdown("---")
    if st.button("Reload connections"):
        st.session_state._connections = None

    connections = st.session_state.get("_connections")
    if connections is None:
        with st.spinner("Loading connections..."):
            try:
                # ensure token on client
                connection_service.api_client.set_token(token)
                connections = connection_service.get_connections_of_user(int(user_id))
            except Exception:
                connections = []
        st.session_state._connections = connections

    st.markdown("### My Connections")

    if connections:
        # show table
        import pandas as pd
        df = pd.DataFrame([{
            'id': c.get('id') or c.get('connection_id'),
            'name': c.get('person_name') or c.get('name') or '',
            'relationship': c.get('relationship'),
            'strength': c.get('strength'),
            'last_interaction': c.get('last_interaction')
        } for c in connections])
        st.dataframe(df, use_container_width=True)

        # selection for details
        ids = [c.get('id') or c.get('connection_id') for c in connections]
        labels = [f"{c.get('person_name') or c.get('name','')} (id:{ids[i]})" for i,c in enumerate(connections)]
        sel = st.selectbox("Select connection to view/edit", ["-- none --"] + labels)
        selected_id = None
        if sel != "-- none --":
            idx = labels.index(sel)
            selected_id = ids[idx]

        if selected_id:
            connection_service.api_client.set_token(token)
            with st.spinner("Loading connection..."):
                try:
                    conn = connection_service.get_connection(str(selected_id))
                except Exception:
                    conn = None

            if conn:
                st.markdown("#### Connection Details")
                st.json(conn)
                if st.button("Edit this connection"):
                    st.session_state._edit_connection = conn
                    st.session_state._connections = None
                if st.button("Delete this connection"):
                    if st.confirmation if hasattr(st, 'confirmation') else True:
                        with st.spinner("Deleting..."):
                            try:
                                ok = connection_service.delete_connection(str(selected_id))
                            except Exception:
                                ok = False
                        if ok:
                            st.success("✅ Connection deleted")
                            st.session_state._connections = None
                        else:
                            st.error("❌ Failed to delete connection")
        else:
            st.info("Select a connection to view details")
    else:
        st.info("No connections found. Use the Create Connection tab to add one.")

with tabs[1]:
    st.markdown("---")
    st.subheader("Create / Edit Connection")

    # if editing state exists, prefill
    edit_conn = st.session_state.get("_edit_connection")

    with st.form("connection_crud_form"):
        col1, col2 = st.columns(2)
        with col1:
            person1_id = st.number_input("Person 1 ID", value=(edit_conn.get("person1_id") if edit_conn else user_id), min_value=1, step=1)
            person2_id = st.number_input("Person 2 ID", value=(edit_conn.get("person2_id") if edit_conn else 0), min_value=0, step=1)
        with col2:
            relationship = st.text_input("Relationship", value=(edit_conn.get("relationship") if edit_conn else ""))
            strength = st.slider("Strength", min_value=0.0, max_value=10.0, value=float(edit_conn.get("strength", 5.0) if edit_conn else 5.0), step=0.5)

        last_interaction = st.date_input("Last interaction", value=(datetime.fromisoformat(edit_conn.get("last_interaction")).date() if edit_conn and edit_conn.get("last_interaction") else datetime.now().date()))
        notes = st.text_area("Notes", value=(edit_conn.get("notes") if edit_conn else ""))
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
        connection_service.api_client.set_token(token)
        if edit_conn and edit_conn.get('id'):
            with st.spinner("Updating connection..."):
                try:
                    updated = connection_service.update_connection(str(edit_conn.get('id')), payload)
                except Exception:
                    updated = None
            if updated:
                st.success("✅ Connection updated")
                st.session_state._connections = None
                st.session_state._edit_connection = None
            else:
                st.error("❌ Failed to update connection")
        else:
            with st.spinner("Creating connection..."):
                try:
                    created = connection_service.create_connection(payload)
                except Exception:
                    created = None
            if created:
                st.success("✅ Connection created")
                st.session_state._connections = None
            else:
                st.error("❌ Failed to create connection")

with st.expander("💡 Connection Tips"):
    st.markdown("""
    - Use numeric IDs for `person1_id` and `person2_id` (or load them from your Users page)
    - `strength` is a float between 0 and 10
    - `last_interaction` should be ISO date (YYYY-MM-DD)
    """)
