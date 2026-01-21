"""
Edit Connection Page for SixPaths
Edit or add connection details
"""
import streamlit as st
from utils.styling import apply_custom_css
from api.api_client import get_api_client
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Edit Connection - SixPaths",
    page_icon="✏️",
    layout="centered"
)

apply_custom_css()

# Check authentication
if not st.session_state.get('logged_in', False):
    st.warning("⚠️ Please login first")
    st.switch_page("pages/01_Login.py")

# Page header
st.title("✏️ Edit Connection")

# Sidebar navigation
with st.sidebar:
    st.markdown("### 🧭 Navigation")
    
    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("streamlit_app.py")
    
    if st.button("📊 Dashboard", use_container_width=True):
        st.switch_page("pages/02_Dashboard.py")
    
    if st.button("🎯 Referrals", use_container_width=True):
        st.switch_page("pages/03_Referrals.py")
    
    if st.button("👤 Profile", use_container_width=True):
        st.switch_page("pages/04_Edit_Profile.py")
    
    st.divider()
    
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.switch_page("pages/01_Login.py")

# Main content
# Find selected connection by user ID (the person clicked in the network)
selected_connection = None
is_new_connection = False

# Debug info (can be removed in production)
with st.expander("🔍 Debug Info", expanded=False):
    st.write(f"Selected Node ID: {st.session_state.selected_node_id}")
    st.write(f"Total Connections: {len(st.session_state.connections) if st.session_state.connections else 0}")
    if st.session_state.connections and len(st.session_state.connections) > 0:
        st.write("Connection IDs:", [c.get('id') for c in st.session_state.connections[:5]])
        st.write("First connection sample:", st.session_state.connections[0])

if st.session_state.selected_node_id:
    # The selected_node_id is the USER ID that was clicked in the network
    # We need to find the connection data for this user
    if st.session_state.connections:
        # Look for the connection where the clicked user ID matches
        # The 'id' field in our transformed connections is the user ID
        selected_connection = next(
            (c for c in st.session_state.connections if c.get('id') == st.session_state.selected_node_id),
            None
        )
    
    if selected_connection:
        st.markdown(f"Editing connection: **{selected_connection.get('name', 'Unknown')}**")
    else:
        st.warning(f"⚠️ Connection not found for user ID {st.session_state.selected_node_id}. Creating new connection instead.")
        is_new_connection = True
else:
    # Creating new connection
    is_new_connection = True
    st.markdown("**Adding a new connection**")

st.divider()

# Initialize form with existing data or defaults
if selected_connection:
    default_name = selected_connection.get('name', '')
    default_email = selected_connection.get('email', '')
    default_phone = selected_connection.get('phone', '')
    default_company = selected_connection.get('company', '')
    default_position = selected_connection.get('position', '')
    default_sector = selected_connection.get('sector', 'Technology')
    default_linkedin = selected_connection.get('linkedin', '')
    default_how_i_know = selected_connection.get('how_i_know_them', '')
    default_notes = selected_connection.get('notes', '')
    default_last_interaction = selected_connection.get('last_interaction', datetime.now().strftime("%Y-%m-%d"))
    default_strength = float(selected_connection.get('relationship_strength', 5.0))
else:
    default_name = ''
    default_email = ''
    default_phone = ''
    default_company = ''
    default_position = ''
    default_sector = 'Technology'
    default_linkedin = ''
    default_how_i_know = ''
    default_notes = ''
    default_last_interaction = datetime.now().strftime("%Y-%m-%d")
    default_strength = 5.0

