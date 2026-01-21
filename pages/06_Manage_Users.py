"""
User Management Page for SixPaths
View and edit all users in the system
"""
import streamlit as st
import pandas as pd
from utils.styling import apply_custom_css
from api.api_client import get_api_client

# Page configuration
st.set_page_config(
    page_title="Manage Users - SixPaths",
    page_icon="👥",
    layout="wide"
)

apply_custom_css()

# Check authentication
if not st.session_state.get('logged_in', False):
    st.warning("⚠️ Please login first")
    st.switch_page("pages/01_Login.py")

# Page header
st.title("👥 User Management")
st.markdown("View and manage all users in your network")

# Sidebar navigation
with st.sidebar:
    st.markdown("### 🧭 Navigation")
    
    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("streamlit_app.py")
    
    if st.button("📊 Dashboard", use_container_width=True):
        st.switch_page("pages/02_Dashboard.py")
    
    if st.button("🎯 Referrals", use_container_width=True):
        st.switch_page("pages/03_Referrals.py")
    
    if st.button("👤 My Profile", use_container_width=True):
        st.switch_page("pages/04_Edit_Profile.py")
    
    st.divider()
    
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.switch_page("pages/01_Login.py")

# Initialize API client
api_client = get_api_client()

# Load all users
if 'all_users' not in st.session_state or st.button("🔄 Refresh Users"):
    try:
        # Get all users from backend
        # Note: You may need to add a get_all_users() method to your API client
        # For now, we'll use the connections which include user data
        all_users_response = api_client.get_all_users() if hasattr(api_client, 'get_all_users') else []
        
        if not all_users_response and st.session_state.get('connections'):
            # Fallback: extract unique users from connections
            users_dict = {}
            for conn in st.session_state.connections:
                user_id = conn.get('id')
                if user_id and user_id not in users_dict:
                    users_dict[user_id] = {
                        'id': user_id,
                        'name': conn.get('name', ''),
                        'email': conn.get('email', ''),
                        'phone': conn.get('phone', ''),
                        'company': conn.get('company', ''),
                        'position': conn.get('position', ''),
                        'sector': conn.get('sector', ''),
                        'linkedin_url': conn.get('linkedin', '')
                    }
            all_users_response = list(users_dict.values())
        
        st.session_state.all_users = all_users_response
        st.success("✅ Users loaded successfully!")
    except Exception as e:
        st.error(f"❌ Error loading users: {str(e)}")
        st.session_state.all_users = []

