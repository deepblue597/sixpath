"""
Dashboard Page for SixPaths — Network Visualization (Streamlit + PyVis)

- Renders a PyVis (vis-network) graph via components.html (HTML embed).
- Supports coloring/grouping by Company or Sector with consistent legend.
- Provides a sidebar selector to jump to an edit page (reliable in Streamlit).
"""
from __future__ import annotations

import hashlib
import json
import tempfile
from typing import Any, Dict, Optional
import re
import math
import random

import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network

from styling import apply_custom_css
from frontend.api.service_locator import (
    get_api_client,
    get_auth_service,
    get_connection_service,
    get_user_service,
)

st.set_page_config(page_title="Dashboard - SixPaths", page_icon="📊", layout="wide")
apply_custom_css()

api_client = get_api_client()
auth_service = get_auth_service()
user_service = get_user_service()
connection_service = get_connection_service()

# -------------------------
# Auth guard
# -------------------------
if not st.session_state.get("logged_in"):
    st.warning("Please login first.")
    st.stop()

token = st.session_state.get("token")
if not token:
    st.error("Authentication token missing. Please login again.")
    st.stop()

api_client.set_token(token)

# -------------------------
# Helpers
# -------------------------
def norm_text(val: Optional[str]) -> str:
    """Normalize keys for matching/grouping."""
    return (val or "Unknown").strip()

def norm_key(val: Optional[str]) -> str:
    return norm_text(val).casefold()

def norm_group_key(val: Optional[str]) -> str:
    """Normalized group key used for vis groups (no spaces, stable)."""
    return re.sub(r"[^a-z0-9_]+", "_", norm_key(val))

def hash_color(s: str) -> str:
    h = int(hashlib.md5(s.encode("utf-8")).hexdigest()[:6], 16)
    return f"#{h:06x}"

def get_sector_color_normalized(sector: Optional[str]) -> Optional[str]:
    """Return a sector color if known; else None so we can fallback to hashing."""
    key = norm_key(sector)
    colors = {
        "technology": "#3B82F6",
        "tech": "#3B82F6",
        "finance": "#10B981",
        "healthcare": "#EF4444",
        "education": "#F59E0B",
        "marketing": "#8B5CF6",
        "manufacturing": "#6B7280",
    }
    return colors.get(key)

def user_label(u: Any) -> str:
    first = (getattr(u, "first_name", "") or "").strip()
    last = (getattr(u, "last_name", "") or "").strip()
    email = (getattr(u, "email", "") or "").strip()
    username = (getattr(u, "username", "") or "").strip()
    full = f"{first} {last}".strip()
    return full or username or email or f"User {getattr(u, 'id', '')}"

def user_tooltip(u: Any) -> str:
    # title supports hover text (HTML is allowed, but keep it simple)
    name = user_label(u)
    username = (getattr(u, "username", "") or "").strip()
    email = (getattr(u, "email", "") or "").strip()
    company = (getattr(u, "company", "") or "").strip()
    sector = (getattr(u, "sector", "") or "").strip()
    subtitle = f"@{username}" if username else ""
    lines = [name, subtitle, company, sector, email]
    return "\n".join([x for x in lines if x])

# -------------------------
# Load data (session cached)
# -------------------------
st.title("📊 Network Dashboard")

if "current_user" not in st.session_state or st.button("🔄 Refresh data"):
    with st.spinner("Loading user and connections..."):
        try:
            st.session_state.current_user = auth_service.get_current_user()
        except Exception:
            st.session_state.current_user = None

        try:
            st.session_state.all_users = user_service.get_users()
        except Exception:
            st.session_state.all_users = []

        try:
            st.session_state.connections = connection_service.get_all_connections()
        except Exception:
            st.session_state.connections = []

current_user = st.session_state.get("current_user")
all_users = st.session_state.get("all_users") or []
if st.session_state.connections is None :
    connections = connection_service.get_all_connections()
else:
    connections = st.session_state.connections

if not current_user:
    st.error("Failed to load current user. Please login again.")
    st.stop()

st.markdown(f"Welcome back, **{user_label(current_user)}**! Here's your professional network.")

# -------------------------
# Filter + coloring controls
# -------------------------
try:
    filter_options = user_service.get_companies_sectors()  # expects .company and .sector lists
except Exception:
    filter_options = None

filter_by = st.sidebar.selectbox("Group / Color By", ["None", "Company", "Sector"], index=1)

companies = []
sectors = []
if filter_options:
    companies = sorted([c for c in (getattr(filter_options, "company", []) or []) if c])
    sectors = sorted([s for s in (getattr(filter_options, "sector", []) or []) if s])

