import streamlit as st
import networkx as nx
from streamlit_helpers import api_get, decode_jwt_sub, render_pyvis, set_query_params


def network_ui():
    st.header('My Network')
    token = st.session_state.get('token')
    if not token:
        st.info('Please login first')
        return
    user_id = decode_jwt_sub(token)
    if not user_id:
        st.error('Could not decode user id from token')
        return
    try:
        connections = api_get(f'/connections/user/{user_id}', token=token)
        G = nx.Graph()
        for c in connections:
            p1 = c.get('person1') or {'id': c.get('person1_id'), 'first_name': str(c.get('person1_id'))}
            p2 = c.get('person2') or {'id': c.get('person2_id'), 'first_name': str(c.get('person2_id'))}
            G.add_node(str(p1['id']), label=f"{p1.get('first_name','')} {p1.get('last_name','')}")
            G.add_node(str(p2['id']), label=f"{p2.get('first_name','')} {p2.get('last_name','')}")
            G.add_edge(str(p1['id']), str(p2['id']))

        if G.number_of_nodes() == 0:
            st.info('No connections found')
            return

        nodes = list(G.nodes(data=True))
        node_labels = {n: d.get('label', n) for n,d in nodes}
        cols = st.columns([3,1])
        with cols[1]:
            selected = st.selectbox('Select user', options=list(node_labels.keys()), format_func=lambda k: node_labels[k])
            if st.button('View profile'):
                st.session_state['selected_user'] = selected
                st.session_state['menu'] = 'Profile'
                from streamlit_helpers import rerun
                rerun()
        render_pyvis(G, central_id=user_id)
    except Exception as e:
        st.error(f'Error loading network: {e}')
