"""
Connections CRUD Page for SixPaths
Uses standalone functions (requests) to call backend /connections routes.
"""
import os
from datetime import datetime
import time
import requests
import streamlit as st
from styling import apply_custom_css
from frontend.api.service_locator import get_connection_service , get_user_service
from models.response_models import UserResponse , ConnectionResponse
from models.input_models import ConnectionCreate , ConnectionUpdate
st.set_page_config(page_title="Edit Connection - SixPaths", page_icon="✏️", layout="centered")
apply_custom_css()

connection_service = get_connection_service()
user_service = get_user_service()

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

user_id = current_user.id

# Load users for dropdowns (cache in session to reduce API calls)
users_list = st.session_state.get('_users_for_conn')
if users_list is None:
    with st.spinner("Loading users for dropdowns..."):
        try:
            user_service.api_client.set_token(token)
            raw_users = user_service.get_users()
            users_list = [UserResponse.model_validate(u) if isinstance(u, dict) else u for u in (raw_users or [])]
        except Exception:
            users_list = []
    st.session_state._users_for_conn = users_list
st.title("✏️ Edit Connection")

# Helper: robust rerun that works across Streamlit versions
def safe_rerun():
    try:
        st.rerun()
    except Exception:
        # Fallback: toggle a query param to force a rerun
        try:
            params = st.query_params()
            params["_ts"] = str(time.time())
            st.experimental_set_query_params(**params)
        except Exception:
            # As a last resort, toggle a session-state flag and stop
            st.session_state.__rerun = not st.session_state.get("__rerun", False)
            st.stop()


def _clear_edit_and_rerun():
    # remove the selected edit connection and refresh UI
    st.session_state.pop('_edit_connection', None)
    # also clear cached connections so lists refresh
    st.session_state.pop('connections', None)
    # Reset the selectbox state so the UI returns to the default selection
    if 'select_edit_connection' in st.session_state:
        st.session_state['select_edit_connection'] = "-- none --"
    # Do NOT call rerun from a callback; Streamlit will re-run the script
    # automatically after the callback finishes.
    return None

# with st.sidebar:
#     if st.button("🏠 Home", width='stretch'):
#         st.switch_page("streamlit_app.py")
#     if st.button("👤 Profile", width='stretch'):
#         st.switch_page("pages/04_Edit_Profile.py")
#     if st.button("🚪 Logout", width='stretch'):
#         st.session_state.logged_in = False
#         st.session_state.token = None
#         st.session_state.user_data = None
#         st.switch_page("pages/01_Login.py")

# Create three tabs: All Connections, Edit Connection, Create Connection
tab_all, tab_edit, tab_create = st.tabs(["All Connections", "Edit Connection", "Create Connection"])

with tab_all:
    st.markdown("---")
    if st.button("Reload connections"):
        st.session_state.connections = None

    connections = st.session_state.connections
    if connections is None:
        with st.spinner("Loading connections..."):
            try:
                connection_service.api_client.set_token(token)
                raw = connection_service.get_all_connections()
                connections = [ConnectionResponse.model_validate(r) if isinstance(r, dict) else r for r in (raw or [])]
            except Exception:
                connections = []
        st.session_state.connections = connections

    st.markdown("### All Connections")
    if connections:
        import pandas as pd
        df = pd.DataFrame([{
            'id': c.id,
            'person1_id': c.person1_id,
            'person2_id': c.person2_id,
            'relationship': c.relationship,
            'strength': c.strength,
            'last_interaction': c.last_interaction,
            'notes': c.notes,
            'created_at': c.created_at,
            'updated_at': c.updated_at
            # 'id': c.get('id') or c.get('connection_id'),
            # 'name': c.get('person_name') or c.get('name') or '',
            # 'relationship': c.get('relationship'),
            # 'strength': c.get('strength'),
            # 'last_interaction': c.get('last_interaction')
        } for c in connections])
        st.dataframe(df, width='stretch')

        ids = [c.id for c in connections]
        #labels = [f"{c.get('person_name') or c.get('name','')} (id:{ids[i]})" for i,c in enumerate(connections)]
    else:
        st.info("No connections found. Use the Create Connection tab to add one.")

