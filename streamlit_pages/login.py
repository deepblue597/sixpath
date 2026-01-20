import streamlit as st
from streamlit_helpers import api_post_login

def login_ui():
    st.header('Login')
    with st.form('login_form'):
        username = st.text_input('Username')
        password = st.text_input('Password', type='password')
        submitted = st.form_submit_button('Login')
        if submitted:
            try:
                data = api_post_login(username, password)
                token = data.get('access_token') or data.get('accessToken') or data.get('token')
                if token:
                    st.session_state['token'] = token
                    st.success('Logged in')
                else:
                    st.error('Login response missing token')
            except Exception as e:
                st.error(f'Login failed: {e}')
