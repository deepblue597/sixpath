"""
Dashboard Page — SixPaths (Professional Layout)

- KPI cards (top)
- Sidebar "View settings"
- Network graph in a bordered container
- Right panel: selected person details (reliable alternative to click events)
"""

from __future__ import annotations

import hashlib
import json
import math
import random
import re
import tempfile
from typing import Any, Dict, Optional, Tuple, List

import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network

from styling import apply_custom_css
from frontend.utils import user_label
from models.response_models import UserResponse
from frontend.api.service_locator import (
    get_api_client,
    get_auth_service,
    get_connection_service,
    get_user_service,
)

# -------------------------
# Page setup
# -------------------------
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
try:
    user_service.api_client.set_token(token)
    connection_service.api_client.set_token(token)
except Exception:
    pass

# -------------------------
# Helpers
# -------------------------
def norm_text(val: Optional[str]) -> str:
    return (val or "Unknown").strip()

def norm_key(val: Optional[str]) -> str:
    return norm_text(val).casefold()

def norm_group_key(val: Optional[str]) -> str:
    return re.sub(r"[^a-z0-9_]+", "_", norm_key(val))

def hash_color(s: str) -> str:
    h = int(hashlib.md5(s.encode("utf-8")).hexdigest()[:6], 16)
    return f"#{h:06x}"

def get_sector_color_normalized(sector: Optional[str]) -> Optional[str]:
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

def user_tooltip(u: UserResponse) -> str:
    name = user_label(u)
    username = (getattr(u, "username", "") or "").strip()
    email = (getattr(u, "email", "") or "").strip()
    company = (getattr(u, "company", "") or "").strip()
    sector = (getattr(u, "sector", "") or "").strip()
    subtitle = f"@{username}" if username else ""
    lines = [name, subtitle, company, sector, email]
    return "\n".join([x for x in lines if x])

