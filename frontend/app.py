"""
SixPath - Main Streamlit entry
Provides sidebar navigation and runs page scripts from `pages/`.
"""
import runpy
from pathlib import Path
import streamlit as st

# Page configuration (UI requirements)
st.set_page_config(
    page_title="SixPath",
    page_icon="an icon with a path",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state variables
for key, default in (
    ("logged_in", False),
    ("username", None),
    ("selected_node_id", None),
    ("user_data", None),
    ("connections", None),
    ("referrals", None),
    ("current_page", None),
):
    if key not in st.session_state:
        st.session_state[key] = default

# Apply custom CSS (project styling helper)
from styling import apply_custom_css
apply_custom_css()

BASE_DIR = Path(__file__).parent


def load_page(page_path: str):
    """Execute a page script from the `pages/` folder.

    This function runs the target page as a separate script and stops
    further rendering of the main app so only the page UI shows.
    """
    target = BASE_DIR / page_path
    if not target.exists():
        st.error(f"Page not found: {page_path}")
        st.stop()
    try:
        st.session_state.current_page = page_path
        runpy.run_path(str(target), run_name="__main__")
    except Exception as e:
        st.exception(e)
    finally:
        st.stop()


# Navigation structure: (Section title, [(label, page_path, icon), ...])
NAVIGATION = [
    (
        "Authentication",
        [
            ("Login", "pages/login.py", "🔐"),
            ("Create Account", "pages/create_account.py", "🆕"),
            ("Forgot Password", "pages/forgot_password.py", "🔑"),
        ],
    ),
    (
        "User Management",
        [
            ("Edit User", "pages/update_user.py", "👤"),
            ("Posts", "pages/posts.py", "📝"),
        ],
    ),
    (
        "Connections",
        [
            ("Connections CRUD", "pages/connections_crud.py", "🔗"),
        ],
    ),
    (
        "Referrals",
        [
            ("Referrals CRUD", "pages/referrals_crud.py", "🎯"),
        ],
    ),
    (
        "Dashboard",
        [
            ("Connections Dashboard", "pages/dashboard.py", "📊"),
        ],
    ),
]


# Sidebar navigation UI
with st.sidebar:
    st.markdown("## 🔗 SixPath")
    st.markdown("### Navigation")
    for section, items in NAVIGATION:
        with st.expander(section, expanded=False):
            for label, path, icon in items:
                btn_label = f"{icon} {label}"
                if st.button(btn_label, key=f"nav_{path}"):
                    load_page(path)

    st.divider()
    st.markdown("### Session")
    if st.session_state.logged_in:
        display_name = st.session_state.username or (
            (
                (st.session_state.user_data.get("first_name", "") + " " + st.session_state.user_data.get("last_name", ""))
                .strip()
            )
            if st.session_state.user_data
            else ""
        )
        st.success(f"Signed in as {display_name}")
        if st.button("Sign out"):
            st.session_state.logged_in = False
            st.session_state.token = None
            st.session_state.user_data = None
            st.experimental_rerun()
    else:
        st.info("Not signed in")

    st.divider()
    st.markdown("### Quick Links")
    if st.button("Go to Dashboard"):
        load_page("pages/dashboard.py")
    if st.button("Manage Connections"):
        load_page("pages/connections_crud.py")
    if st.button("Manage Referrals"):
        load_page("pages/referrals_crud.py")


# Main content header and quick access
st.title("🔗 SixPath")
st.markdown(
    """
SixPath is a professional networking visualization tool.

Use the sidebar to navigate between Authentication, User Management, Connections, Referrals, and Dashboard.
"""
)

cols = st.columns(3)
with cols[0]:
    if st.button("📊 Dashboard (Open)"):
        load_page("pages/dashboard.py")
with cols[1]:
    if st.button("🎯 Referrals (Open)"):
        load_page("pages/referrals_crud.py")
with cols[2]:
    if st.button("👤 Edit Profile (Open)"):
        load_page("pages/update_user.py")

st.divider()

# Home cards
card_col1, card_col2, card_col3 = st.columns(3)
with card_col1:
    st.markdown("### Authentication")
    st.button("Login", key="home_login", help="Open the Login page", on_click=lambda: load_page("pages/login.py"))
with card_col2:
    st.markdown("### User Management")
    st.button("Edit User", key="home_edit_user", help="Open Edit User page", on_click=lambda: load_page("pages/update_user.py"))
with card_col3:
    st.markdown("### Connections")
    st.button("Connections CRUD", key="home_connections", help="Open Connections CRUD page", on_click=lambda: load_page("pages/connections_crud.py"))

st.divider()

st.markdown(
    """
**Quick tips**
- Use the sidebar to jump to any section.
- Login first to access user-specific features.
"""
)
