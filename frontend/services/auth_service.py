"""Simple auth service for Streamlit frontend.

Provides a single function `authenticate` which posts OAuth2-compatible
form data (`application/x-www-form-urlencoded`) to the FastAPI login
endpoint and returns the parsed JSON or an error dict.
"""
import os
import requests
import streamlit as st
from typing import Optional, Dict, Any


def _get_api_base() -> str:
    # Prefer Streamlit secrets, then env var, then localhost default
    try:
        api_base = st.secrets.get("API_BASE_URL")
    except Exception:
        api_base = None
    if not api_base:
        api_base = os.getenv("API_BASE_URL", "http://localhost:8000")
    return api_base


def authenticate(username: str, password: str, api_base_url: Optional[str] = None, timeout: int = 5) -> Dict[str, Any]:
    """Authenticate against backend and return JSON response on success.

    Sends form-encoded data fields `username` and `password` (OAuth2 compatible).

    Returns:
      - On success: dict parsed from JSON (expected to contain `access_token`, `token_type`).
      - On failure: dict with `error` and optional `status_code`.
    """
    if not api_base_url:
        api_base_url = _get_api_base()

    url = api_base_url.rstrip("/") + "/auth/login"

    try:
        resp = requests.post(url, data={"username": username, "password": password}, timeout=timeout)
        # If status is 200 OK, parse JSON
        if resp.status_code == 200:
            try:
                return resp.json()
            except Exception:
                return {"error": "Invalid JSON response from server", "status_code": resp.status_code}

        # Non-200: try to extract JSON error, otherwise raw text
        try:
            return {"error": resp.json(), "status_code": resp.status_code}
        except Exception:
            return {"error": resp.text or f"HTTP {resp.status_code}", "status_code": resp.status_code}

    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