def kpi_card(title: str, value: str, caption: str = "") -> None:
    st.markdown(
        f"""
        <div class="six-card">
          <div style="font-size:0.85rem;color:#64748B;font-weight:600;">{title}</div>
          <div style="font-size:1.9rem;font-weight:800;color:#0F172A;line-height:1.15;">{value}</div>
          <div class="muted">{caption}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# -------------------------
# Data fetch (cached)
# -------------------------
@st.cache_data(show_spinner=False, ttl=60)
def fetch_current_user() -> Optional[Any]:
    try:
        return auth_service.get_current_user()
    except Exception:
        return None

@st.cache_data(show_spinner=False, ttl=60)
def fetch_all_users() -> List[Any]:
    try:
        return user_service.get_users() or []
    except Exception:
        return []

@st.cache_data(show_spinner=False, ttl=60)
def fetch_connections() -> List[Any]:
    try:
        return connection_service.get_all_connections() or []
    except Exception:
        return []

@st.cache_data(show_spinner=False, ttl=300)
def fetch_filter_options():
    try:
        return user_service.get_companies_sectors()
    except Exception:
        return None

# -------------------------
# Sidebar
# -------------------------
st.sidebar.title("SixPaths")
st.sidebar.caption("Network view settings")

refresh = st.sidebar.button("Refresh data", type="primary", width='stretch')
if refresh:
    fetch_current_user.clear()
    fetch_all_users.clear()
    fetch_connections.clear()
    fetch_filter_options.clear()
    st.rerun()

filter_by = st.sidebar.selectbox("Color / group by", ["None", "Company", "Sector"], index=1)
arrange_groups = st.sidebar.checkbox("Arrange groups into regions", value=False, disabled=(filter_by == "None"))

with st.sidebar.expander("Advanced", expanded=False):
    show_labels = st.checkbox("Show labels", value=True)
    show_legend = st.checkbox("Show legend", value=True)
    graph_height = st.slider("Graph height (px)", 450, 1000, 680, 10)
    physics_enabled = st.checkbox("Physics (force layout)", value=not arrange_groups, disabled=arrange_groups)

# -------------------------
# Main header
# -------------------------
st.title("📊 Network Dashboard")
st.caption("Your professional network at a glance.")

with st.spinner("Loading..."):
    current_user = fetch_current_user()
    all_users = fetch_all_users()
    connections = fetch_connections()
    filter_options = fetch_filter_options()

if not current_user:
    st.error("Failed to load current user. Please login again.")
    st.stop()

# Build users map
users_by_id: Dict[str, Any] = {}
for u in all_users:
    uid = getattr(u, "id", None)
    if uid is not None:
        users_by_id[str(uid)] = u

# KPIs
unique_user_ids = set()
for c in connections:
    a = getattr(c, "person1_id", None)
    b = getattr(c, "person2_id", None)
    if a:
        unique_user_ids.add(int(a))
    if b:
        unique_user_ids.add(int(b))

companies_set = set()
sectors_set = set()
for u in all_users:
    companies_set.add(norm_text(getattr(u, "company", None)))
    sectors_set.add(norm_text(getattr(u, "sector", None)))

k1, k2, k3, k4 = st.columns(4, gap="medium")
with k1:
    kpi_card("Connections", str(len(connections)), "Total edges")
with k2:
    kpi_card("Contacts", str(max(0, len(unique_user_ids) - 1)), "Unique people (excluding you)")
with k3:
    kpi_card("Companies", str(len([c for c in companies_set if c and c != "Unknown"])), "Distinct")
with k4:
    kpi_card("Sectors", str(len([s for s in sectors_set if s and s != "Unknown"])), "Distinct")

st.markdown("---")

# -------------------------
# Build group maps
# -------------------------
group_color_map: Dict[str, str] = {}
group_display_map: Dict[str, str] = {}

if filter_by != "None":
    raw_groups = set()
    for u in all_users:
        raw_groups.add(norm_text(getattr(u, "company" if filter_by == "Company" else "sector", None)))

    for display_name in sorted(raw_groups):
        g_display = display_name or "Unknown"
        gkey = norm_group_key(g_display)
        color = (
            (get_sector_color_normalized(g_display) or hash_color(g_display))
            if filter_by == "Sector"
            else hash_color(g_display)
        )
        group_color_map[gkey] = color
        group_display_map[gkey] = g_display

# Group positions (for arrange_groups)
group_positions: Dict[str, Tuple[int, int]] = {}
if arrange_groups and group_color_map:
    if filter_by == "Sector":
        preset = {
            "technology": (-420, 0),
            "healthcare": (420, 0),
            "finance": (0, -320),
            "education": (-320, -260),
            "marketing": (320, -260),
            "manufacturing": (-320, 260),
        }
        for k, display in group_display_map.items():
            pos = preset.get(display.casefold())
            if pos:
                group_positions[k] = pos
        missing = [k for k in group_color_map.keys() if k not in group_positions]
        r = 360
        for i, k in enumerate(missing):
            angle = 2 * math.pi * i / max(len(missing), 1)
            group_positions[k] = (int(math.cos(angle) * r), int(math.sin(angle) * r))
    else:
        keys = list(group_color_map.keys())
        r = 360
        for i, k in enumerate(keys):
            angle = 2 * math.pi * i / max(len(keys), 1)
            group_positions[k] = (int(math.cos(angle) * r), int(math.sin(angle) * r))

# -------------------------
# Layout: Graph + Details
# -------------------------
left, right = st.columns([3, 2], gap="large")

# ---- Graph ----
with left:
    with st.container(border=True):
        st.subheader("🌐 Network")
        st.caption("Use the selector on the right to view a person’s details.")

        net = Network(height=f"{int(graph_height)}px", width="100%", bgcolor="#ffffff", font_color="#222222")
        net.barnes_hut()

        groups_opts = {
            gkey: {"color": {"background": col, "border": col}}
            for gkey, col in group_color_map.items()
        }

        net.set_options(json.dumps({
            "groups": groups_opts,
            "interaction": {"hover": True},
            "physics": {
                "enabled": bool(physics_enabled) and not arrange_groups,
                "barnesHut": {
                    "gravitationalConstant": -20000,
                    "centralGravity": 0.3,
                    "springLength": 95,
                    "springConstant": 0.04
                },
                "minVelocity": 0.75
            }
        }))

        center_id = str(getattr(current_user, "id"))
        center_company = norm_text(getattr(current_user, "company", None))
        center_sector = norm_text(getattr(current_user, "sector", None))

        center_group = None
        if filter_by == "Company":
            center_group = norm_group_key(center_company)
        elif filter_by == "Sector":
            center_group = norm_group_key(center_sector)

        net.add_node(
            center_id,
            label=user_label(current_user) if show_labels else "",
            title=user_tooltip(current_user),
            color="#1E90FF",
            size=30,
            group=center_group if center_group else None,
        )

        existing_node_ids = {center_id}

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

                node_kwargs = dict(
                    label=label if show_labels else "",
                    title=title,
                    size=size,
                    group=group if group else None,
                )
                if not group:
                    node_kwargs["color"] = node_color

                if arrange_groups and group:
                    gx, gy = group_positions.get(group, (0, 0))
                    node_kwargs["x"] = gx + random.randint(-70, 70)
                    node_kwargs["y"] = gy + random.randint(-70, 70)
                    node_kwargs["fixed"] = {"x": True, "y": True}
                    node_kwargs["physics"] = False

                net.add_node(endpoint, **node_kwargs)
                existing_node_ids.add(endpoint)

            net.add_edge(str(a), str(b), color="#e6e6e6")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp:
            net.write_html(tmp.name, open_browser=False, notebook=False)
            tmp_path = tmp.name

        with open(tmp_path, "r", encoding="utf-8") as f:
            html = f.read()

        # Ensure consistent size for the mynetwork div
        desired_style = f"width: 100%; height: {int(graph_height)}px;"
        html = re.sub(
            r'(<div[^>]+id="mynetwork"[^>]*style=")([^\"]*)("[^>]*>)',
            lambda m: m.group(1) + desired_style + m.group(3),
            html,
            flags=re.IGNORECASE
        )

        components.html(html, height=int(graph_height), scrolling=True)

        if show_legend and filter_by != "None" and group_color_map:
            with st.expander("Legend", expanded=False):
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

# ---- Details panel ----
with right:
    with st.container(border=True):
        st.subheader("Person details")

        # Build a nice selector list (exclude current user)
        selectable_users = [u for u in all_users if u and str(getattr(u, "id", "")) != str(getattr(current_user, "id", ""))]
        options = {user_label(u): str(getattr(u, "id")) for u in selectable_users if getattr(u, "id", None) is not None}

        selected_label = st.selectbox("Select a person", [""] + sorted(options.keys()))
        selected_id = options.get(selected_label) if selected_label else None

        if not selected_id:
            st.info("Select someone to view details and quick actions.")
        else:
            u = users_by_id.get(str(selected_id))
            if not u:
                st.warning("Details not found in the current list.")
            else:
                st.markdown(f"### {user_label(u)}")
                company = norm_text(getattr(u, "company", None))
                sector = norm_text(getattr(u, "sector", None))
                email = (getattr(u, "email", "") or "").strip()
                phone = (getattr(u, "phone", "") or "").strip()
                linkedin = (getattr(u, "linkedin_url", "") or "").strip()

                st.caption(" • ".join([x for x in [company, sector] if x and x != "Unknown"]))

                a, b = st.columns(2)
                with a:
                    st.markdown("**Email**")
                    st.write(email or "—")
                    st.markdown("**Phone**")
                    st.write(phone or "—")
                with b:
                    st.markdown("**Company**")
                    st.write(company if company != "Unknown" else "—")
                    st.markdown("**Sector**")
                    st.write(sector if sector != "Unknown" else "—")

                if linkedin:
                    st.markdown("**LinkedIn**")
                    st.write(linkedin)

                st.divider()
                if st.button("Edit this person", width='stretch'):
                    st.session_state["_selected_user_id"] = str(getattr(u, "id"))
                    st.switch_page("pages/04_Edit_Profile.py")
