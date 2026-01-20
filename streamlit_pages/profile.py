import streamlit as st
from streamlit_helpers import api_get, api_put, decode_jwt_sub, set_query_params


def profile_ui():
    st.header('Profile')
    token = st.session_state.get('token')
    if not token:
        st.info('Please login first')
        return
    user_param = st.session_state.get('selected_user')
    user_id = user_param or decode_jwt_sub(token)
    if not user_id:
        st.error('No user selected and cannot decode token')
        return
    try:
        user = api_get(f'/users/{user_id}', token=token)
        st.subheader(f"{user.get('first_name')} {user.get('last_name')}")
        st.write('Company:', user.get('company'))
        st.write('Sector:', user.get('sector'))
        if st.button('Edit profile'):
            st.session_state['selected_user'] = user_id
            st.session_state['menu'] = 'Edit'
            from streamlit_helpers import rerun
            rerun()
    except Exception as e:
        st.error(f'Error loading profile: {e}')
