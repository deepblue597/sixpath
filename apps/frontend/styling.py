"""
Custom styling for SixPaths application
Applies navy/blue theme with gold accents
"""
import streamlit as st


def apply_custom_css():
    st.markdown("""
    <style>
      :root {
        --primary-navy: #1E3A8A;
        --secondary-blue: #3B82F6;
        --accent-gold: #F59E0B;
        --bg: #F8FAFC;
        --card-bg: #FFFFFF;
        --text: #0F172A;
        --muted: #64748B;
        --border: #E2E8F0;
      }

      /* Page background */
      [data-testid="stAppViewContainer"] {
        background: var(--bg);
      }

      /* Headings */
      h1, h2, h3 {
        color: var(--primary-navy) !important;
        font-weight: 650 !important;
        letter-spacing: -0.02em;
      }

      /* Buttons: soften + consistent */
      .stButton > button {
        border-radius: 10px;
        border: 1px solid rgba(15, 23, 42, 0.08);
        padding: 0.5rem 1rem;
        font-weight: 600;
      }
      .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(2, 6, 23, 0.08);
      }

      /* Inputs: consistent border + focus */
      .stTextInput input, .stTextArea textarea, .stSelectbox select {
        border-radius: 10px !important;
        border: 1px solid var(--border) !important;
      }

      /* Sidebar: color background, don’t force * everything to white */
      [data-testid="stSidebar"] {
        background: #0B1F52;
      }
      [data-testid="stSidebar"] label,
      [data-testid="stSidebar"] p,
      [data-testid="stSidebar"] span,
      [data-testid="stSidebar"] a,
      [data-testid="stSidebar"] h1,
      [data-testid="stSidebar"] h2,
      [data-testid="stSidebar"] h3 {
        color: #FFFFFF !important;
      }

      /* Card utility class (use in st.markdown blocks) */
      .six-card {
        background: var(--card-bg);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 1rem 1.25rem;
        box-shadow: 0 8px 22px rgba(2, 6, 23, 0.06);
      }
      .six-card .muted {
        color: var(--muted);
        font-size: 0.9rem;
      }

      /* Messages: keep subtle */
      [data-testid="stAlert"] {
        border-radius: 12px;
      }

      /* Divider */
      hr {
        margin: 1.5rem 0;
        border: none;
        border-top: 1px solid var(--border);
      }

      /* Embedded network iframe */
      iframe {
        border-radius: 14px;
        box-shadow: 0 8px 22px rgba(2, 6, 23, 0.10);
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
