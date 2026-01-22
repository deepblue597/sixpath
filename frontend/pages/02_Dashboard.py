"""
Dashboard Page for SixPaths — Network Visualization

Uses PyVis to render a network graph of the current user's connections.
All backend calls are standalone functions using `requests`.
"""
import os
import tempfile
import hashlib
from typing import List, Optional
import requests
import streamlit as st
from pyvis.network import Network
import streamlit.components.v1 as components
from styling import apply_custom_css
from mock_data import get_sector_color
from api.service_locator import get_user_service, get_connection_service, get_api_client, get_auth_service

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
        if st.session_state.current_user:
            try:
                st.session_state.connections = connection_service.get_connections_of_user(int(st.session_state.current_user.get("id")))
            except Exception:
                st.session_state.connections = []

current_user = st.session_state.get("current_user")
all_users = st.session_state.get("all_users") or []
connections = st.session_state.get("connections") or []

if not current_user:
    st.error("Failed to load current user. Please login again.")
    st.stop()

# Display greeting
user_name = current_user.get("first_name", "") + (" " + current_user.get("last_name", "") if current_user.get("last_name") else "")
user_name = user_name.strip() or current_user.get("email", "User")
st.markdown(f"Welcome back, **{user_name}**! Here's your professional network.")

# Sidebar controls
with st.sidebar:
    st.markdown("### 🎛️ Network Controls")
    # Filters
    sectors = sorted({c.get('sector') for c in connections if c.get('sector')})
    companies = sorted({c.get('company') for c in connections if c.get('company')})
    selected_sectors = st.multiselect("Filter by Sector", options=sectors, default=sectors)
    selected_companies = st.multiselect("Filter by Company", options=companies, default=companies)
    color_by = st.radio("Color nodes by", options=["Sector", "Company"], index=0)
    show_labels = st.checkbox("Show labels", value=True)
    physics_enabled = st.checkbox("Enable physics", value=True)

    # st.divider()
    # st.markdown("### 🧭 Navigation")
    # if st.button("👥 Manage Users", use_container_width=True):
    #     st.switch_page("pages/update_user.py")
    # if st.button("🎯 Referrals", use_container_width=True):
    #     st.switch_page("pages/03_Referrals.py")
    # if st.button("👤 My Profile", use_container_width=True):
    #     st.switch_page("pages/04_Edit_Profile.py")
    # st.divider()
    # if st.button("🚪 Logout", use_container_width=True):
    #     st.session_state.logged_in = False
    #     st.session_state.token = None
    #     st.session_state.user_data = None
    #     st.session_state.connections = None
    #     st.switch_page("pages/01_Login.py")

# Filter connections
filtered_connections = [c for c in connections if (not selected_sectors or c.get('sector') in selected_sectors) and (not selected_companies or c.get('company') in selected_companies)]

st.markdown("### 🌐 Interactive Network")
st.markdown("**Click a node and then use the selector on the right to edit that user.**")

# Build lookup
users_by_id = {u.get('id'): u for u in all_users}

# Build PyVis network
net = Network(height="650px", width="100%", bgcolor="#ffffff", font_color="#222222")
net.barnes_hut()

# center node
uid = current_user.get("id")
center_label = f"{current_user.get('first_name','')} {current_user.get('last_name','')}".strip() or current_user.get('email')
center_title = f"<b>{center_label}</b><br/>{current_user.get('company','')}<br/>{current_user.get('email','')}"
net.add_node(uid, label=center_label if show_labels else "", title=center_title, color="#1E90FF", size=30)

# add connected nodes
for c in filtered_connections:
    p1 = c.get('person1_id')
    p2 = c.get('person2_id')
    other = None
    if p1 == uid:
        other = p2
    elif p2 == uid:
        other = p1
    else:
        # include both endpoints if neither equals current user
        other = p1 or p2
    if not other:
        continue
    other_user = users_by_id.get(other)
    if other_user:
        name = f"{other_user.get('first_name','')} {other_user.get('last_name','') }".strip() or other_user.get('email')
        tooltip = f"<b>{name}</b><br/>{other_user.get('position','') or other_user.get('company','')}<br/>{other_user.get('email','')}"
    else:
        name = str(other)
        tooltip = f"<b>User ID {other}</b>"

    # color
    if color_by == "Sector":
        node_color = get_sector_color(c.get('sector', 'Other'))
    else:
        comp = c.get('company', 'Unknown') or 'Unknown'
        color_hash = int(hashlib.md5(comp.encode()).hexdigest()[:6], 16)
        node_color = f"#{color_hash:06x}"

    size = 12 + (c.get('relationship_strength', 5) * 1.5)
    if other not in [n.get('id') for n in net.nodes]:
        net.add_node(other, label=name if show_labels else "", title=tooltip, color=node_color, size=size)
    try:
        net.add_edge(uid, other)
    except Exception:
        pass

# attempt to add edges between connected users when data present
seen = set()
for c in connections:
    a = c.get('person1_id')
    b = c.get('person2_id')
    if not a or not b:
        continue
    pair = tuple(sorted((a,b)))
    if pair in seen:
        continue
    seen.add(pair)
    if a in users_by_id and b in users_by_id:
        try:
            net.add_edge(a,b, color="#e6e6e6")
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

col_main, col_side = st.columns([3,1])
with col_main:
    components.html(html, height=650, scrolling=True)

with col_side:
    st.markdown("### Nodes")
    node_list = []
    for node in net.nodes:
        nid = node.get('id')
        lbl = node.get('label') or str(nid)
        node_list.append((f"{lbl} (id:{nid})", nid))
    if node_list:
        labels = [n[0] for n in node_list]
        choice = st.selectbox("Select node", labels)
        chosen = node_list[labels.index(choice)][1]
        selected_user = users_by_id.get(chosen)
        if selected_user:
            st.markdown(f"**Name:** {selected_user.get('first_name','')} {selected_user.get('last_name','')}")
            st.markdown(f"**Company:** {selected_user.get('company','') or '—'}")
            st.markdown(f"**Email:** {selected_user.get('email','') or '—'}")
        else:
            st.markdown(f"**Node ID:** {chosen}")
        if st.button("Edit user (open Edit Connection page)"):
            st.session_state.selected_node_id = chosen
            st.switch_page("pages/05_Edit_Connection.py")
    else:
        st.info("No nodes available")

st.markdown('---')
st.markdown("Tip: Click a node in the graph to explore. Use the selector to jump to the Edit page.")
