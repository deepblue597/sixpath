"""
Login Page for SixPaths
Handles user authentication and session initialization
"""
import os
import streamlit as st
from styling import apply_custom_css
from api.api_call import AuthUserService, APIClient

# Page configuration
st.set_page_config(
    page_title="Login - SixPaths",
    page_icon="🔗",
    layout="centered"
)

apply_custom_css()

@st.cache_resource()
def get_api_services():
    api_base = None
    try:
        api_base = st.secrets.get("API_BASE_URL")
    except Exception:
        api_base = os.getenv("API_BASE_URL", "http://localhost:8000")
        
    api_client = APIClient(base_url=api_base)
    auth_service = AuthUserService(api_client)
    return api_client, auth_service

api_client, auth_service = get_api_services()

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'login_attempts' not in st.session_state:
    st.session_state.login_attempts = 0

# If already logged in, redirect to main page
if st.session_state.logged_in:
    st.switch_page("pages/02_Dashboard.py")

# Login page UI
st.markdown("""
<div style="text-align: center; padding: 2rem 0;">
    <h1 style="color: #1E3A8A; font-size: 3rem; margin-bottom: 0.5rem;">🔗 SixPaths</h1>
    <p style="color: #64748B; font-size: 1.2rem;">Professional Networking Visualization</p>
</div>
""", unsafe_allow_html=True)

# Create centered login form
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("""
    <div style="
        background-color: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
    ">
    """, unsafe_allow_html=True)
    
    st.markdown("### 🔐 Sign In")
    st.markdown("Enter your credentials to access your network")
    
    with st.form("login_form", clear_on_submit=False):
        username = st.text_input(
            "Username",
            placeholder="Enter your username",
            help="Demo credentials: demo / password"
        )
        
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password"
        )
        

        submit_button = st.form_submit_button("Login", use_container_width=True)
    
    # Handle form submission
    if submit_button:
        # Basic validation
        if not username or not password:
            st.warning("⚠️ Please enter both username and password")
        else:
            # api_base = None
            # try:
            #     api_base = st.secrets.get("API_BASE_URL")
            # except Exception:
            #     api_base = os.getenv("API_BASE_URL")

            with st.spinner("Authenticating..."):
                try:
                    result = auth_service.login(username, password)
                    
                    if result and result.get("access_token"):
                        token = result.get("access_token")
                        
                        # ensure token is a concrete string for the API client
                        if token is None:
                            raise ValueError("Authentication succeeded but no access token was returned")
                        token = str(token)
                        
                        api_client.set_token(token)
                        # Update session state
                        st.session_state.token = token
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.login_attempts = 0
                        
                        st.success(f"✅ Welcome back, {username}!")
                        #st.balloons()
                        
                        import time
                        time.sleep(1)

                        # fetch current user profile and cache connections/referrals
                        try:
                            user_data = auth_service.get_current_user()
                            st.session_state.user_data = user_data
                            # preload connections and referrals placeholders (pages will fetch on demand)
                            st.session_state._connections = None
                            st.session_state.referrals = None
                        except Exception as e:
                            st.error(f"❌ Failed to fetch user profile: {str(e)}")
                            
                        st.switch_page("pages/02_Dashboard.py")
                    else:
                        st.session_state.login_attempts += 1
                        err = None
                        if isinstance(result, dict):
                            err = result.get("error")
                        if not err:
                            err = "Invalid credentials or server error"
                        st.error(f"❌ Login failed: {err}")
                except Exception as e:
                    st.session_state.login_attempts += 1
                    st.error(f"❌ Login failed: {str(e)}")
                            
    
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Demo credentials hint
    st.info("💡 **Login with your account:** Use your registered email and password")
    st.info("🔐 **Need an account?** Contact your administrator for access")

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 3rem; color: #94A3B8; font-size: 0.875rem;">
    <p>SixPaths © 2026 | Professional Networking Made Visual</p>
</div>
""", unsafe_allow_html=True)