with tab_edit:
    st.markdown("---")
    st.subheader("Edit Connection")
    # allow selecting a connection to edit, or use session_state._edit_connection if set
    edit_conn = st.session_state.get('_edit_connection')
    if edit_conn is None:
        # let user pick which connection to edit
        connections = st.session_state.get('connections')
        if connections is None:
            with st.spinner("Loading connections..."):
                try:
                    connection_service.api_client.set_token(token)
                    connections = connection_service.get_all_connections()
                except Exception:
                    connections = []
                st.session_state.connections = connections

        if connections:
            ids = [c.id for c in connections]
            labels = [f"{c.person1_id} (id:{ids[i]})" for i,c in enumerate(connections)]
            sel = st.selectbox("Select connection to edit", ["-- none --"] + labels, key="select_edit_connection")
            if sel != "-- none --":
                idx = labels.index(sel)
                selected_id = ids[idx]
                with st.spinner("Loading connection..."):
                    try:
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
            relationship = st.text_input("Relationship", value = edit_conn.relationship)
            strength = st.slider("Strength", min_value=0 , max_value=5, value=edit_conn.strength, step=1)
            context = st.text_input("Context", value = edit_conn.context)
            last_interaction = st.date_input("Last interaction", value = edit_conn.last_interaction )
            notes = st.text_area("Notes", value = edit_conn.notes)
            submitted = st.form_submit_button("Save")
        # with st.form("edit_connection_form"):
        #     col1, col2 = st.columns(2)
 
        #     # person1_id = st.number_input("Person 1 ID", value=(edit_conn.get('person1_id') if isinstance(edit_conn, dict) else getattr(edit_conn, 'person1_id', user_id)), min_value=1, step=1)
        #     # person2_id = st.number_input("Person 2 ID", value=(edit_conn.get('person2_id') if isinstance(edit_conn, dict) else getattr(edit_conn, 'person2_id', 0)), min_value=0, step=1)
        #     with col2:
        #         relationship = st.text_input("Relationship", value=(edit_conn.get('relationship') if isinstance(edit_conn, dict) else getattr(edit_conn, 'relationship', '')))
        #         strength = st.slider("Strength", min_value=0.0, max_value=10.0, value=edit_conn.get('strength') if isinstance(edit_conn, dict) else getattr(edit_conn, 'strength', 5.0) or 5.0, step=0.5)

        #     notes = st.text_area("Notes", value=(edit_conn.get('notes') if isinstance(edit_conn, dict) else getattr(edit_conn, 'notes', '')))
        #     submitted = st.form_submit_button("Save")
        
        if submitted:
            # if person1_id == person2_id:
            #     st.error("Person 1 and Person 2 must be different")
            # else:
            connection_service.api_client.set_token(token)
            conn_id = edit_conn.id
            payload = ConnectionUpdate(
                relationship=relationship,
                strength=float(strength),
                context=context,
                last_interaction=last_interaction.strftime("%Y-%m-%d"), # type: ignore
                notes=notes
            )
            with st.spinner("Updating connection..."):
                try:
                    updated = connection_service.update_connection(str(conn_id), payload)
                except Exception:
                    updated = None
            if updated:
                st.success("✅ Connection updated")
                st.session_state.connections = None
                st.session_state._edit_connection = None
            else:
                st.error("❌ Failed to update connection")
    st.markdown("---")
    st.button("Clear edit selection", on_click=_clear_edit_and_rerun)
    
    st.markdown("#### Delete Connection")
    if edit_conn:
        delete_submitted = st.button("Delete this connection", key="delete_connection_btn")
        if delete_submitted:
            connection_service.api_client.set_token(token)
            conn_id = edit_conn.id
            with st.spinner("Deleting connection..."):
                try:
                    deleted = connection_service.delete_connection(str(conn_id))
                    _clear_edit_and_rerun()
                except Exception:
                    deleted = False
            if deleted:
                st.success("✅ Connection deleted")
                st.session_state.connections = None
                st.session_state._edit_connection = None
            else:
                st.error("❌ Failed to delete connection")
           

with tab_create:
    st.markdown("---")
    st.subheader("Create Connection")
    col1, col2 = st.columns(2)
    with col1:
        if users_list:
            names = []
            ids = {}
            for u in users_list:
                name = ((getattr(u, 'first_name', '') or '') + ' ' + (getattr(u, 'last_name', '') or '')).strip()
                if not name:
                    name = getattr(u, 'email', '') or f"id:{getattr(u, 'id', '')}"
                names.append(name)
                ids[name] = u.id

            # try:
            #     p1_idx = ids.index(user_id)
            # except Exception:
            #     p1_idx = 0
            person1_label = st.selectbox("Person 1", names)
            person1_id = ids[person1_label]
            #print("Selected person1_id:", person1_label)
            
            p2_labels = [name for name in names if ids[name] != person1_id]
            person2_label = st.selectbox("Person 2", p2_labels)
            person2_id = ids[person2_label]
        else:
            person1_id = st.number_input("Person 1 ID", value=user_id, min_value=1, step=1)
            person2_id = st.number_input("Person 2 ID", value=0, min_value=0, step=1)
        with col2:
            relationship = st.text_input("Relationship", value="")
            strength = st.slider("Strength", min_value=0, max_value=5, value=5, step=1)

        last_interaction = st.date_input("Last interaction", value=datetime.now().date())
        notes = st.text_area("Notes", value="")
        submitted = st.button("Create")
        

    if submitted:
        if person1_id == person2_id:
            st.error("Person 1 and Person 2 must be different")
        connection_service.api_client.set_token(token)
        with st.spinner("Creating connection..."):
            payload = ConnectionCreate(
                person1_id=person1_id,
                person2_id=person2_id,
                relationship=relationship,
                strength=strength,
                context="",
                last_interaction=last_interaction.strftime("%Y-%m-%d"),
                notes=notes
            )
            try:
                created = connection_service.create_connection(payload)
            except Exception:
                created = None
        if created:
            st.success("✅ Connection created")
            st.session_state.connections = None
        else:
            st.error("❌ Failed to create connection")

with st.expander("💡 Connection Tips"):
    st.markdown("""
    - Use numeric IDs for `person1_id` and `person2_id` (or load them from your Users page)
    - `strength` is a float between 0 and 10
    - `last_interaction` should be ISO date (YYYY-MM-DD)
    """)