# Edit form
with st.form("connection_form", clear_on_submit=False):
    # Option to create connection between any two users
    st.markdown("### 🔗 Connection Between")
    
    # Checkbox to enable creating connection between other users
    create_between_others = st.checkbox(
        "Create connection between other users (not involving me)",
        value=False,
        help="Check this to create a connection between any two users in your network"
    )
    
    person1_id = None
    person2_id = None
    
    if create_between_others:
        st.info("Select two users to create a connection between them")
        
        # Get all users for selection
        api_client = get_api_client()
        try:
            # Try to get all users
            if not st.session_state.get('all_users_for_connection'):
                all_users = api_client.get_all_users()
                st.session_state.all_users_for_connection = all_users
            else:
                all_users = st.session_state.all_users_for_connection
            
            if all_users:
                col1, col2 = st.columns(2)
                
                with col1:
                    user1_options = {
                        f"{u.get('first_name', '')} {u.get('last_name', '')} ({u.get('company', 'N/A')})": u['id']
                        for u in all_users
                    }
                    selected_user1 = st.selectbox(
                        "Person 1 *",
                        options=list(user1_options.keys()),
                        help="Select the first person in the connection"
                    )
                    person1_id = user1_options[selected_user1]
                
                with col2:
                    # Filter out person1 from person2 options
                    user2_options = {
                        f"{u.get('first_name', '')} {u.get('last_name', '')} ({u.get('company', 'N/A')})": u['id']
                        for u in all_users
                        if u['id'] != person1_id
                    }
                    selected_user2 = st.selectbox(
                        "Person 2 *",
                        options=list(user2_options.keys()),
                        help="Select the second person in the connection"
                    )
                    person2_id = user2_options[selected_user2]
                
                st.markdown("---")
            else:
                st.warning("No users available. Please load users first.")
        except Exception as e:
            st.warning(f"Could not load users: {str(e)}. You can still create a new user connection.")
    
    # Only show user detail fields if NOT creating between others
    if not create_between_others:
        st.markdown("### 📝 Basic Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input(
                "Full Name *",
                value=default_name,
                placeholder="Jane Smith",
                help="Contact's full name"
            )
            
            email = st.text_input(
                "Email",
                value=default_email,
                placeholder="jane.smith@company.com",
                help="Contact's email address"
            )
            
            phone = st.text_input(
                "Phone",
                value=default_phone,
                placeholder="+1 (555) 987-6543",
                help="Contact's phone number"
            )
        
        with col2:
            company = st.text_input(
                "Company *",
                value=default_company,
                placeholder="TechCorp",
                help="Contact's current company"
            )
            
            position = st.text_input(
                "Position",
                value=default_position,
                placeholder="Senior Engineer",
                help="Contact's job title"
            )
            
            sector = st.selectbox(
                "Sector *",
                options=["Technology", "Finance", "Healthcare", "Education", "Marketing", "Manufacturing", "Other"],
                index=["Technology", "Finance", "Healthcare", "Education", "Marketing", "Manufacturing", "Other"].index(
                    default_sector
                ) if default_sector in ["Technology", "Finance", "Healthcare", "Education", "Marketing", "Manufacturing", "Other"] else 0,
                help="Contact's industry sector"
            )
        
        linkedin = st.text_input(
            "LinkedIn Profile",
            value=default_linkedin,
            placeholder="linkedin.com/in/janesmith",
            help="Contact's LinkedIn profile URL"
        )
    else:
        # Set defaults when creating between existing users
        name = ""
        email = ""
        phone = ""
        company = ""
        position = ""
        sector = "Technology"
        linkedin = ""
    
    st.markdown("### 🤝 Relationship Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        how_i_know_them = st.text_input(
            "How I Know Them",
            value=default_how_i_know,
            placeholder="Met at conference, Former colleague, etc.",
            help="How you met or know this person"
        )
        
        relationship_strength = st.slider(
            "Relationship Strength",
            min_value=1.0,
            max_value=10.0,
            value=default_strength,
            step=0.5,
            help="Rate the strength of your relationship (1=weak, 10=very strong)"
        )
    
    with col2:
        last_interaction = st.date_input(
            "Last Interaction",
            value=datetime.strptime(default_last_interaction, "%Y-%m-%d") if default_last_interaction else datetime.now(),
            help="When did you last interact with this person?"
        )
    
    notes = st.text_area(
        "Notes",
        value=default_notes,
        placeholder="Add any notes about this connection...",
        help="Additional notes or context about this connection",
        height=150
    )
    
    st.markdown("<small>* Required fields</small>", unsafe_allow_html=True)
    
    st.divider()
    
    # Form action buttons
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if not is_new_connection and selected_connection:
            delete_button = st.form_submit_button("🗑️ Delete", use_container_width=True)
        else:
            delete_button = False
    
    with col2:
        st.markdown("")
    
    with col3:
        cancel_button = st.form_submit_button("❌ Cancel", use_container_width=True)
    
    with col4:
        submit_button = st.form_submit_button("💾 Save", use_container_width=True, type="primary")

