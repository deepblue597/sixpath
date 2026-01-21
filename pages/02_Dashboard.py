"""
Dashboard Page for SixPaths
Interactive network visualization with filters and metrics
"""
import streamlit as st
from pyvis.network import Network
import pandas as pd
import tempfile
import streamlit.components.v1 as components
from utils.styling import apply_custom_css
from utils.mock_data import get_sector_color
from api.api_client import get_api_client

# Page configuration
st.set_page_config(
    page_title="Dashboard - SixPaths",
    page_icon="📊",
    layout="wide"
)

apply_custom_css()

# Check authentication
if not st.session_state.get('logged_in', False):
    st.warning("⚠️ Please login first")
    st.switch_page("pages/01_Login.py")

# Page header
st.title("📊 Network Dashboard")

# Display user name properly
user_name = st.session_state.username
if st.session_state.get('user_data'):
    first_name = st.session_state.user_data.get('first_name', '')
    last_name = st.session_state.user_data.get('last_name', '')
    if first_name or last_name:
        user_name = f"{first_name} {last_name}".strip()

st.markdown(f"Welcome back, **{user_name}**! Here's your professional network.")

# Refresh data button
col_title, col_refresh = st.columns([5, 1])
with col_refresh:
    if st.button("🔄 Refresh", use_container_width=True):
        api_client = get_api_client()
        with st.spinner("Refreshing data..."):
            st.session_state.connections = api_client.get_my_connections_with_users()
            st.session_state.referrals = api_client.get_my_referrals_with_users()
        st.success("✅ Data refreshed!")
        st.rerun()

# Sidebar controls
with st.sidebar:
    st.markdown("### 🎛️ Network Controls")
    
    # Filters
    st.markdown("#### Filters")
    
    # Sector filter
    if st.session_state.connections:
        all_sectors = sorted(set(c['sector'] for c in st.session_state.connections))
        selected_sectors = st.multiselect(
            "Filter by Sector",
            options=all_sectors,
            default=all_sectors,
            help="Select sectors to display"
        )
        
        # Company filter
        all_companies = sorted(set(c['company'] for c in st.session_state.connections))
        selected_companies = st.multiselect(
            "Filter by Company",
            options=all_companies,
            default=all_companies,
            help="Select companies to display"
        )
        
        # Visualization settings
        st.markdown("#### Visualization")
        
        color_by = st.radio(
            "Color nodes by",
            options=["Sector", "Company"],
            help="Choose how to color-code the network nodes"
        )
        
        show_labels = st.checkbox("Show labels", value=True)
        
        physics_enabled = st.checkbox("Enable physics", value=True, 
                                     help="Enable force-directed layout")
        
        # Navigation
        st.divider()
        st.markdown("### 🧭 Navigation")
        
        if st.button("👥 Manage Users", use_container_width=True):
            st.switch_page("pages/06_Manage_Users.py")
        
        if st.button("🎯 Referrals", use_container_width=True):
            st.switch_page("pages/03_Referrals.py")
        
        if st.button("👤 My Profile", use_container_width=True):
            st.switch_page("pages/04_Edit_Profile.py")
        
        # Logout button
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.user_data = None
            st.session_state.connections = None
            st.session_state.referrals = None
            st.switch_page("pages/01_Login.py")