# Main content
if st.session_state.get('all_users'):
    users = st.session_state.all_users
    
    # Summary metrics
    st.markdown("### 📊 User Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Users", len(users))
    
    with col2:
        sectors = set(u.get('sector', 'Unknown') for u in users if u.get('sector'))
        st.metric("Sectors", len(sectors))
    
    with col3:
        companies = set(u.get('company', 'Unknown') for u in users if u.get('company'))
        st.metric("Companies", len(companies))
    
    with col4:
        current_user_id = st.session_state.get('user_id')
        other_users = [u for u in users if u.get('id') != current_user_id]
        st.metric("Other Users", len(other_users))
    
    st.divider()
    
    # Filters
    st.markdown("### 🔍 Filters")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Sector filter
        all_sectors = sorted(set(u.get('sector', 'Unknown') for u in users if u.get('sector')))
        selected_sectors = st.multiselect(
            "Sector",
            options=all_sectors,
            default=all_sectors
        )
    
    with col2:
        # Company filter
        all_companies = sorted(set(u.get('company', 'Unknown') for u in users if u.get('company')))
        selected_companies = st.multiselect(
            "Company",
            options=all_companies,
            default=all_companies
        )
    
    with col3:
        # Search
        search_query = st.text_input("🔍 Search users", placeholder="Search by name, email, company...")
    
    st.divider()
    
    # Filter users
    filtered_users = [
        u for u in users
        if (not selected_sectors or u.get('sector', 'Unknown') in selected_sectors)
        and (not selected_companies or u.get('company', 'Unknown') in selected_companies)
    ]
    
    # Apply search
    if search_query:
        search_lower = search_query.lower()
        filtered_users = [
            u for u in filtered_users
            if search_lower in u.get('name', '').lower()
            or search_lower in u.get('email', '').lower()
            or search_lower in u.get('company', '').lower()
            or search_lower in u.get('position', '').lower()
        ]
    
    # Display users
    st.markdown(f"### 📋 Users ({len(filtered_users)} found)")
    
    if filtered_users:
        # Create table view
        df = pd.DataFrame([{
            "ID": u['id'],
            "Name": u.get('name', 'Unknown'),
            "Email": u.get('email', ''),
            "Company": u.get('company', ''),
            "Position": u.get('position', ''),
            "Sector": u.get('sector', 'Unknown')
        } for u in filtered_users])
        
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )
        
        # Edit user section
        st.divider()
        st.markdown("### ✏️ Edit User")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Select user to edit
            user_options = {f"{u.get('name', 'Unknown')} ({u.get('company', 'N/A')})": u['id'] for u in filtered_users}
            selected_user_display = st.selectbox(
                "Select User to Edit",
                options=list(user_options.keys())
            )
            selected_user_id = user_options[selected_user_display]
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("✏️ Edit Selected User", use_container_width=True, type="primary"):
                # Store the selected user ID and navigate to edit page
                selected_user = next((u for u in filtered_users if u['id'] == selected_user_id), None)
                if selected_user:
                    st.session_state.editing_user_id = selected_user_id
                    st.session_state.editing_user_data = selected_user
                    st.rerun()
        
        # Edit form (shown when a user is selected)
        if st.session_state.get('editing_user_id'):
            editing_user = st.session_state.get('editing_user_data', {})
            
            with st.form("edit_user_form"):
                st.markdown(f"#### Editing: {editing_user.get('name', 'Unknown')}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Split name into first and last
                    full_name = editing_user.get('name', '')
                    name_parts = full_name.split(' ', 1)
                    first_name = st.text_input(
                        "First Name *",
                        value=name_parts[0] if name_parts else '',
                        placeholder="John"
                    )
                    last_name = st.text_input(
                        "Last Name *",
                        value=name_parts[1] if len(name_parts) > 1 else '',
                        placeholder="Doe"
                    )
                    
                    email = st.text_input(
                        "Email",
                        value=editing_user.get('email', ''),
                        placeholder="john.doe@company.com"
                    )
                    
                    phone = st.text_input(
                        "Phone",
                        value=editing_user.get('phone', ''),
                        placeholder="+1 (555) 123-4567"
                    )
                
                with col2:
                    company = st.text_input(
                        "Company *",
                        value=editing_user.get('company', ''),
                        placeholder="TechCorp"
                    )
                    
                    position = st.text_input(
                        "Position",
                        value=editing_user.get('position', ''),
                        placeholder="Software Engineer"
                    )
                    
                    sector_options = ["Technology", "Finance", "Healthcare", "Education", "Manufacturing", "Retail", "Other"]
                    current_sector = editing_user.get('sector', 'Technology')
                    sector = st.selectbox(
                        "Sector *",
                        options=sector_options,
                        index=sector_options.index(current_sector) if current_sector in sector_options else 0
                    )
                    
                    linkedin_url = st.text_input(
                        "LinkedIn URL",
                        value=editing_user.get('linkedin_url', ''),
                        placeholder="https://linkedin.com/in/johndoe"
                    )
                
                # Form buttons
                col1, col2 = st.columns(2)
                
                with col1:
                    submitted = st.form_submit_button("💾 Save Changes", use_container_width=True, type="primary")
                
                with col2:
                    cancelled = st.form_submit_button("❌ Cancel", use_container_width=True)
                
                if submitted:
                    # Validate required fields
                    if not first_name or not last_name or not company:
                        st.error("⚠️ Please fill in all required fields (marked with *)")
                    else:
                        try:
                            # Prepare user data
                            user_data = {
                                "first_name": first_name,
                                "last_name": last_name,
                                "email": email or "",
                                "phone": phone or "",
                                "company": company,
                                "position": position or "",
                                "sector": sector,
                                "linkedin_url": linkedin_url or ""
                            }
                            
                            # Update user via API
                            response = api_client.update_user(st.session_state.editing_user_id, user_data)
                            st.success(f"✅ User {first_name} {last_name} updated successfully!")
                            
                            # Clear editing state and refresh users
                            st.session_state.editing_user_id = None
                            st.session_state.editing_user_data = None
                            
                            # Refresh all users
                            if hasattr(api_client, 'get_all_users'):
                                st.session_state.all_users = api_client.get_all_users()
                            
                            # Refresh connections if the current user was updated
                            if st.session_state.editing_user_id == st.session_state.get('user_id'):
                                user_id = st.session_state.get('user_id')
                                if user_id:
                                    connections_response = api_client.get_my_connections_with_users()
                                    st.session_state.connections = connections_response
                            
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"❌ Error updating user: {str(e)}")
                
                if cancelled:
                    st.session_state.editing_user_id = None
                    st.session_state.editing_user_data = None
                    st.rerun()
    
    else:
        st.info("No users match your current filters")

else:
    st.warning("No users available. Click 'Refresh Users' to load users.")
    if st.button("Go to Dashboard"):
        st.switch_page("pages/02_Dashboard.py")
