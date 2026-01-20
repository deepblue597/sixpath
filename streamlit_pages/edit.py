import streamlit as st
from streamlit_helpers import api_get, api_put, decode_jwt_sub, set_query_params


def edit_ui():
    st.header('Edit Profile')
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
        with st.form('edit_user'):
            first = st.text_input('First name', value=user.get('first_name',''))
            last = st.text_input('Last name', value=user.get('last_name',''))
            company = st.text_input('Company', value=user.get('company') or '')
            submit = st.form_submit_button('Save')
            if submit:
                payload = {'first_name': first, 'last_name': last, 'company': company}
                try:
                    updated = api_put(f'/users/{user_id}', payload, token=token)
                    st.success('Profile updated')
                    st.session_state['selected_user'] = user_id
                    st.session_state['menu'] = 'Profile'
                    from streamlit_helpers import rerun
                    rerun()
                except Exception as e:
                    st.error(f'Update failed: {e}')
    except Exception as e:
        st.error(f'Error loading profile: {e}')
