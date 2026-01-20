import requests
import json
import base64
from pyvis.network import Network
import streamlit as st
import streamlit.components.v1 as components
import os


def _resolve_backend():
    """Return backend URL from Streamlit secrets, environment, or default."""
    default = os.environ.get('BACKEND_URL', 'http://localhost:8000')
    try:
        # st.secrets may raise if no secrets file exists; guard it
        return st.secrets.get('backend_url', default)
    except Exception:
        return default


BACKEND = _resolve_backend()


def set_query_params(**kwargs):
    """Set query params using the stable API if available, otherwise fall back to experimental.

    Using getattr avoids static attribute checks that can trigger Pylance errors.
    """
    func = getattr(st, 'set_query_params', None)
    if not func:
        # Do not mix experimental setter with st.query_params reads; require newer Streamlit
        raise RuntimeError('st.set_query_params not available. Please upgrade Streamlit to a version that provides set_query_params.')
    return func(**kwargs)


def rerun():
    """Call Streamlit rerun function in a way that avoids static attribute checks.

    Uses `getattr` to locate `experimental_rerun`. If not available, raises RuntimeError.
    """
    fn = getattr(st, 'experimental_rerun', None)
    if not fn:
        raise RuntimeError('Streamlit rerun API not available in this environment')
    return fn()

# API helpers
def api_post_login(username, password):
    url = f"{BACKEND}/auth/login"
    r = requests.post(url, data={'username': username, 'password': password})
    r.raise_for_status()
    return r.json()

def api_get(path, token=None):
    headers = {'Authorization': f"Bearer {token}"} if token else {}
    r = requests.get(BACKEND + path, headers=headers)
    r.raise_for_status()
    return r.json()

def api_put(path, data, token=None):
    headers = {'Authorization': f"Bearer {token}", 'Content-Type': 'application/json'} if token else {'Content-Type': 'application/json'}
    r = requests.put(BACKEND + path, headers=headers, data=json.dumps(data))
    r.raise_for_status()
    return r.json()

# JWT helper
def decode_jwt_sub(token):
    try:
        payload = token.split('.')[1]
        payload += '=' * (-len(payload) % 4)
        decoded = json.loads(base64.urlsafe_b64decode(payload))
        return int(decoded.get('sub')) if decoded.get('sub') else None
    except Exception:
        return None

# Pyvis renderer
def render_pyvis(graph_nx, central_id=None, height=700):
    net = Network(height=f'{height}px', width='100%', notebook=False)
    net.from_nx(graph_nx)
    if central_id is not None:
        target = str(central_id)
        # net.nodes is a list of node dicts; avoid relying on internal node_map structure
        for n in net.nodes:
            try:
                if str(n.get('id')) == target or str(n.get('label')) == target:
                    n['size'] = 30
                    n['color'] = '#ff7f0e'
                    break
            except Exception:
                continue
    html = net.generate_html()
    components.html(html, height=height, scrolling=True)
