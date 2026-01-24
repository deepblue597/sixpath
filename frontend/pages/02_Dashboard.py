"""
Dashboard Page for SixPaths — Network Visualization

Uses PyVis to render a network graph of the current user's connections.
All backend calls are standalone functions using `requests`.
"""
import tempfile
import hashlib
import streamlit as st
from pyvis.network import Network
import streamlit.components.v1 as components
from styling import apply_custom_css
from mock_data import get_sector_color
from frontend.api.service_locator import get_user_service, get_connection_service, get_api_client, get_auth_service

st.set_page_config(page_title="Dashboard - SixPaths", page_icon="📊", layout="wide")
apply_custom_css()

# Backend API calls
api_client = get_api_client()
user_service = get_user_service()
connection_service = get_connection_service()
auth_service = get_auth_service()

if not st.session_state.get("logged_in"):
    st.warning("⚠️ Please login first")
    st.stop()

token = st.session_state.get("token")
if not token:
    st.error("Authentication token missing. Please login.")
    st.stop()

st.title("📊 Network Dashboard")

# Load current user and data (cached in session_state)
if "current_user" not in st.session_state or st.button("🔄 Refresh data"):
    with st.spinner("Loading user and connections..."):
        # ensure token set on API client
        api_client.set_token(token)
        try:
            st.session_state.current_user = auth_service.get_current_user()
        except Exception:
            st.session_state.current_user = None
        try:
            st.session_state.all_users = user_service.get_users()
        except Exception:
            st.session_state.all_users = []
        # Load all connections (so the dashboard can display the full network)
        try:
            print("Loading all connections for dashboard...")
            st.session_state.connections = connection_service.get_all_connections()
        except Exception:
            st.session_state.connections = []

current_user = st.session_state.current_user  # type: ignore
all_users = st.session_state.all_users  # type: ignore

if "connections" not in st.session_state or st.session_state.get("connections") is None:
    st.session_state.connections = connection_service.get_all_connections()

connections = st.session_state.connections  
#print(connections)


# Use direct attribute access on API models (or dict access when needed).
# If a field is missing, fall back to an empty string.

if not current_user:
    st.error("Failed to load current user. Please login again.")
    st.stop()

user_name = (current_user.first_name + ' ' + current_user.last_name).strip() or current_user.email
st.markdown(f"Welcome back, **{user_name}**! Here's your professional network.")

# Sidebar controls removed for now — use defaults
# Default filter/display settings (no filtering, color by sector, show labels)
# sectors = sorted({c.get('sector') for c in connections if c.get('sector')})
# companies = sorted({c.get('company') for c in connections if c.get('company')})
# selected_sectors = None
# selected_companies = None
# color_by = "Sector"
show_labels = True
physics_enabled = True

# Filter connections
# filtered_connections = [c for c in connections if (not selected_sectors or c.get('sector') in selected_sectors) and (not selected_companies or c.get('company') in selected_companies)]

st.markdown("### 🌐 Interactive Network")
st.markdown("**Click a node and then use the selector on the right to edit that user.**")

# Build lookup (use string IDs for consistent matching)
users_by_id = {}
for u in all_users:
    if u is None:
        continue
    # prefer storing the original object (UserResponse) so callers can use attributes

    uid_val = u.id

    if uid_val is not None:
        users_by_id[str(uid_val)] = u

# Build PyVis network
net = Network(height="650px", width="100%", bgcolor="#ffffff", font_color="#222222")
net.barnes_hut()


uid = str(current_user.id) 
username = current_user.username or ''  
first = current_user.first_name or ''
last = current_user.last_name or ''
company = current_user.company or ''
email = current_user.email or ''

center_label = f"{first} {last}".strip() or email
center_title = f"<b>{center_label}</b><br/>{company}<br/>{email}"
net.add_node(uid, label=center_label if show_labels else "", title=center_title, color="#1E90FF", size=30)

# Add nodes and edges for all filtered connections (both endpoints)
existing_node_ids = {str(n.get('id')) for n in net.nodes}
for c in connections:
    a = c.person1_id
    b = c.person2_id
    if not a or not b:
        continue

    # ensure both endpoint nodes exist (use string IDs)
    for endpoint_raw in (a, b):
        endpoint = str(endpoint_raw)
        if endpoint in existing_node_ids:
            continue
        user = users_by_id.get(endpoint)
        if user:
            username = getattr(user, 'username', '')
            first = getattr(user, 'first_name', '')
            last = getattr(user, 'last_name', '')
            email = getattr(user, 'email', '')
            position = getattr(user, 'position', '')
            company = getattr(user, 'company', '')
            sector = getattr(user, 'sector', None) 

            name = username or f"{first} {last}".strip() or email
            # build subtitle safely (prefer @username, else position or company)
            subtitle = ''
            if username:
                subtitle = '@' + username
            else:
                subtitle = position or company or ''
            tooltip = f"<b>{name}</b><br/>{subtitle}<br/>{email}"
            comp = company
        else:
            name = endpoint
            tooltip = f"<b>User ID {endpoint}</b>"
            # sector = c.
            # comp = c.get('company') or 'Unknown'

        # if color_by == "Sector":
        #     node_color = get_sector_color(sector)
        # else:
        color_hash = int(hashlib.md5((comp or 'Unknown').encode()).hexdigest()[:6], 16)
        node_color = f"#{color_hash:06x}"

        size = 30 if endpoint == uid else 12 + c.strength * 1.5
        try:
            net.add_node(endpoint, label=name if show_labels else "", title=tooltip, color=node_color, size=size)
            existing_node_ids.add(endpoint)
        except Exception:
            pass

    # add the edge between endpoints (use a light color, string IDs)
    try:
        net.add_edge(str(a), str(b), color="#e6e6e6")
    except Exception:
        pass

# physics options
net.set_options('''
{
    "physics": {
        "enabled": true,
        "barnesHut": {"gravitationalConstant": -20000, "centralGravity": 0.3, "springLength": 95, "springConstant": 0.04},
        "minVelocity": 0.75
    }
}
''')

# render
with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp:
    # write_html avoids notebook-specific template rendering issues
    net.write_html(tmp.name, open_browser=False, notebook=False)
    tmp_path = tmp.name
with open(tmp_path, 'r', encoding='utf-8') as f:
    html = f.read()


components.html(html, height=650, scrolling=True)

st.markdown('---')
st.markdown("Tip: Click a node in the graph to explore.")
