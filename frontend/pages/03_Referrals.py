"""
Referrals CRUD Page — SixPaths (clean app layout)

- Overview: KPI cards + searchable table + pagination
- Edit: left = pick referral, right = edit form + danger zone
- Create: clean form card
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import streamlit as st

from frontend.api.service_locator import (
    get_referral_service,
    get_auth_service,
    get_api_client,
    get_user_service,
)
from styling import apply_custom_css

# -----------------------------
# Page setup
# -----------------------------
st.set_page_config(page_title="Referrals - SixPaths", page_icon="🎯", layout="wide")
apply_custom_css()

api_client = get_api_client()
referral_service = get_referral_service()
auth_service = get_auth_service()
user_service = get_user_service()

# -----------------------------
# Auth guard
# -----------------------------
if not st.session_state.get("logged_in"):
    st.warning("Please login first")
    st.stop()

token = st.session_state.get("token")
if not token:
    st.error("Authentication token missing. Please login.")
    st.stop()

api_client.set_token(token)
try:
    referral_service.api_client.set_token(token)
    user_service.api_client.set_token(token)
except Exception:
    pass

# -----------------------------
# State defaults
# -----------------------------
st.session_state.setdefault("referrals_offset", 0)
st.session_state.setdefault("referrals_limit", 20)
st.session_state.setdefault("referrals", None)
st.session_state.setdefault("referrals_has_next", False)
st.session_state.setdefault("selected_referral_id", None)
st.session_state.setdefault("all_users", None)

# -----------------------------
# Helpers
# -----------------------------
def _safe_text(v: Any) -> str:
    return (v or "").strip() if isinstance(v, str) else (str(v) if v is not None else "")

def _kpi_card(title: str, value: str, caption: str = "") -> None:
    st.markdown(
        f"""
        <div class="six-card">
          <div style="font-size:0.85rem;color:#64748B;font-weight:650;">{title}</div>
          <div style="font-size:1.9rem;font-weight:850;color:#0F172A;line-height:1.15;">{value}</div>
          <div class="muted">{caption}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def _load_users_cached() -> List[Any]:
    users = st.session_state.get("all_users")
    if users is None:
        try:
            users = user_service.get_users() or []
        except Exception:
            users = []
        st.session_state.all_users = users
    return users

def _users_by_id(users: List[Any]) -> Dict[int, str]:
    out: Dict[int, str] = {}
    for u in users or []:
        try:
            uid = u.get("id") if isinstance(u, dict) else getattr(u, "id", None)
            if uid is None:
                continue
            first = (u.get("first_name") if isinstance(u, dict) else getattr(u, "first_name", None)) or ""
            last = (u.get("last_name") if isinstance(u, dict) else getattr(u, "last_name", None)) or ""
            email = (u.get("email") if isinstance(u, dict) else getattr(u, "email", None)) or ""
            display = f"{first} {last}".strip() or email or f"User {uid}"
            out[int(uid)] = display
        except Exception:
            continue
    return out

def _parse_date(d: Any):
    if not d:
        return datetime.now().date()
    try:
        return datetime.fromisoformat(str(d)).date()
    except Exception:
        return datetime.now().date()

def _load_referrals_page(limit: int, offset: int) -> Tuple[List[dict], bool]:
    """
    Prefer: backend returns limit+1 so we can detect has_next.
    If backend returns exactly limit items, we use len==limit heuristic.
    """
    api_client.set_token(token)
    try:
        rows = referral_service.get_current_user_referrals(limit + 1, offset)  # try limit+1
        rows = rows if isinstance(rows, list) else []
        has_next = len(rows) > limit
        return rows[:limit], has_next
    except Exception:
        # fallback to your original call
        try:
            rows = referral_service.get_current_user_referrals(limit, offset)
            rows = rows if isinstance(rows, list) else []
            has_next = len(rows) == limit
            return rows, has_next
        except Exception:
            return [], False

def _reload_referrals():
    with st.spinner("Loading referrals..."):
        rows, has_next = _load_referrals_page(st.session_state.referrals_limit, st.session_state.referrals_offset)
    st.session_state.referrals = rows
    st.session_state.referrals_has_next = has_next

