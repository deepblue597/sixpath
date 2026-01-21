"""
SixPaths - Professional Networking Visualization App
Main entry point for the Streamlit application
"""
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="SixPaths",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'selected_node_id' not in st.session_state:
    st.session_state.selected_node_id = None
if 'user_data' not in st.session_state:
    st.session_state.user_data = None
if 'connections' not in st.session_state:
    st.session_state.connections = None
if 'referrals' not in st.session_state:
    st.session_state.referrals = None

# Apply custom CSS
from utils.styling import apply_custom_css
apply_custom_css()

# Check if user is logged in
if not st.session_state.logged_in:
    st.switch_page("pages/01_Login.py")
else:
    # Welcome message
    st.title("🔗 Welcome to SixPaths")
    
    # Get user name
    user_name = st.session_state.username
    if st.session_state.get('user_data'):
        first_name = st.session_state.user_data.get('first_name', '')
        last_name = st.session_state.user_data.get('last_name', '')
        if first_name or last_name:
            user_name = f"{first_name} {last_name}".strip()
    
    st.markdown(f"### Hello, {user_name}!")
    
    st.markdown("""
    SixPaths is your professional networking visualization tool. 
    
    **Quick Navigation:**
    - 📊 **Dashboard**: Visualize your network connections
    - 🎯 **Referrals**: Manage incoming referrals
    - 👤 **Profile**: Edit your profile information
    - ✏️ **Edit Connection**: Modify connection details
    
    Use the sidebar to navigate between pages.
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Go to Dashboard", use_container_width=True):
            st.switch_page("pages/02_Dashboard.py")
    
    with col2:
        if st.button("🎯 View Referrals", use_container_width=True):
            st.switch_page("pages/03_Referrals.py")
    
    with col3:
        if st.button("👤 Edit Profile", use_container_width=True):
            st.switch_page("pages/04_Edit_Profile.py")
    
    st.divider()
    
    # Quick stats
    if st.session_state.connections:
        st.markdown("### 📈 Quick Stats")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Connections", len(st.session_state.connections))
        
        with col2:
            sectors = set(c['sector'] for c in st.session_state.connections)
            st.metric("Sectors", len(sectors))
        
        with col3:
            if st.session_state.referrals:
                st.metric("Active Referrals", len(st.session_state.referrals))
            else:
                st.metric("Active Referrals", 0)
        
        with col4:
            recent = sum(1 for c in st.session_state.connections 
                        if c.get('last_interaction') and str(c.get('last_interaction', '')).startswith('2026'))
            st.metric("Recent Interactions", recent)
