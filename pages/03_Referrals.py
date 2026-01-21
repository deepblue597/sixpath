"""
Referrals Page for SixPaths
Manage incoming referrals with search and filters
"""
import streamlit as st
import pandas as pd
from utils.styling import apply_custom_css
from api.api_client import get_api_client
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Referrals - SixPaths",
    page_icon="🎯",
    layout="wide"
)

apply_custom_css()

# Check authentication
if not st.session_state.get('logged_in', False):
    st.warning("⚠️ Please login first")
    st.switch_page("pages/01_Login.py")

# Initialize referral action state
if 'show_referral_details' not in st.session_state:
    st.session_state.show_referral_details = None

# Page header
st.title("🎯 Referrals Management")
st.markdown("Track and manage your job referrals from your network")

# Create/Edit Referral Form
if st.session_state.get('show_referral_form', False):
    st.markdown("---")
    
    # Determine if editing or creating
    editing_id = st.session_state.get('editing_referral_id', None)
    form_title = "✏️ Edit Referral" if editing_id else "➕ Create New Referral"
    st.markdown(f"### {form_title}")
    
    # Find referral being edited if any
    editing_referral = None
    if editing_id:
        editing_referral = next((r for r in st.session_state.referrals if r.get('id') == editing_id), None)
    
    with st.form("referral_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            # Get list of connections for referrer selection
            connection_options = {}
            if st.session_state.get('connections'):
                for conn in st.session_state.connections:
                    conn_id = conn.get('id')
                    conn_name = conn.get('name', 'Unknown')
                    if conn_id:
                        connection_options[f"{conn_name} (ID: {conn_id})"] = conn_id
            
            # Referrer selection
            if editing_referral:
                default_referrer = next(
                    (key for key, val in connection_options.items() if val == editing_referral.get('referrer_id')),
                    list(connection_options.keys())[0] if connection_options else None
                )
            else:
                default_referrer = list(connection_options.keys())[0] if connection_options else None
            
            selected_referrer = st.selectbox(
                "Referrer *",
                options=list(connection_options.keys()) if connection_options else ["No connections available"],
                index=list(connection_options.keys()).index(default_referrer) if default_referrer and connection_options else 0,
                help="Select who referred you"
            )
            
            company = st.text_input(
                "Company *",
                value=editing_referral.get('company', '') if editing_referral else '',
                placeholder="e.g., Microsoft"
            )
            
            position = st.text_input(
                "Position *",
                value=editing_referral.get('position', '') if editing_referral else '',
                placeholder="e.g., Senior Software Engineer"
            )
        
        with col2:
            status_options = ["Pending", "Applied", "Under Review", "Interview Scheduled", "Accepted", "Rejected"]
            status = st.selectbox(
                "Status *",
                options=status_options,
                index=status_options.index(editing_referral['status']) if editing_referral and editing_referral.get('status') in status_options else 0
            )
            
            application_date = st.date_input(
                "Application Date",
                value=datetime.strptime(editing_referral['application_date'], '%Y-%m-%d').date() if editing_referral and editing_referral.get('application_date') else datetime.now().date()
            )
            
            notes = st.text_area(
                "Notes",
                value=editing_referral.get('notes', '') if editing_referral else '',
                placeholder="Any additional notes about this referral..."
            )
        
        # Form buttons
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            submitted = st.form_submit_button("💾 Save", use_container_width=True, type="primary")
        
        with col2:
            cancelled = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        if submitted:
            # Validate required fields
            if not company or not position:
                st.error("⚠️ Please fill in all required fields (marked with *)")
            elif not connection_options:
                st.error("⚠️ No connections available. Please add connections first.")
            else:
                # Get the selected referrer ID
                referrer_id = connection_options.get(selected_referrer)
                
                if referrer_id:
                    api_client = get_api_client()
                    
                    try:
                        # Prepare referral data
                        referral_data = {
                            "referrer_id": referrer_id,
                            "company": company,
                            "position": position,
                            "status": status,
                            "application_date": application_date.isoformat(),
                            "notes": notes or ""
                        }
                        
                        if editing_id:
                            # Update existing referral
                            response = api_client.update_referral(editing_id, referral_data)
                            st.success(f"✅ Referral for {position} at {company} updated successfully!")
                        else:
                            # Create new referral
                            response = api_client.create_referral(referral_data)
                            st.success(f"✅ New referral for {position} at {company} created successfully!")
                        
                        # Refresh referrals from backend
                        user_id = st.session_state.get('user_id')
                        if user_id:
                            referrals_response = api_client.get_my_referrals_with_users()
                            st.session_state.referrals = referrals_response
                        
                        # Close form
                        st.session_state.show_referral_form = False
                        st.session_state.editing_referral_id = None
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error saving referral: {str(e)}")
                else:
                    st.error("⚠️ Please select a valid referrer")
        
        if cancelled:
            st.session_state.show_referral_form = False
            st.session_state.editing_referral_id = None
            st.rerun()
    
    st.markdown("---")


# Sidebar navigation
with st.sidebar:
    st.markdown("### 🧭 Navigation")
    
    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("streamlit_app.py")
    
    if st.button("📊 Dashboard", use_container_width=True):
        st.switch_page("pages/02_Dashboard.py")
    
    if st.button("👤 Profile", use_container_width=True):
        st.switch_page("pages/04_Edit_Profile.py")
    
    st.divider()
    
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.switch_page("pages/01_Login.py")

# Main content
if st.session_state.referrals:
    # Summary metrics
    st.markdown("### 📊 Referral Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Referrals", len(st.session_state.referrals))
    
    with col2:
        pending = sum(1 for r in st.session_state.referrals if r['status'] in ['Pending', 'Under Review'])
        st.metric("Pending", pending, delta=f"{pending} active")
    
    with col3:
        interviews = sum(1 for r in st.session_state.referrals if 'Interview' in r['status'])
        st.metric("Interviews", interviews)
    
    with col4:
        accepted = sum(1 for r in st.session_state.referrals if r['status'] == 'Accepted')
        st.metric("Accepted", accepted, delta="✅" if accepted > 0 else "")
    
    st.divider()
    
    # Filters
    st.markdown("### 🔍 Filters")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Sector filter
        all_sectors = sorted(set(r['sector'] for r in st.session_state.referrals))
        selected_sectors = st.multiselect(
            "Sector",
            options=all_sectors,
            default=all_sectors
        )
    
    with col2:
        # Company filter
        all_companies = sorted(set(r['company'] for r in st.session_state.referrals))
        selected_companies = st.multiselect(
            "Company",
            options=all_companies,
            default=all_companies
        )
    
    with col3:
        # Status filter
        all_statuses = sorted(set(r['status'] for r in st.session_state.referrals))
        selected_statuses = st.multiselect(
            "Status",
            options=all_statuses,
            default=all_statuses
        )
    
    # Search bar and Create button
    col1, col2 = st.columns([4, 1])
    with col1:
        search_query = st.text_input("🔍 Search referrals", placeholder="Search by referrer name, company, position...")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Add spacing
        if st.button("➕ New Referral", use_container_width=True, type="primary"):
            st.session_state.show_referral_form = True
            st.session_state.editing_referral_id = None
            st.rerun()
    
    st.divider()
    
    # Filter referrals
    filtered_referrals = [
        r for r in st.session_state.referrals
        if r['sector'] in selected_sectors
        and r['company'] in selected_companies
        and r['status'] in selected_statuses
    ]
    
    # Apply search
    if search_query:
        search_lower = search_query.lower()
        filtered_referrals = [
            r for r in filtered_referrals
            if search_lower in r['referrer_name'].lower()
            or search_lower in r['company'].lower()
            or search_lower in r['position'].lower()
            or search_lower in r.get('notes', '').lower()
        ]
    
    # Display referrals
    st.markdown(f"### 📋 Referrals ({len(filtered_referrals)} found)")
    
    if filtered_referrals:
        # Create tabs for different views
        tab1, tab2 = st.tabs(["📊 Table View", "📇 Card View"])
        
        with tab1:
            # Table view
            df = pd.DataFrame([{
                "ID": r['id'],
                "Referrer": r['referrer_name'],
                "Company": r['company'],
                "Position": r['position'],
                "Sector": r['sector'],
                "Applied": r['application_date'],
                "Status": r['status'],
                "Last Contact": r['last_interaction']
            } for r in filtered_referrals])
            
            # Status color coding
            def color_status(val):
                colors = {
                    'Accepted': 'background-color: #D1FAE5',
                    'Interview Scheduled': 'background-color: #DBEAFE',
                    'Pending': 'background-color: #FEF3C7',
                    'Under Review': 'background-color: #E0E7FF',
                    'Rejected': 'background-color: #FEE2E2',
                    'Applied': 'background-color: #F3F4F6'
                }
                return colors.get(val, '')
            
            st.dataframe(
                df.style.map(color_status, subset=['Status']),
                use_container_width=True,
                hide_index=True
            )
            
            # Action buttons below table
            st.markdown("#### ⚡ Quick Actions")
            action_cols = st.columns(len(filtered_referrals[:3]))  # Show up to 3
            
            for idx, (col, referral) in enumerate(zip(action_cols, filtered_referrals[:3])):
                with col:
                    if st.button(f"View {referral['referrer_name']}", key=f"view_{referral['id']}", use_container_width=True):
                        st.session_state.show_referral_details = referral['id']
        
        with tab2:
            # Card view
            for referral in filtered_referrals:
                with st.container():
                    # Status badge color
                    status_colors = {
                        'Accepted': '#10B981',
                        'Interview Scheduled': '#3B82F6',
                        'Pending': '#F59E0B',
                        'Under Review': '#8B5CF6',
                        'Rejected': '#EF4444',
                        'Applied': '#6B7280'
                    }
                    status_color = status_colors.get(referral['status'], '#94A3B8')
                    
                    st.markdown(f"""
                    <div style="
                        background-color: white;
                        padding: 1.5rem;
                        border-radius: 12px;
                        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
                        border-left: 4px solid {status_color};
                        margin-bottom: 1rem;
                    ">
                        <div style="display: flex; justify-content: space-between; align-items: start;">
                            <div>
                                <h3 style="margin: 0; color: #1E3A8A;">{referral['position']}</h3>
                                <p style="margin: 0.5rem 0; color: #64748B; font-size: 1.1rem; font-weight: 500;">
                                    {referral['company']} • {referral['sector']}
                                </p>
                            </div>
                            <div style="
                                background-color: {status_color};
                                color: white;
                                padding: 0.5rem 1rem;
                                border-radius: 6px;
                                font-weight: 500;
                                font-size: 0.875rem;
                            ">
                                {referral['status']}
                            </div>
                        </div>
                        <div style="margin-top: 1rem; color: #475569;">
                            <p style="margin: 0.25rem 0;">
                                <strong>Referred by:</strong> {referral['referrer_name']}
                            </p>
                            <p style="margin: 0.25rem 0;">
                                <strong>Applied:</strong> {referral['application_date']}
                            </p>
                            <p style="margin: 0.25rem 0;">
                                <strong>Last Contact:</strong> {referral['last_interaction']}
                            </p>
                        </div>
                        <p style="margin-top: 1rem; color: #64748B; font-style: italic;">
                            {referral.get('notes', 'No notes available')}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Action buttons for each card
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        if st.button("📝 Edit", key=f"edit_{referral['id']}", use_container_width=True):
                            st.session_state.show_referral_form = True
                            st.session_state.editing_referral_id = referral['id']
                            st.rerun()
                    
                    with col2:
                        if st.button("👤 View Referrer", key=f"referrer_{referral['id']}", use_container_width=True):
                            # Find and select the referrer connection
                            st.session_state.selected_node_id = referral['referrer_id']
                            st.switch_page("pages/05_Edit_Connection.py")
                    
                    with col3:
                        if st.button("✉️ Contact", key=f"contact_{referral['id']}", use_container_width=True):
                            st.info(f"Contact feature for {referral['referrer_name']} (to be implemented)")
                    
                    with col4:
                        if st.button("🗑️ Delete", key=f"delete_{referral['id']}", use_container_width=True):
                            # Delete via API
                            api_client = get_api_client()
                            try:
                                api_client.delete_referral(referral['id'])
                                st.success(f"✅ Deleted referral for {referral['position']}")
                                
                                # Refresh referrals from backend
                                user_id = st.session_state.get('user_id')
                                if user_id:
                                    referrals_response = api_client.get_my_referrals_with_users()
                                    st.session_state.referrals = referrals_response
                                
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error deleting referral: {str(e)}")
    else:
        st.info("No referrals match your current filters")
    
    # Export option
    st.divider()
    st.markdown("### 📤 Export")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("Download your referrals data as CSV")
    
    with col2:
        if filtered_referrals:
            df_export = pd.DataFrame(filtered_referrals)
            csv = df_export.to_csv(index=False)
            st.download_button(
                "⬇️ Download CSV",
                csv,
                "referrals.csv",
                "text/csv",
                use_container_width=True
            )

else:
    st.warning("No referrals available. Generate sample data by logging in.")
    if st.button("Go to Login"):
        st.switch_page("pages/01_Login.py")