# selected_companies = st.sidebar.multiselect("Filter companies", companies, default=[])
# selected_sectors = st.sidebar.multiselect("Filter sectors", sectors, default=[])

# Build quick lookup for users
users_by_id: Dict[str, Any] = {}
for u in all_users:
    uid = getattr(u, "id", None)
    if uid is not None:
        users_by_id[str(uid)] = u

# # Optional: filter nodes by company/sector (filters apply to user nodes, not edges)
# def include_user(u: Any) -> bool:
#     comp = norm_text(getattr(u, "company", None))
#     sec = norm_text(getattr(u, "sector", None))
#     if selected_companies and comp not in selected_companies:
#         return False
#     if selected_sectors and sec not in selected_sectors:
#         return False
#     return True

# Build group color maps for legend + vis groups
group_color_map: Dict[str, str] = {}
group_display_map: Dict[str, str] = {}

if filter_by != "None":
    # Collect all possible groups from users
    raw_groups = set()
    for u in all_users:
        # if not u or not include_user(u):
        #     continue
        if filter_by == "Company":
            raw_groups.add(norm_text(getattr(u, "company", None)))
        else:
            raw_groups.add(norm_text(getattr(u, "sector", None)))

    for display_name in sorted(raw_groups):
        g_display = display_name or "Unknown"
        gkey = norm_group_key(g_display)
        if filter_by == "Sector":
            c = get_sector_color_normalized(g_display) or hash_color(g_display)
        else:
            c = hash_color(g_display)
        group_color_map[gkey] = c
        group_display_map[gkey] = g_display

# Arrange groups toggle
arrange_groups = False
if filter_by != "None":
    arrange_groups = st.sidebar.checkbox("Arrange groups into regions", value=False)

# Compute group positions when arranging is enabled
group_positions: Dict[str, tuple[float, float]] = {}
if arrange_groups and group_color_map:
    if filter_by == "Sector":
        # prefer human-chosen positions for common sectors
        preset = {
            "technology": (-400, 0),
            "healthcare": (400, 0),
            "finance": (0, -300),
            "education": (-300, -250),
            "marketing": (300, -250),
            "manufacturing": (-300, 250),
        }
        for k, display in group_display_map.items():
            pos = preset.get(display.casefold(), None)
            if pos:
                group_positions[k] = pos
        # any missing sectors: place around circle
        missing = [k for k in group_color_map.keys() if k not in group_positions]
        n = len(missing)
        for i, k in enumerate(missing):
            angle = 2 * math.pi * i / max(n, 1)
            r = 350
            group_positions[k] = (int(math.cos(angle) * r), int(math.sin(angle) * r))
    else:
        # company grouping: spread companies evenly around a circle
        keys = list(group_color_map.keys())
        n = len(keys)
        r = 350
        for i, k in enumerate(keys):
            angle = 2 * math.pi * i / max(n, 1)
            group_positions[k] = (int(math.cos(angle) * r), int(math.sin(angle) * r))

    # # Network sizing controls
    # width_mode = st.sidebar.selectbox("Network width", ["Full width", "Fixed width (px)"], index=0)
    # network_height = st.sidebar.number_input("Network height (px)", min_value=200, max_value=1600, value=650)
    # fixed_width_px = st.sidebar.number_input("Fixed width (px)", min_value=400, max_value=2000, value=1000)

# -------------------------
# Build the network
# -------------------------
st.markdown("### 🌐 Interactive Network")
st.caption("Tip: Use the sidebar selector to jump to the edit page for a person.")

net = Network(height="650px", width="100%", bgcolor="#ffffff", font_color="#222222")
net.barnes_hut()

# Inject vis-network group styling so group colors are consistent
groups_opts = {
    gkey: {
        "color": {
            "background": col,
            "border": col,
            "highlight": {"background": col, "border": col},
            "hover": {"background": col, "border": col},
        }
    }
    for gkey, col in group_color_map.items()
}

physics_enabled = not arrange_groups
net.set_options(json.dumps({
    "groups": groups_opts,
    "interaction": {"hover": True},
    "physics": {
        "enabled": physics_enabled,
        "barnesHut": {
            "gravitationalConstant": -20000,
            "centralGravity": 0.3,
            "springLength": 95,
            "springConstant": 0.04
        },
        "minVelocity": 0.75
    }
}))

# Add current user as center
center_id = str(getattr(current_user, "id"))
center_company = norm_text(getattr(current_user, "company", None))
center_sector = norm_text(getattr(current_user, "sector", None))

