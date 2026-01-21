"""
Custom styling for SixPaths application
Applies navy/blue theme with gold accents
"""
import streamlit as st


def apply_custom_css():
    """Apply custom CSS styling to the Streamlit app"""
    st.markdown("""
    <style>
        /* Main color scheme */
        :root {
            --primary-navy: #1E3A8A;
            --secondary-blue: #3B82F6;
            --accent-gold: #F59E0B;
            --background-light: #F8FAFC;
            --text-dark: #1E293B;
        }
        
        /* Main container styling */
        .main {
            background-color: var(--background-light);
        }
        
        /* Headers */
        h1, h2, h3 {
            color: var(--primary-navy) !important;
            font-weight: 600 !important;
        }
        
        /* Buttons */
        .stButton > button {
            background-color: var(--primary-navy);
            color: white;
            border-radius: 8px;
            border: none;
            padding: 0.5rem 1rem;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            background-color: var(--secondary-blue);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        /* Form inputs */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div > select {
            border-radius: 6px;
            border: 1px solid #CBD5E1;
        }
        
        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: var(--primary-navy);
        }
        
        [data-testid="stSidebar"] * {
            color: white !important;
        }
        
        /* Metrics */
        [data-testid="stMetricValue"] {
            color: var(--primary-navy);
            font-size: 2rem;
            font-weight: 700;
        }
        
        [data-testid="stMetricLabel"] {
            color: var(--text-dark);
            font-weight: 500;
        }
        
        /* Tables */
        .dataframe {
            border-radius: 8px;
            overflow: hidden;
        }
        
        /* Cards */
        .element-container {
            border-radius: 8px;
        }
        
        /* Success messages */
        .stSuccess {
            background-color: #D1FAE5;
            color: #065F46;
            border-radius: 6px;
            padding: 1rem;
        }
        
        /* Error messages */
        .stError {
            background-color: #FEE2E2;
            color: #991B1B;
            border-radius: 6px;
            padding: 1rem;
        }
        
        /* Info messages */
        .stInfo {
            background-color: #DBEAFE;
            color: #1E40AF;
            border-radius: 6px;
            padding: 1rem;
        }
        
        /* Divider */
        hr {
            margin: 2rem 0;
            border: none;
            border-top: 2px solid #E2E8F0;
        }
        
        /* Network graph container */
        iframe {
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        /* Login form styling */
        .login-container {
            max-width: 400px;
            margin: 0 auto;
            padding: 2rem;
            background-color: white;
            border-radius: 12px;
            box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
        }
        
        /* Navigation tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 0.75rem 1.5rem;
            font-weight: 500;
            color: var(--text-dark);
        }
        
        .stTabs [aria-selected="true"] {
            color: var(--primary-navy);
            border-bottom: 3px solid var(--accent-gold);
        }
        
        /* Responsive design */
        @media (max-width: 768px) {
            .main {
                padding: 1rem;
            }
            
            h1 {
                font-size: 1.75rem !important;
            }
            
            h2 {
                font-size: 1.5rem !important;
            }
            
            h3 {
                font-size: 1.25rem !important;
            }
        }
    </style>
    """, unsafe_allow_html=True)


def display_metric_card(label, value, icon=""):
    """Display a styled metric card"""
    st.markdown(f"""
    <div style="
        background-color: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        text-align: center;
    ">
        <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
        <div style="font-size: 2rem; font-weight: 700; color: #1E3A8A;">{value}</div>
        <div style="font-size: 0.875rem; color: #64748B; font-weight: 500;">{label}</div>
    </div>
    """, unsafe_allow_html=True)
