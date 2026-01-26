"""
Login Page for SixPaths
Handles user authentication and session initialization
"""
import os
import time
import streamlit as st
from models.input_models import AccountCreate, UserCreate 
from styling import apply_custom_css
from frontend.api.service_locator import get_api_client , get_auth_service 
# Page configuration
st.set_page_config(
    page_title="Login - SixPaths",
    page_icon="🔗",
    layout="centered"
)

apply_custom_css()



api_client = get_api_client()
auth_service = get_auth_service()
# Determine whether account creation should be shown
try:
    #account_creation_allowed = True
    # AuthUserService exposes `account_user_exist()`
    #if hasattr(auth_service, "account_user_exist"):
    account_creation_allowed = not auth_service.account_user_exist()
except Exception:
    account_creation_allowed = False
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

    
    st.markdown("### 🔐 Sign In")
    st.markdown("Enter your credentials to access your network")
    
    with st.form("login_form", clear_on_submit=False):
        username = st.text_input(
            "Username",
            placeholder="Enter your username"
        )
        
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password"
        )
        

        submit_button = st.form_submit_button("Login", width='stretch')

    # Create account toggle (only show if account creation is allowed)
    if "show_create_account" not in st.session_state:
        st.session_state.show_create_account = False
    if account_creation_allowed:
        if st.button("Create account"):
            st.session_state.show_create_account = True

    if st.session_state.show_create_account:
        st.markdown("---")
        st.markdown("### ➕ Create Account")
        with st.form("create_account_form"):
            ca_first = st.text_input("First name")
            ca_last = st.text_input("Last name")
            ca_email = st.text_input("Email (optional)")
            ca_username = st.text_input("Username")
            ca_password = st.text_input("Password", type="password")
            ca_submit = st.form_submit_button("Create Account")

        if ca_submit:
            if not ca_username or not ca_password or not ca_first or not ca_last:
                st.error("Please provide first name, last name, username and password")
            else:
                with st.spinner("Creating account..."):
                    # TODO: create classes for payloads
                    # payload = {
                    #     "username": ca_username,
                    #     "password": ca_password,
                    #     "first_name": ca_first,
                    #     "last_name": ca_last,
                    #     "email": ca_email or None,
                    #     "is_me": True
                    # }
                    payload = AccountCreate(
                        username=ca_username,
                        password=ca_password,
                        first_name=ca_first,
                        last_name=ca_last,
                        email=ca_email or None,
                        is_me=True
                    )
                    try:
                        res = auth_service.register_user(payload)
                    except Exception as e:
                        res = None
                        err = str(e)
                    if res:
                        st.success("Account created — logging in...")
                        try:
                            login_res = auth_service.login(ca_username, ca_password)
                        except Exception as e:
                            login_res = None
                        if login_res and login_res.access_token:
                            token = str(login_res.access_token)
                            api_client.set_token(token)
                            st.session_state.token = token
                            st.session_state.logged_in = True
                            st.session_state.username = ca_username
                            st.session_state.login_attempts = 0
                            # preload placeholders
                            st.session_state.connections = None
                            st.session_state.referrals = None
                            try:
                                params = st.experimental_get_query_params()
                                params["ts"] = str(int(time.time()))
                                st.experimental_set_query_params(**params)
                            except Exception:
                                # fallback: set logged_in and navigate
                                st.switch_page("pages/02_Dashboard.py")
                        else:
                            st.error("Account created but automatic login failed — please login manually")
                    else:
                        st.error(f"Failed to create account: {locals().get('err','Unknown error')}")
    
    # Handle form submission
    if submit_button:
        # Basic validation
        if not username or not password:
            st.warning("⚠️ Please enter both username and password")
        else:

            with st.spinner("Authenticating..."):
                try:
                    result = auth_service.login(username, password)
                    
                    if result and result.access_token:
                        token = result.access_token
                        
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
                            st.session_state.connections = None
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
