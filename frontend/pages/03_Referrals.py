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
from api.service_locator import get_referral_service , get_auth_service , get_api_client, get_user_service
st.set_page_config(page_title="Referrals - SixPaths", page_icon="🎯", layout="wide")


api_client =  get_api_client()
referral_service = get_referral_service()
auth_service = get_auth_service()
user_service = get_user_service()

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
    # ensure token set on client
    api_client.set_token(token)
    with st.spinner("Loading referrals..."):
        try:
            result = referral_service.get_current_user_referrals(st.session_state.referrals_limit, st.session_state.referrals_offset)
        except Exception as e:
            st.session_state._referrals_load_info = {"error": str(e)}
            st.session_state.referrals = []
            return
    st.session_state.referrals = result if isinstance(result, list) else []

if st.button("Reload referrals"):
    _load_referrals()

if "referrals" not in st.session_state or st.session_state.get("referrals") is None:
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

# build users lookup for referrer names
users = st.session_state.get('all_users') or st.session_state.get('_users')
if users is None:
    try:
        users = user_service.get_users()
    except Exception:
        users = []
    st.session_state.all_users = users

users_by_id = {}
for u in users or []:
    try:
        uid = u.id #u.get('id') if isinstance(u, dict) else getattr(u, 'id', None)
        first = (u.get('first_name') if isinstance(u, dict) else getattr(u, 'first_name', None)) or ''
        last = (u.get('last_name') if isinstance(u, dict) else getattr(u, 'last_name', None)) or ''
        email = (u.get('email') if isinstance(u, dict) else getattr(u, 'email', None)) or ''
        display = f"{first} {last}".strip() or email or f"User {uid}"
        users_by_id[uid] = display
    except Exception:
        continue

if filtered:
    df = pd.DataFrame([{
        'id': r.get('id'),
        'referrer': users_by_id.get(r.get('referrer_id')) or r.get('referrer_name') or '',
        'company': r.get('company'),
        'position': r.get('position'),
        'status': r.get('status'),
        'applied': r.get('application_date')
    } for r in filtered])
    st.dataframe(df, width='stretch')

    # Selection
    ids = [r.get('id') for r in filtered]
    labels = [f"{(users_by_id.get(r.get('referrer_id')) or r.get('referrer_name'))} — {r.get('position')} @ {r.get('company')} (id:{r.get('id')})" for r in filtered]
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
        api_client.set_token(token)
        with st.spinner("Loading referral..."):
            try:
                editing_ref = referral_service.get_referral(str(editing_id))
            except Exception:
                editing_ref = None

    title = "✏️ Edit Referral" if editing_ref else "➕ Create Referral"
    st.markdown(f"### {title}")

    with st.form("referral_crud_form"):
        col1, col2 = st.columns(2)
        with col1:
            # referrer selection: use users (people in the system) instead of connections
            user_options = {}
            users = st.session_state.get('all_users') or st.session_state.get('_users')
            if users is None:
                # try fetching from user service
                try:
                    users = user_service.get_users()
                except Exception:
                    users = []
                # cache for later
                st.session_state.all_users = users

            for u in users or []:
                try:
                    uid = u.get('id') if isinstance(u, dict) else getattr(u, 'id', None)
                    name = (u.get('first_name') if isinstance(u, dict) else getattr(u, 'first_name', None)) or (u.get('email') if isinstance(u, dict) else getattr(u, 'email', ''))
                    last = (u.get('last_name') if isinstance(u, dict) else getattr(u, 'last_name', ''))
                    display = f"{name} {last} (id:{uid})"
                    user_options[display] = uid
                except Exception:
                    continue

            if user_options:
                default_ref = None
                if editing_ref:
                    default_ref = next((k for k,v in user_options.items() if v==editing_ref.get('referrer_id')), list(user_options.keys())[0])
                selected_ref = st.selectbox("Referrer", options=list(user_options.keys()), index=list(user_options.keys()).index(default_ref) if default_ref else 0)
                referrer_id = user_options.get(selected_ref)
            else:
                st.info("No users available to select as referrer")
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
                            try:
                                res = referral_service.update_referral(str(editing_ref.get('id')), payload)
                            except Exception:
                                res = None
                if res:
                    st.success("✅ Referral updated")
                    st.session_state.show_referral_form = False
                    st.session_state.selected_referral_id = None
                    _load_referrals()
                else:
                    st.error("❌ Failed to update referral")
            else:
                with st.spinner("Creating referral..."):
                            try:
                                res = referral_service.create_referral(payload)
                            except Exception:
                                res = None
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
                try:
                    ok = referral_service.delete_referral(str(rid))
                except Exception:
                    ok = False
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