def _clear_selection():
    st.session_state.selected_referral_id = None

def _filter_refs(refs: List[dict], q: str) -> List[dict]:
    if not q:
        return refs
    ql = q.lower()
    def hay(r: dict) -> str:
        return " ".join([
            _safe_text(r.get("company")),
            _safe_text(r.get("position")),
            _safe_text(r.get("status")),
            _safe_text(r.get("notes")),
            _safe_text(r.get("referrer_name")),
        ]).lower()
    return [r for r in refs if ql in hay(r)]

# -----------------------------
# Header
# -----------------------------
st.title("🎯 Referrals")
st.caption("Track and manage referrals sourced from your network.")

# Ensure loaded once
if st.session_state.referrals is None:
    _reload_referrals()

refs = st.session_state.get("referrals") or []
has_next = bool(st.session_state.get("referrals_has_next", False))

users = _load_users_cached()
users_by_id = _users_by_id(users)

# KPI row + quick actions
k1, k2, k3, k4 = st.columns([1, 1, 1, 2], gap="medium")
with k1:
    _kpi_card("Loaded", str(len(refs)), "Rows in memory")
with k2:
    _kpi_card("Page", str((st.session_state.referrals_offset // st.session_state.referrals_limit) + 1), "Pagination")
with k3:
    _kpi_card("Per page", str(st.session_state.referrals_limit), "Limit")
with k4:
    with st.container(border=True):
        st.markdown("**Quick actions**")
        a, b, c = st.columns(3)
        if a.button("Reload", type="primary", width='stretch'):
            _reload_referrals()
            _clear_selection()
            st.rerun()
        if b.button("Clear selection", width='stretch'):
            _clear_selection()
            st.rerun()
        if c.button("Export CSV", width='stretch'):
            st.session_state["_export_refs"] = True

st.divider()

# Tabs
tab_all, tab_edit, tab_create = st.tabs(["Overview", "Edit", "Create"])  # [web:733]

# =========================================================
# TAB: Overview
# =========================================================
with tab_all:
    with st.container(border=True):
        top = st.columns([2, 2, 1, 1, 1], vertical_alignment="center")  # [web:608]
        with top[0]:
            search_q = st.text_input("Search", placeholder="Company, position, status, notes…", key="ref_search")
        with top[1]:
            st.caption("Search applies to currently loaded page.")
        with top[2]:
            if st.button("Prev", width='stretch', disabled=(st.session_state.referrals_offset == 0)):
                st.session_state.referrals_offset = max(0, st.session_state.referrals_offset - st.session_state.referrals_limit)
                _reload_referrals()
                _clear_selection()
                st.rerun()
        with top[3]:
            if st.button("Next", width='stretch', disabled=(not has_next)):
                st.session_state.referrals_offset += st.session_state.referrals_limit
                _reload_referrals()
                _clear_selection()
                st.rerun()
        with top[4]:
            per_page = st.selectbox("Per page", [10, 20, 50, 100], index=[10, 20, 50, 100].index(st.session_state.referrals_limit))
            if per_page != st.session_state.referrals_limit:
                st.session_state.referrals_limit = int(per_page)
                st.session_state.referrals_offset = 0
                _reload_referrals()
                _clear_selection()
                st.rerun()

    filtered = _filter_refs(refs, st.session_state.get("ref_search", ""))

    with st.container(border=True):
        st.subheader(f"Referrals ({len(filtered)})")

        if not filtered:
            st.info("No referrals found.")
        else:
            df = pd.DataFrame([{
                "ID": r.get("id"),
                "Referrer": users_by_id.get(int(r.get("referrer_id") or 0)) or r.get("referrer_name") or "",
                "Company": r.get("company"),
                "Position": r.get("position"),
                "Status": r.get("status"),
                "Applied": r.get("application_date"),
            } for r in filtered])
            st.dataframe(df, width='stretch', hide_index=True)

    if st.session_state.pop("_export_refs", False):
        df_export = pd.DataFrame(refs)
        st.download_button(
            "Download referrals.csv",
            df_export.to_csv(index=False),
            "referrals.csv",
            "text/csv",
            width='stretch',
        )

# =========================================================
# TAB: Edit (two-panel)
# =========================================================
with tab_edit:
    left, right = st.columns([2, 3], gap="large")  # [web:608]

    with left:
        with st.container(border=True):
            st.subheader("Select referral")

            if not refs:
                st.info("No referrals loaded. Go to Overview and press Reload.")
            else:
                labels = []
                id_by_label: Dict[str, int] = {}
                for r in refs:
                    rid = r.get("id")
                    referrer_id = r.get("referrer_id")
                    referrer = users_by_id.get(int(referrer_id)) if referrer_id else (r.get("referrer_name") or "")
                    label = f"{referrer} — {r.get('position')} @ {r.get('company')} (id:{rid})"
                    labels.append(label)
                    if rid is not None:
                        id_by_label[label] = int(rid)

                choice = st.selectbox("Referral", ["-- none --"] + labels, key="ref_edit_select")
                if choice != "-- none --":
                    st.session_state.selected_referral_id = id_by_label.get(choice)

                if st.button("Clear", width='stretch'):
                    _clear_selection()
                    st.rerun()

    with right:
        with st.container(border=True):
            st.subheader("Details & actions")

            editing_id = st.session_state.get("selected_referral_id")
            if not editing_id:
                st.info("Select a referral on the left to edit.")
                st.stop()

            api_client.set_token(token)
            with st.spinner("Loading referral..."):
                try:
                    editing_ref = referral_service.get_referral(str(editing_id))
                except Exception:
                    editing_ref = None

            if not editing_ref:
                st.error("Failed to load referral details.")
                st.stop()

            # Summary (instead of st.json)
            st.markdown(f"**Referral ID:** {editing_ref.get('id')}")
            st.caption(f"{_safe_text(editing_ref.get('position'))} @ {_safe_text(editing_ref.get('company'))}")

            with st.expander("Raw data (debug)", expanded=False):
                st.json(editing_ref)

            st.divider()

            # Build user dropdown once
            user_options: Dict[str, int] = {}
            for u in users or []:
                try:
                    uid = u.get("id") if isinstance(u, dict) else getattr(u, "id", None)
                    if uid is None:
                        continue
                    first = (u.get("first_name") if isinstance(u, dict) else getattr(u, "first_name", None)) or ""
                    last = (u.get("last_name") if isinstance(u, dict) else getattr(u, "last_name", "")) or ""
                    email = (u.get("email") if isinstance(u, dict) else getattr(u, "email", "")) or ""
                    display = f"{(first + ' ' + last).strip() or email} (id:{uid})"
                    user_options[display] = int(uid)
                except Exception:
                    continue

            with st.form("edit_referral_form"):
                c1, c2 = st.columns(2)

                with c1:
                    if user_options:
                        current_referrer_id = editing_ref.get("referrer_id")
                        default_label = next((k for k, v in user_options.items() if v == current_referrer_id), list(user_options.keys())[0])
                        selected_ref = st.selectbox("Referrer", options=list(user_options.keys()), index=list(user_options.keys()).index(default_label))
                        referrer_id = user_options[selected_ref]
                    else:
                        referrer_id = st.number_input("Referrer ID", min_value=1, step=1, value=int(editing_ref.get("referrer_id") or 1))

                    company = st.text_input("Company", value=_safe_text(editing_ref.get("company")))
                    position = st.text_input("Position", value=_safe_text(editing_ref.get("position")))

                with c2:
                    status_opts = ["Pending", "Applied", "Under Review", "Interview Scheduled", "Accepted", "Rejected"]
                    cur_status = editing_ref.get("status")
                    status_idx = status_opts.index(cur_status) if cur_status in status_opts else 0
                    status = st.selectbox("Status", options=status_opts, index=status_idx)

                    application_date = st.date_input("Application date", value=_parse_date(editing_ref.get("application_date")))
                    notes = st.text_area("Notes", value=_safe_text(editing_ref.get("notes")))

                save_btn = st.form_submit_button("Save changes", type="primary", width='stretch')  # [web:757]
                cancel_btn = st.form_submit_button("Cancel", width='stretch')  # [web:757]

            if cancel_btn:
                st.rerun()

            if save_btn:
                if not company or not position:
                    st.error("Company and Position are required.")
                else:
                    payload = {
                        "referrer_id": int(referrer_id),
                        "company": company,
                        "position": position,
                        "status": status,
                        "application_date": application_date.isoformat(),
                        "notes": notes or "",
                    }
                    with st.spinner("Updating referral..."):
                        try:
                            res = referral_service.update_referral(str(editing_ref.get("id")), payload)
                        except Exception:
                            res = None

                    if res:
                        st.success("Referral updated.")
                        _reload_referrals()
                        st.rerun()
                    else:
                        st.error("Failed to update referral.")

            st.divider()
            st.markdown("### Danger zone")
            confirm = st.checkbox("I understand this will permanently delete this referral.", value=False)
            if st.button("Delete referral", width='stretch', disabled=not confirm):
                with st.spinner("Deleting..."):
                    try:
                        ok = referral_service.delete_referral(str(editing_id))
                    except Exception:
                        ok = False
                if ok:
                    st.success("Referral deleted.")
                    _reload_referrals()
                    _clear_selection()
                    st.rerun()
                else:
                    st.error("Failed to delete referral.")

# =========================================================
# TAB: Create
# =========================================================
with tab_create:
    with st.container(border=True):
        st.subheader("Create referral")
        st.caption("Add a new referral opportunity and link it to a.criteria: a referrer in your network.")

        # user dropdown
        user_options: Dict[str, int] = {}
        for u in users or []:
            try:
                uid = u.get("id") if isinstance(u, dict) else getattr(u, "id", None)
                if uid is None:
                    continue
                first = (u.get("first_name") if isinstance(u, dict) else getattr(u, "first_name", None)) or ""
                last = (u.get("last_name") if isinstance(u, dict) else getattr(u, "last_name", "")) or ""
                email = (u.get("email") if isinstance(u, dict) else getattr(u, "email", "")) or ""
                display = f"{(first + ' ' + last).strip() or email} (id:{uid})"
                user_options[display] = int(uid)
            except Exception:
                continue

        with st.form("referral_create_form"):
            c1, c2 = st.columns(2)

            with c1:
                if user_options:
                    selected_ref = st.selectbox("Referrer", options=list(user_options.keys()), index=0)
                    referrer_id = user_options[selected_ref]
                else:
                    st.info("No users available to select as referrer.")
                    referrer_id = st.number_input("Referrer ID", min_value=1, step=1, value=1)

                company = st.text_input("Company")
                position = st.text_input("Position")

            with c2:
                status_opts = ["Pending", "Applied", "Under Review", "Interview Scheduled", "Accepted", "Rejected"]
                status = st.selectbox("Status", options=status_opts, index=0)
                application_date = st.date_input("Application date", value=datetime.now().date())
                notes = st.text_area("Notes")

            create_btn = st.form_submit_button("Create referral", type="primary", width='stretch')  # [web:757]
            reset_btn = st.form_submit_button("Reset", width='stretch')  # [web:757]

        if reset_btn:
            st.rerun()

        if create_btn:
            if not company or not position:
                st.error("Company and Position are required.")
            else:
                payload = {
                    "referrer_id": int(referrer_id),
                    "company": company,
                    "position": position,
                    "status": status,
                    "application_date": application_date.isoformat(),
                    "notes": notes or "",
                }
                with st.spinner("Creating referral..."):
                    try:
                        res = referral_service.create_referral(payload)
                    except Exception:
                        res = None
                if res:
                    st.success("Referral created.")
                    _reload_referrals()
                    st.rerun()
                else:
                    st.error("Failed to create referral.")

with st.expander("Tips", expanded=False):
    st.write("Use statuses consistently and keep notes short (what you need to do next).")