# Handle form submission
if submit_button:
    # Validation
    errors = []
    
    if create_between_others and (not person1_id or not person2_id):
        errors.append("Please select both Person 1 and Person 2")
    elif not create_between_others:
        # Only validate name/company when not creating between existing users
        if not name or len(name.strip()) < 2:
            errors.append("Name must be at least 2 characters")
        
        if not company or len(company.strip()) < 2:
            errors.append("Company is required")
        
        if email and '@' not in email:
            errors.append("Invalid email format")
    
    if errors:
        for error in errors:
            st.error(f"❌ {error}")
    else:
        api_client = get_api_client()
        
        # Determine the connection participants
        current_user_id = st.session_state.user_data.get('id')
        
        if create_between_others:
            # Creating connection between two other users
            connection_person1_id = person1_id
            connection_person2_id = person2_id
            
            # No need to create new users, just create the connection
            connection_api_data = {
                'person1_id': connection_person1_id,
                'person2_id': connection_person2_id,
                'relationship': how_i_know_them.strip() if how_i_know_them else '',
                'strength': relationship_strength,
                'context': '',
                'last_interaction': last_interaction.strftime("%Y-%m-%d"),
                'notes': notes.strip() if notes else ''
            }
            
            with st.spinner("Creating connection..."):
                response = api_client.create_connection(connection_api_data)
                
                if response:
                    st.success(f"✅ Connection created successfully!")
                    
                    # Refresh connections from backend
                    user_id = st.session_state.get('user_id')
                    if user_id:
                        connections_response = api_client.get_my_connections_with_users()
                        st.session_state.connections = connections_response
                    
                    # Clear selection and return to dashboard
                    st.session_state.selected_node_id = None
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Failed to create connection")
        else:
            # Original flow: creating connection with current user
            # Split name into first and last
            name_parts = name.strip().split(' ', 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ''
            
            # Prepare user data for API
            user_data = {
                'first_name': first_name,
                'last_name': last_name,
                'email': email.strip() if email else '',
                'phone': phone.strip() if phone else '',
                'company': company.strip(),
                'sector': sector,
                'linkedin_url': linkedin.strip() if linkedin else '',
                'how_i_know_them': how_i_know_them.strip() if how_i_know_them else '',
                'when_i_met_them': last_interaction.strftime("%Y-%m-%d"),
                'notes': notes.strip() if notes else ''
            }
            
            if is_new_connection or not selected_connection:
                # Create new user first
                with st.spinner("Creating new contact..."):
                    new_user = api_client.register(user_data)
                    
                    if new_user:
                        new_user_id = new_user.get('id')
                        
                        # Create connection between current user and new user
                        connection_api_data = {
                            'person1_id': current_user_id,
                            'person2_id': new_user_id,
                            'relationship': how_i_know_them.strip() if how_i_know_them else '',
                            'strength': relationship_strength,
                            'context': '',
                            'last_interaction': last_interaction.strftime("%Y-%m-%d"),
                            'notes': notes.strip() if notes else ''
                        }
                    
                        created_connection = api_client.create_connection(connection_api_data)
                        
                        if created_connection:
                            st.success(f"✅ Added new connection: {name}")
                            st.balloons()
                            
                            # Refresh connections from backend
                            st.session_state.connections = api_client.get_my_connections_with_users()
                        else:
                            st.error("❌ Failed to create connection relationship")
                    else:
                        st.error("❌ Failed to create new contact")
            else:
                # Update existing user and connection
                user_id = selected_connection.get('id')
                connection_id = selected_connection.get('connection_id')
                
                with st.spinner("Updating connection..."):
                    # Update user info
                    updated_user = api_client.update_user(user_id, user_data)
                    
                    if updated_user and connection_id:
                        # Update connection relationship
                        connection_update = {
                            'relationship': how_i_know_them.strip() if how_i_know_them else '',
                            'strength': relationship_strength,
                            'context': '',
                            'last_interaction': last_interaction.strftime("%Y-%m-%d"),
                            'notes': notes.strip() if notes else ''
                        }
                        
                        updated_connection = api_client.update_connection(connection_id, connection_update)
                        
                        if updated_connection:
                            st.success(f"✅ Updated connection: {name}")
                            
                            # Refresh connections from backend
                            st.session_state.connections = api_client.get_my_connections_with_users()
                        else:
                            st.warning("⚠️ User updated but connection relationship update failed")
                    elif updated_user:
                        st.success(f"✅ Updated user: {name}")
                        st.session_state.connections = api_client.get_my_connections_with_users()
                    else:
                        st.error("❌ Failed to update connection")
            
            # Clear selection
            st.session_state.selected_node_id = None

if cancel_button:
    st.info("Changes cancelled")
    st.session_state.selected_node_id = None
    st.switch_page("pages/02_Dashboard.py")

if delete_button and selected_connection:
    # Confirm deletion
    st.warning(f"⚠️ Are you sure you want to delete {selected_connection.get('name', 'this connection')}?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ Yes, Delete", use_container_width=True):
            api_client = get_api_client()
            connection_id = selected_connection.get('connection_id')
            
            if connection_id:
                with st.spinner("Deleting connection..."):
                    success = api_client.delete_connection(connection_id)
                    
                    if success:
                        st.success(f"✅ Deleted {selected_connection.get('name', 'connection')}")
                        
                        # Refresh connections from backend
                        st.session_state.connections = api_client.get_my_connections_with_users()
                        st.session_state.selected_node_id = None
                        
                        import time
                        time.sleep(1)
                        st.switch_page("pages/02_Dashboard.py")
                    else:
                        st.error("❌ Failed to delete connection")
            else:
                st.error("❌ Connection ID not found")
    
    with col2:
        if st.button("❌ No, Keep It", use_container_width=True):
            st.info("Deletion cancelled")

# Quick actions
if selected_connection and not is_new_connection:
    st.divider()
    st.markdown("### ⚡ Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 View in Network", use_container_width=True):
            st.switch_page("pages/02_Dashboard.py")
    
    with col2:
        # Check if this connection has any referrals
        has_referrals = False
        if st.session_state.referrals:
            has_referrals = any(r['referrer_id'] == selected_connection['id'] for r in st.session_state.referrals)
        
        if st.button(f"🎯 {'View' if has_referrals else 'No'} Referrals", use_container_width=True, disabled=not has_referrals):
            st.switch_page("pages/03_Referrals.py")
    
    with col3:
        if st.button("✉️ Send Message", use_container_width=True):
            st.info(f"Message feature for {selected_connection['name']} (to be implemented)")

# Tips
with st.expander("💡 Connection Tips"):
    st.markdown("""
    **Tips for Managing Connections:**
    - Keep contact information up-to-date
    - Record how you met to remember context
    - Update last interaction date regularly
    - Use relationship strength to prioritize follow-ups
    - Add detailed notes about conversations and interests
    - Include LinkedIn for professional networking
    """)
