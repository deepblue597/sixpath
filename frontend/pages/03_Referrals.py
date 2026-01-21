"""
Referrals CRUD Page (Streamlit + FastAPI)

Standalone HTTP helper functions call the backend /referrals routes.
UI uses Streamlit forms and state; no classes or API clients.
"""
import os
from typing import List, Optional
import requests
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Referrals - SixPaths", page_icon="🎯", layout="wide")

def _get_api_base() -> str:
    try:
        return st.secrets.get("API_BASE_URL") or os.getenv("API_BASE_URL", "http://localhost:8000")
    except Exception:
        return os.getenv("API_BASE_URL", "http://localhost:8000")

def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

def get_current_user_referrals(offset: int, limit: int, token: str):
    """Return a dict with items, status, and optional text for diagnostics."""
    url = _get_api_base().rstrip("/") + f"/referrals/me?offset={offset}&limit={limit}"
    try:
        headers = _auth_headers(token)
        resp = requests.get(url, headers=headers, timeout=8)
        try:
            body = resp.json()
        except Exception:
            body = resp.text
        return {"items": body if resp.status_code == 200 else [], "status": resp.status_code, "text": body, "url": url, "headers": {k: (v if k.lower() != 'authorization' else 'REDACTED') for k,v in headers.items()}}
    except requests.RequestException as e:
        return {"items": [], "status": None, "text": repr(e), "url": url, "headers": {"authorization": f"REDACTED (len={len(token) if token else 0})"}}

def get_referral(referral_id: int, token: str) -> Optional[dict]:
    url = _get_api_base().rstrip("/") + f"/referrals/{referral_id}"
    try:
        resp = requests.get(url, headers=_auth_headers(token), timeout=6)
        if resp.status_code == 200:
            return resp.json()
    except requests.RequestException:
        pass
    return None

def create_referral(payload: dict, token: str) -> Optional[dict]:
    url = _get_api_base().rstrip("/") + "/referrals"
    try:
        resp = requests.post(url, headers=_auth_headers(token), json=payload, timeout=8)
        if resp.status_code in (200, 201):
            return resp.json()
    except requests.RequestException:
        pass
    return None

def update_referral(referral_id: int, payload: dict, token: str) -> Optional[dict]:
    url = _get_api_base().rstrip("/") + f"/referrals/{referral_id}"
    try:
        resp = requests.put(url, headers=_auth_headers(token), json=payload, timeout=8)
        if resp.status_code in (200, 201):
            return resp.json()
    except requests.RequestException:
        pass
    return None

def delete_referral(referral_id: int, token: str) -> bool:
    url = _get_api_base().rstrip("/") + f"/referrals/{referral_id}"
    try:
        resp = requests.delete(url, headers=_auth_headers(token), timeout=8)
        return resp.status_code in (200, 204)
    except requests.RequestException:
        return False

from styling import apply_custom_css
apply_custom_css()

if not st.session_state.get("logged_in"):
    st.warning("⚠️ Please login first")
    st.stop()

token = st.session_state.get("token")
if not token:
    st.error("Authentication token missing. Please login.")
    st.stop()

st.title("🎯 Referrals Management")
st.markdown("Track and manage your job referrals from your network")

# UI state defaults
if "referrals_offset" not in st.session_state:
    st.session_state.referrals_offset = 0
if "referrals_limit" not in st.session_state:
    st.session_state.referrals_limit = 20
if "selected_referral_id" not in st.session_state:
    st.session_state.selected_referral_id = None
if "show_referral_form" not in st.session_state:
    st.session_state.show_referral_form = False

def _load_referrals():
    with st.spinner("Loading referrals..."):
        result = get_current_user_referrals(st.session_state.referrals_offset, st.session_state.referrals_limit, token)
    # store diagnostics
    st.session_state._referrals_load_info = {
        "status": result.get("status"),
        "text": result.get("text")
    }
    st.session_state.referrals = result.get("items") or []

if st.button("Reload referrals"):
    _load_referrals()

if "referrals" not in st.session_state:
    _load_referrals()

cols = st.columns([3, 1, 1, 1])
with cols[0]:
    _refs = st.session_state.get('referrals') or []
    st.markdown(f"**Total loaded:** {len(_refs)}")
with cols[1]:
    if st.button("Prev"):
        st.session_state.referrals_offset = max(0, st.session_state.referrals_offset - st.session_state.referrals_limit)
        _load_referrals()
with cols[2]:
    if st.button("Next"):
        st.session_state.referrals_offset += st.session_state.referrals_limit
        _load_referrals()
with cols[3]:
    st.selectbox("Per page", options=[10,20,50,100], index=[10,20,50,100].index(st.session_state.referrals_limit), key="_per_page", on_change=lambda: (st.session_state.update({"referrals_limit": int(st.session_state.get("_per_page",20)), "referrals_offset":0}), _load_referrals()))

st.divider()

# Search and create button
search_col, create_col = st.columns([4,1])
with search_col:
    search_q = st.text_input("Search referrals", placeholder="Search by company, position, referrer...")
with create_col:
    if st.button("➕ New Referral"):
        st.session_state.show_referral_form = True
        st.session_state.selected_referral_id = None

def _filtered(refs):
    if not search_q:
        return refs
    q = search_q.lower()
    return [r for r in refs if q in (r.get('company','') + ' ' + r.get('position','') + ' ' + r.get('referrer_name','') + ' ' + r.get('notes','')).lower()]

filtered = _filtered(st.session_state.get('referrals') or [])

st.markdown(f"### 📋 Referrals ({len(filtered)})")

