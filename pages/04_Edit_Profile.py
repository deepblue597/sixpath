"""
Profile Edit Page for SixPaths
Edit user's own profile information
"""
import streamlit as st
from utils.styling import apply_custom_css
from api.api_client import get_api_client
from utils.data_transformer import transform_user_for_api

# Page configuration
st.set_page_config(
    page_title="Edit Profile - SixPaths",
    page_icon="👤",
    layout="centered"
)

apply_custom_css()

# Check authentication
if not st.session_state.get('logged_in', False):
    st.warning("⚠️ Please login first")
    st.switch_page("pages/01_Login.py")

# Page header
st.title("👤 Edit Profile")
st.markdown("Update your professional information")

# Sidebar navigation
with st.sidebar:
    st.markdown("### 🧭 Navigation")
    
    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("streamlit_app.py")
    
    if st.button("📊 Dashboard", use_container_width=True):
        st.switch_page("pages/02_Dashboard.py")
    
    if st.button("🎯 Referrals", use_container_width=True):
        st.switch_page("pages/03_Referrals.py")
    
    st.divider()
    
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.switch_page("pages/01_Login.py")

# Main content
if st.session_state.user_data:
    user = st.session_state.user_data
    
    # Build full name
    first_name = user.get('first_name', '')
    last_name = user.get('last_name', '')
    full_name = f"{first_name} {last_name}".strip() or user.get('username', 'User')
    
    # Profile preview
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
        padding: 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 2rem;
    ">
        <h2 style="margin: 0; color: white;">👤 {}</h2>
        <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.9;">{}</p>
    </div>
    """.format(full_name, user.get('company', 'Professional')), unsafe_allow_html=True)
    
    # Edit form
    st.markdown("### ✏️ Edit Information")
    
    with st.form("profile_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        
        with col1:
            first_name_input = st.text_input(
                "First Name *",
                value=user.get('first_name', ''),
                placeholder="John",
                help="Your first name"
            )
            
            last_name_input = st.text_input(
                "Last Name *",
                value=user.get('last_name', ''),
                placeholder="Doe",
                help="Your last name"
            )
            
            email = st.text_input(
                "Email *",
                value=user.get('email', ''),
                placeholder="john.doe@example.com",
                help="Your professional email address"
            )
            
            phone = st.text_input(
                "Phone",
                value=user.get('phone', ''),
                placeholder="+1 (555) 123-4567",
                help="Your contact phone number"
            )
        
        with col2:
            company = st.text_input(
                "Company *",
                value=user.get('company', ''),
                placeholder="TechCorp",
                help="Your current employer"
            )
            
            sector = st.selectbox(
                "Sector *",
                options=["Technology", "Finance", "Healthcare", "Education", "Marketing", "Manufacturing", "Other"],
                index=["Technology", "Finance", "Healthcare", "Education", "Marketing", "Manufacturing", "Other"].index(
                    user.get('sector', 'Technology')
                ) if user.get('sector') in ["Technology", "Finance", "Healthcare", "Education", "Marketing", "Manufacturing", "Other"] else 0,
                help="Your industry sector"
            )
        
        linkedin = st.text_input(
            "LinkedIn Profile",
            value=user.get('linkedin_url', ''),
            placeholder="linkedin.com/in/johndoe",
            help="Your LinkedIn profile URL"
        )
        
        st.markdown("<small>* Required fields</small>", unsafe_allow_html=True)
        
        st.divider()
        
        # Form buttons
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown("")
        
        with col2:
            cancel_button = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        with col3:
            submit_button = st.form_submit_button("💾 Save Changes", use_container_width=True, type="primary")
    
    # Handle form submission
    if submit_button:
        # Validation
        errors = []
        
        if not first_name_input or len(first_name_input.strip()) < 2:
            errors.append("First name must be at least 2 characters")
        
        if not last_name_input or len(last_name_input.strip()) < 2:
            errors.append("Last name must be at least 2 characters")
        
        if not email or '@' not in email:
            errors.append("Valid email is required")
        
        if not company or len(company.strip()) < 2:
            errors.append("Company is required")
        
        if errors:
            for error in errors:
                st.error(f"❌ {error}")
        else:
            # Update user data via API
            api_client = get_api_client()
            
            update_data = {
                'first_name': first_name_input.strip(),
                'last_name': last_name_input.strip(),
                'email': email.strip() if email else '',
                'phone': phone.strip() if phone else '',
                'company': company.strip(),
                'sector': sector,
                'linkedin_url': linkedin.strip() if linkedin else ''
            }
            
            user_id = st.session_state.user_data.get('id')
            updated_user = api_client.update_user(user_id, update_data)
            
            if updated_user:
                # Update session state
                st.session_state.user_data = updated_user
                st.session_state.username = f"{first_name_input} {last_name_input}".strip()
                
                st.success("✅ Profile updated successfully!")
                st.balloons()
                
                # Show updated info
                with st.expander("📋 Updated Profile", expanded=True):
                    st.json(updated_user)
            else:
                st.error("❌ Failed to update profile. Please try again.")
    
    if cancel_button:
        st.info("Changes cancelled")
        st.switch_page("streamlit_app.py")
    
    # Additional information
    st.divider()
    
    st.markdown("### 📊 Profile Statistics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.session_state.connections:
            st.metric("Connections", len(st.session_state.connections))
        else:
            st.metric("Connections", 0)
    
    with col2:
        if st.session_state.referrals:
            st.metric("Active Referrals", len(st.session_state.referrals))
        else:
            st.metric("Active Referrals", 0)
    
    with col3:
        # Calculate sectors
        if st.session_state.connections:
            sectors = set(c['sector'] for c in st.session_state.connections)
            st.metric("Sectors Covered", len(sectors))
        else:
            st.metric("Sectors Covered", 0)
    
    # Tips
    with st.expander("💡 Profile Tips"):
        st.markdown("""
        **Tips for a Great Profile:**
        - Keep your information up-to-date
        - Use a professional email address
        - Include your LinkedIn for better networking
        - Make sure your position and company are accurate
        - Your profile information helps connections find you
        """)

else:
    st.error("User data not found. Please login again.")
    if st.button("Go to Login"):
        st.switch_page("pages/01_Login.py")