# Main content
if st.session_state.connections:
    # Filter connections based on selection
    filtered_connections = [
        c for c in st.session_state.connections
        if c.get('sector') in selected_sectors and c.get('company') in selected_companies
    ]
    
    # Show connection count
    if len(filtered_connections) != len(st.session_state.connections):
        st.info(f"📊 Showing {len(filtered_connections)} of {len(st.session_state.connections)} connections (filtered)")
    
    # Metrics row
    st.markdown("### 📈 Network Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Connections",
            len(filtered_connections),
            delta=f"{len(filtered_connections) - len(st.session_state.connections) + len(filtered_connections)} filtered"
        )
    
    with col2:
        sectors = set(c['sector'] for c in filtered_connections)
        st.metric("Active Sectors", len(sectors))
    
    with col3:
        # Recent interactions (last 30 days)
        from datetime import datetime, timedelta
        cutoff = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        recent = sum(1 for c in filtered_connections if c.get('last_interaction') and str(c.get('last_interaction', '')) >= cutoff)
        st.metric("Recent Interactions", recent, delta="Last 30 days")
    
    with col4:
        # Average relationship strength
        avg_strength = sum(c.get('relationship_strength', 0) for c in filtered_connections) / len(filtered_connections) if filtered_connections else 0
        st.metric("Avg. Strength", f"{avg_strength:.1f}/10")
    
    st.divider()
    
    # Network visualization
    st.markdown("### 🌐 Interactive Network")
    st.markdown("**Click on any node** to view and edit connection details")
    
    # Create network graph
    net = Network(
        height="600px",
        width="100%",
        bgcolor="#F8FAFC",
        font_color="#1E293B"
    )
    
    # Configure physics
    if physics_enabled:
        net.set_options("""
        {
            "physics": {
                "enabled": true,
                "forceAtlas2Based": {
                    "gravitationalConstant": -50,
                    "centralGravity": 0.01,
                    "springLength": 200,
                    "springConstant": 0.08
                },
                "solver": "forceAtlas2Based",
                "stabilization": {
                    "enabled": true,
                    "iterations": 100
                }
            },
            "interaction": {
                "hover": true,
                "navigationButtons": true,
                "tooltipDelay": 200
            }
        }
        """)
    else:
        net.set_options('{"physics": {"enabled": false}}')
    
    # Add central node (user)
    net.add_node(
        1,
        label=user_name if show_labels else "",
        title=f"{user_name}\n{st.session_state.user_data.get('company', 'User')}",
        color="#F59E0B",  # Gold for user
        size=30,
        shape="dot",
        font={"size": 16, "color": "#1E293B", "face": "arial", "bold": True}
    )
    
    # Add connection nodes
    for conn in filtered_connections:
        # Determine node color
        if color_by == "Sector":
            node_color = get_sector_color(conn.get('sector', 'Other'))
        else:
            # Generate consistent color for company
            import hashlib
            company = conn.get('company', 'Unknown')
            color_hash = int(hashlib.md5(company.encode()).hexdigest()[:6], 16)
            node_color = f"#{color_hash:06x}"
        
        # Node size based on relationship strength
        node_size = 10 + (conn.get('relationship_strength', 5) * 1.5)
        
        # Add node
        net.add_node(
            conn.get('id'),
            label=conn.get('name', 'Unknown') if show_labels else "",
            title=f"{conn.get('name', 'Unknown')}\n{conn.get('position', 'N/A')}\n{conn.get('company', 'N/A')}\n{conn.get('sector', 'N/A')}\nStrength: {conn.get('relationship_strength', 'N/A')}",
            color=node_color,
            size=node_size,
            shape="dot",
            font={"size": 12, "color": "#1E293B"}
        )
        
        # Add edge from user to connection
        edge_width = conn.get('relationship_strength', 5) / 2
        net.add_edge(
            1,
            conn.get('id'),
            width=edge_width,
            color={"color": node_color, "opacity": 0.4}
        )
    
    # Save and display network
    try:
        # Generate HTML
        html_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode='w')
        net.save_graph(html_file.name)
        html_file.close()
        
        # Read and display
        with open(html_file.name, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Display the network (without click handler for now - will use table below instead)
        components.html(html_content, height=620, scrolling=False)
        
        st.info("💡 **Tip:** Click on a connection in the table below to edit")
        
    except Exception as e:
        st.error(f"Error rendering network: {str(e)}")
    
    # Legend
    st.markdown("### 🎨 Legend")
    legend_cols = st.columns(len(selected_sectors) if color_by == "Sector" else 3)
    
    if color_by == "Sector":
        for idx, sector in enumerate(selected_sectors):
            with legend_cols[idx]:
                color = get_sector_color(sector)
                st.markdown(
                    f'<div style="display: flex; align-items: center;">'
                    f'<div style="width: 20px; height: 20px; background-color: {color}; '
                    f'border-radius: 50%; margin-right: 8px;"></div>'
                    f'<span>{sector}</span></div>',
                    unsafe_allow_html=True
                )
    else:
        st.info("Companies are color-coded automatically")
    
    st.divider()
    
    # Connection table
    st.markdown("### 📋 Connection List")
    
    # Create DataFrame
    df_data = []
    for c in filtered_connections:
        df_data.append({
            "ID": c.get('id'),
            "Name": c.get('name', 'Unknown'),
            "Company": c.get('company', 'N/A'),
            "Sector": c.get('sector', 'N/A'),
            "Position": c.get('position', 'N/A'),
            "Last Interaction": c.get('last_interaction', 'N/A'),
            "Strength": c.get('relationship_strength', 0)
        })
    
    df = pd.DataFrame(df_data)
    
    # Add search
    search = st.text_input("🔍 Search connections", placeholder="Type to filter...")
    
    if search:
        df = df[df.apply(lambda row: search.lower() in row.to_string().lower(), axis=1)]
        filtered_connections = [c for c in filtered_connections if str(c.get('id')) in df['ID'].astype(str).values]
    
    # Display table with clickable rows via index selection
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "ID": st.column_config.NumberColumn("ID", help="User ID"),
            "Strength": st.column_config.ProgressColumn(
                "Strength",
                format="%.1f",
                min_value=0,
                max_value=10,
            )
        }
    )
    
    # Add edit buttons for each connection
    st.markdown("#### ✏️ Edit Connection")
    
    # Create columns for connection selection
    num_cols = min(4, len(filtered_connections))
    if num_cols > 0:
        cols = st.columns(num_cols)
        
        for idx, conn in enumerate(filtered_connections[:8]):  # Show first 8
            with cols[idx % num_cols]:
                if st.button(f"✏️ {conn.get('name', 'Unknown')}", key=f"edit_{conn.get('id')}", use_container_width=True):
                    st.session_state.selected_node_id = conn.get('id')
                    st.switch_page("pages/05_Edit_Connection.py")
    
    # Quick actions
    st.markdown("### ⚡ Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🎯 View Referrals", use_container_width=True):
            st.switch_page("pages/03_Referrals.py")
    
    with col2:
        if st.button("👤 Edit Profile", use_container_width=True):
            st.switch_page("pages/04_Edit_Profile.py")
    
    with col3:
        if st.button("➕ Add Connection", use_container_width=True):
            st.session_state.selected_node_id = None
            st.switch_page("pages/05_Edit_Connection.py")

else:
    st.warning("No connections found. Please login again to generate sample data.")
