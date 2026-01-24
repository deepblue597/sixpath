"""
Main Streamlit application entry point.
This is the main file to run the multi-page Streamlit app.

Run with: streamlit run frontend/main.py
"""
import streamlit as st
import os
import sys

# Ensure project root is on sys.path so top-level imports like `models` resolve
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Page configuration - MUST be first Streamlit command
st.set_page_config(
    page_title="SixPaths",
    page_icon="🔗",
    layout="centered",
    initial_sidebar_state='expanded'
)

# # Custom CSS to hide sidebar completely and style buttons
# st.markdown("""
#     <style>
#     /* Hide sidebar */
    
#     /* Full width buttons */
#     .stButton > button {
#         width: 100%;
#     }
    
#     /* Main content padding */
#     .main {
#         padding-top: 2rem;
#     }
    
#     /* Hide default navigation */
#     [data-testid="stSidebarNav"] {
#         display: none;
#     }
#     </style>
# """, unsafe_allow_html=True)

# Define pages
login_page = st.Page(
    page="pages/01_Login.py",
    title="Login",
    icon="🔐",
    default=True
)

# New clean dashboard/home
home_page = st.Page(
    page="pages/02_Dashboard.py",
    title="Home",
    icon="🏠"
)

# New analysis wizard
referral_page = st.Page(
    page="pages/03_Referrals.py",
    title="Referrals",
    icon="➕"
)

# My analyses list
edit_profile_page = st.Page(
    page="pages/04_Edit_Profile.py",
    title="Edit Profile",
    icon="👤"
)

# Results viewer
edit_connections_page = st.Page(
    page="pages/05_Edit_Connection.py",
    title="Edit Connection",
    icon="✏️"
)

# Create navigation with pages (but sidebar is hidden)
pg = st.navigation([
    login_page, 
    home_page, 
    referral_page,
    edit_profile_page,
    edit_connections_page
])

# Run the selected page
pg.run()