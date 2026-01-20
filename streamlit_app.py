import streamlit as st
import streamlit.components.v1 as components
import requests
import json
import base64
from pyvis.network import Network
import networkx as nx
from io import BytesIO

# Config
st.set_page_config(page_title='Sixpath', layout='wide')

from streamlit_helpers import api_post_login, api_get, api_put, decode_jwt_sub, render_pyvis

# UI
st.title('Sixpath — Network')

if 'token' not in st.session_state:
    st.session_state['token'] = None

menu = st.sidebar.selectbox('Menu', ['Login', 'My Network', 'Profile', 'Edit'], key='menu')

if menu == 'Login':
    from streamlit_pages.login import login_ui
    login_ui()
elif menu == 'My Network':
    from streamlit_pages.network import network_ui
    network_ui()
elif menu == 'Profile':
    from streamlit_pages.profile import profile_ui
    profile_ui()
elif menu == 'Edit':
    from streamlit_pages.edit import edit_ui
    edit_ui()