center_group_key: Optional[str] = None
if filter_by == "Company":
    center_group_key = norm_key(center_company)
elif filter_by == "Sector":
    center_group_key = norm_key(center_sector)

net.add_node(
    center_id,
    label=user_label(current_user),
    title=user_tooltip(current_user),
    color="#1E90FF",
    size=30,
    group=norm_group_key(center_group_key) if center_group_key else None,
)

existing_node_ids = {center_id}

# Add nodes/edges from connections
for c in connections:
    a = getattr(c, "person1_id", None)
    b = getattr(c, "person2_id", None)
    if not a or not b:
        continue

    for endpoint_raw in (a, b):
        endpoint = str(endpoint_raw)
        if endpoint in existing_node_ids:
            continue

        u = users_by_id.get(endpoint)
        # if u and not include_user(u):
        #     continue

        if u:
            comp = norm_text(getattr(u, "company", None))
            sec = norm_text(getattr(u, "sector", None))
            title = user_tooltip(u)
            label = user_label(u)
        else:
            comp = "Unknown"
            sec = "Unknown"
            title = f"User ID {endpoint}"
            label = endpoint

        if filter_by == "Company":
            gkey = norm_group_key(comp)
            node_color = group_color_map.get(gkey) or hash_color(comp)
            group = gkey
        elif filter_by == "Sector":
            gkey = norm_group_key(sec)
            node_color = group_color_map.get(gkey) or get_sector_color_normalized(sec) or hash_color(sec)
            group = gkey
        else:
            node_color = hash_color(comp)
            group = None

        strength = getattr(c, "strength", None) or 1
        size = 30 if endpoint == center_id else 12 + strength * 1.5

        # If node belongs to a group, let vis.js group styling define the color
        node_kwargs = dict(
            label=label,
            title=title,
            size=size,
            group=group if group else None,
        )
        if not group:
            node_kwargs["color"] = node_color

        # If arranging groups, assign x/y positions clustered around group center
        if arrange_groups and group:
            gx, gy = group_positions.get(group, (0, 0))
            # jitter so nodes don't overlap exactly
            jitter_x = random.randint(-60, 60)
            jitter_y = random.randint(-60, 60)
            node_kwargs["x"] = gx + jitter_x
            node_kwargs["y"] = gy + jitter_y
            node_kwargs["fixed"] = {"x": True, "y": True}
            node_kwargs["physics"] = False

        net.add_node(endpoint, **node_kwargs)
        existing_node_ids.add(endpoint)

    # Add edge
    net.add_edge(str(a), str(b), color="#e6e6e6")

# Render HTML into Streamlit
with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp:
    net.write_html(tmp.name, open_browser=False, notebook=False)
    tmp_path = tmp.name

with open(tmp_path, "r", encoding="utf-8") as f:
    html = f.read()

    # Ensure the PyVis container uses the requested width/height.
    # Look for the div with id that PyVis writes (usually id="mynetwork") and replace its style.
    desired_width = "100%"
    network_height = 650
    desired_style = f"width: {desired_width}; height: {int(network_height)}px;"
    html = re.sub(r'(<div[^>]+id="mynetwork"[^>]*style=")([^\"]*)("[^>]*>)', lambda m: m.group(1) + desired_style + m.group(3), html, flags=re.IGNORECASE)

    components.html(html, height=int(network_height), scrolling=True)

# Legend
if filter_by != "None" and group_color_map:
    st.markdown(f"**Legend — {filter_by} colors**", unsafe_allow_html=True)
    items = []
    for k in sorted(group_display_map.keys(), key=lambda kk: group_display_map[kk]):
        color = group_color_map[k]
        label = group_display_map[k]
        items.append(
            f'<div style="display:inline-block;margin-right:12px;margin-bottom:6px;">'
            f'<span style="display:inline-block;width:14px;height:14px;background:{color};'
            f'border:1px solid #ccc;margin-right:6px;vertical-align:middle;"></span>'
            f'{label}</div>'
        )
    st.markdown("<div>" + "".join(items) + "</div>", unsafe_allow_html=True)

# # Reliable navigation to edit page (Streamlit-safe)
# editable_users = [u for u in all_users if u and str(getattr(u, "id", "")) != center_id]
# choices = {user_label(u): str(getattr(u, "id")) for u in editable_users}
# selected_name = st.sidebar.selectbox("Edit a person", [""] + sorted(choices.keys()))
# if selected_name:
#     st.session_state["selected_user_id"] = choices[selected_name]
#     if st.sidebar.button("Go to edit page"):
#         st.switch_page("pages/05_Edit_Connection.py")
