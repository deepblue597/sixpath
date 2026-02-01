"""
Centralized API service initialization
Import services from here to ensure consistent client across all pages
"""
import os
import streamlit as st
from .api_call import APIClient , AuthUserService , UserService , ConnectionService  , ReferralService

@st.cache_resource
def get_api_client():
    """Initialize and cache the API client"""
    api_base = None
    try:
        api_base = st.secrets.get("API_BASE_URL")
    except Exception:
        api_base = None

    # Ensure we pass a str to APIClient and fall back to env/default when missing
    base_url = str(api_base) if api_base is not None else os.getenv("API_BASE_URL", "http://localhost:8000")
    
    return APIClient(base_url=base_url)

@st.cache_resource
def get_services():
    """Initialize and cache all API services"""
    client = get_api_client()
    
    return {
        'auth': AuthUserService(client),
        'user': UserService(client),
        'connection': ConnectionService(client),
        'referral': ReferralService(client)
    }

# Convenience functions for individual services
def get_auth_service() -> AuthUserService:
    return get_services()['auth']

def get_user_service() -> UserService:
    return get_services()['user']

def get_connection_service() -> ConnectionService:
    return get_services()['connection']

def  get_referral_service() -> ReferralService:
    return get_services()['referral']