if filtered:
    df = pd.DataFrame([{
        'id': r.get('id'),
        'referrer': r.get('referrer_name'),
        'company': r.get('company'),
        'position': r.get('position'),
        'status': r.get('status'),
        'applied': r.get('application_date')
    } for r in filtered])
    st.dataframe(df, use_container_width=True)

    # Selection
    ids = [r.get('id') for r in filtered]
    labels = [f"{r.get('referrer_name')} — {r.get('position')} @ {r.get('company')} (id:{r.get('id')})" for r in filtered]
    sel = st.selectbox("Select referral", ["-- none --"] + labels)
    if sel != "-- none --":
        idx = labels.index(sel)
        st.session_state.selected_referral_id = ids[idx]

else:
    info_msg = "No referrals found"
    load_info = st.session_state.get("_referrals_load_info") or {}
    status = load_info.get("status")
    text = load_info.get("text")
    if status is None:
        st.info(f"{info_msg} — failed to contact server: {text}")
        url = load_info.get("url")
        headers = load_info.get("headers")
        if url:
            st.write("**Tried URL:**", url)
        if headers:
            st.write("**Request headers:**", headers)
    elif status != 200:
        st.info(f"{info_msg} — server returned status {status}: {text}")
        url = load_info.get("url")
        headers = load_info.get("headers")
        if url:
            st.write("**Tried URL:**", url)
        if headers:
            st.write("**Request headers:**", headers)
    else:
        st.info(info_msg)

st.divider()

# Create / Edit form
if st.session_state.show_referral_form or st.session_state.selected_referral_id:
    editing_id = st.session_state.selected_referral_id if st.session_state.selected_referral_id else None
    editing_ref = None
    if editing_id:
        with st.spinner("Loading referral..."):
            editing_ref = get_referral(editing_id, token)

    title = "✏️ Edit Referral" if editing_ref else "➕ Create Referral"
    st.markdown(f"### {title}")

    with st.form("referral_crud_form"):
        col1, col2 = st.columns(2)
        with col1:
            # referrer selection: use connections in session if available
            conn_options = {}
            if st.session_state.get('connections'):
                for c in st.session_state.connections:
                    cid = c.get('id')
                    name = c.get('name') or f"{c.get('first_name','')} {c.get('last_name','') }"
                    conn_options[f"{name} (id:{cid})"] = cid

            if conn_options:
                default_ref = None
                if editing_ref:
                    default_ref = next((k for k,v in conn_options.items() if v==editing_ref.get('referrer_id')), list(conn_options.keys())[0])
                selected_ref = st.selectbox("Referrer", options=list(conn_options.keys()), index=list(conn_options.keys()).index(default_ref) if default_ref else 0)
                referrer_id = conn_options.get(selected_ref)
            else:
                st.info("No connections available to select as referrer")
                referrer_id = st.number_input("Referrer ID", min_value=1, step=1, value=(editing_ref.get('referrer_id') if editing_ref else 0))

            company = st.text_input("Company", value=(editing_ref.get('company') if editing_ref else ""))
            position = st.text_input("Position", value=(editing_ref.get('position') if editing_ref else ""))

        with col2:
            status_opts = ["Pending", "Applied", "Under Review", "Interview Scheduled", "Accepted", "Rejected"]
            status = st.selectbox("Status", options=status_opts, index=status_opts.index(editing_ref.get('status')) if editing_ref and editing_ref.get('status') in status_opts else 0)
            application_date = st.date_input("Application date", value=(datetime.fromisoformat(editing_ref.get('application_date')).date() if editing_ref and editing_ref.get('application_date') else datetime.now().date()))
            notes = st.text_area("Notes", value=(editing_ref.get('notes') if editing_ref else ""))

        col_a, col_b = st.columns([1,1])
        with col_a:
            save_btn = st.form_submit_button("💾 Save")
        with col_b:
            cancel_btn = st.form_submit_button("❌ Cancel")

    if save_btn:
        if not company or not position:
            st.error("Company and Position are required")
        else:
            payload = {
                "referrer_id": int(referrer_id),
                "company": company,
                "position": position,
                "status": status,
                "application_date": application_date.isoformat(),
                "notes": notes or ""
            }
            if editing_ref:
                with st.spinner("Updating referral..."):
                    res = update_referral(editing_ref.get('id'), payload, token)
                if res:
                    st.success("✅ Referral updated")
                    st.session_state.show_referral_form = False
                    st.session_state.selected_referral_id = None
                    _load_referrals()
                else:
                    st.error("❌ Failed to update referral")
            else:
                with st.spinner("Creating referral..."):
                    res = create_referral(payload, token)
                if res:
                    st.success("✅ Referral created")
                    st.session_state.show_referral_form = False
                    _load_referrals()
                else:
                    st.error("❌ Failed to create referral")

    if cancel_btn:
        st.session_state.show_referral_form = False
        st.session_state.selected_referral_id = None

st.divider()

# Deletion panel
st.subheader("Delete Referral")
if st.session_state.selected_referral_id:
    rid = st.session_state.selected_referral_id
    if st.checkbox("Confirm deletion of selected referral"):
        if st.button("Delete referral"):
            with st.spinner("Deleting..."):
                ok = delete_referral(rid, token)
            if ok:
                st.success("✅ Referral deleted")
                st.session_state.selected_referral_id = None
                _load_referrals()
            else:
                st.error("❌ Failed to delete referral")

st.markdown("---")

# Export
if st.session_state.get('referrals'):
    df_export = pd.DataFrame(st.session_state.referrals)
    csv = df_export.to_csv(index=False)
    st.download_button("⬇️ Download CSV", csv, "referrals.csv", "text/csv")

with st.expander("💡 Referral Tips"):
    st.markdown("""
    - Use the Referrer selector to pick a connection from your network
    - Pagination uses `offset` and `limit` to load subsets
    - Fill required fields before saving
    """)

