"""
API Client for SixPaths Streamlit Frontend
Handles communication with FastAPI backend
"""
import requests
import streamlit as st
from typing import Optional, List, Dict, Any


class APIClient:
    """Client for communicating with FastAPI backend"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token: Optional[str] = None
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with authorization token"""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response and errors"""
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                st.error("🔒 Session expired. Please login again.")
                st.session_state.logged_in = False
                st.session_state.token = None
                st.switch_page("pages/01_Login.py")
            elif response.status_code == 404:
                return None
            else:
                error_detail = response.json().get("detail", str(e))
                st.error(f"API Error: {error_detail}")
            return None
        except Exception as e:
            st.error(f"Connection error: {str(e)}")
            return None
    
    # Authentication endpoints
    
    def login(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Login to the API
        POST /auth/login
        """
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                data={
                    "username": username,  # FastAPI OAuth2PasswordRequestForm uses 'username'
                    "password": password
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                return data
            else:
                error_detail = response.json().get("detail", "Login failed")
                st.error(f"❌ {error_detail}")
                return None
        except Exception as e:
            st.error(f"❌ Connection error: {str(e)}")
            return None
    
    def register(self, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a new user (requires authentication)
        POST /users/
        """
        try:
            response = requests.post(
                f"{self.base_url}/users/",
                json=user_data,
                headers=self._get_headers()
            )
            return self._handle_response(response)
        except Exception as e:
            st.error(f"Error creating user: {str(e)}")
            return None
    
    # User endpoints
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """
        Get current user information
        GET /users/me
        """
        try:
            response = requests.get(
                f"{self.base_url}/users/me",
                headers=self._get_headers()
            )
            return self._handle_response(response)
        except Exception as e:
            st.error(f"Error fetching user: {str(e)}")
            return None
    
    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user by ID
        GET /users/{user_id}
        """
        try:
            response = requests.get(
                f"{self.base_url}/users/{user_id}",
                headers=self._get_headers()
            )
            return self._handle_response(response)
        except Exception as e:
            return None
    
    def get_all_users(self, offset: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get all users
        GET /users/
        """
        try:
            response = requests.get(
                f"{self.base_url}/users/",
                params={"offset": offset, "limit": limit},
                headers=self._get_headers()
            )
            result = self._handle_response(response)
            return result if result else []
        except Exception as e:
            st.error(f"Error fetching all users: {str(e)}")
            return []
    
    def update_user(self, user_id: int, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update user information
        PUT /users/{user_id}
        """
        try:
            response = requests.put(
                f"{self.base_url}/users/{user_id}",
                json=user_data,
                headers=self._get_headers()
            )
            return self._handle_response(response)
        except Exception as e:
            st.error(f"Error updating user: {str(e)}")
            return None
    
    # Connection endpoints
    
    def get_my_connections_with_users(self) -> List[Dict[str, Any]]:
        """
        Get current user's connections with full user details
        Fetches connections and enriches with user information
        """
        from utils.data_transformer import transform_user_to_connection
        
        try:
            # Get current user to get their ID
            current_user = self.get_current_user()
            if not current_user:
                return []
            
            user_id = current_user.get('id')
            
            # Get connections for this user
            response = requests.get(
                f"{self.base_url}/connections/user/{user_id}",
                headers=self._get_headers()
            )
            
            connections = self._handle_response(response)
            if not connections:
                return []
            
            # Fetch user details for each connection
            enriched_connections = []
            for conn in connections:
                # Determine which person is the other user
                other_user_id = conn['person2_id'] if conn['person1_id'] == user_id else conn['person1_id']
                
                # Fetch user details
                user = self.get_user(other_user_id)
                if user:
                    # Transform to frontend format
                    enriched_conn = transform_user_to_connection(user, conn)
                    enriched_connections.append(enriched_conn)
            
            return enriched_connections
            
        except Exception as e:
            st.error(f"Error fetching connections: {str(e)}")
            return []
    
    def get_my_connections(self, offset: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get current user's connections
        GET /connections/me
        """
        try:
            response = requests.get(
                f"{self.base_url}/connections/me",
                params={"offset": offset, "limit": limit},
                headers=self._get_headers()
            )
            result = self._handle_response(response)
            return result if result else []
        except Exception as e:
            st.error(f"Error fetching connections: {str(e)}")
            return []
    
    def get_connection(self, connection_id: int) -> Optional[Dict[str, Any]]:
        """
        Get connection by ID
        GET /connections/{connection_id}
        """
        try:
            response = requests.get(
                f"{self.base_url}/connections/{connection_id}",
                headers=self._get_headers()
            )
            return self._handle_response(response)
        except Exception as e:
            return None
    
    def create_connection(self, connection_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a new connection
        POST /connections/
        """
        try:
            response = requests.post(
                f"{self.base_url}/connections/",
                json=connection_data,
                headers=self._get_headers()
            )
            return self._handle_response(response)
        except Exception as e:
            st.error(f"Error creating connection: {str(e)}")
            return None
    
    def update_connection(self, connection_id: int, connection_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update connection
        PUT /connections/{connection_id}
        """
        try:
            response = requests.put(
                f"{self.base_url}/connections/{connection_id}",
                json=connection_data,
                headers=self._get_headers()
            )
            return self._handle_response(response)
        except Exception as e:
            st.error(f"Error updating connection: {str(e)}")
            return None
    
    def delete_connection(self, connection_id: int) -> bool:
        """
        Delete connection
        DELETE /connections/{connection_id}
        """
        try:
            response = requests.delete(
                f"{self.base_url}/connections/{connection_id}",
                headers=self._get_headers()
            )
            return response.status_code == 200
        except Exception as e:
            st.error(f"Error deleting connection: {str(e)}")
            return False
    
    # Referral endpoints
    
    def get_my_referrals_with_users(self) -> List[Dict[str, Any]]:
        """
        Get current user's referrals with referrer user details
        """
        from utils.data_transformer import transform_referral
        
        try:
            # Get referrals
            response = requests.get(
                f"{self.base_url}/referrals/me",
                params={"offset": 0, "limit": 100},
                headers=self._get_headers()
            )
            
            referrals = self._handle_response(response)
            if not referrals:
                return []
            
            # Enrich with referrer data
            enriched_referrals = []
            for referral in referrals:
                referrer_id = referral.get('referrer_id')
                referrer = self.get_user(referrer_id) if referrer_id else None
                enriched_ref = transform_referral(referral, referrer)
                enriched_referrals.append(enriched_ref)
            
            return enriched_referrals
            
        except Exception as e:
            st.error(f"Error fetching referrals: {str(e)}")
            return []
    
    def get_my_referrals(self, offset: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get current user's referrals
        GET /referrals/me
        """
        try:
            response = requests.get(
                f"{self.base_url}/referrals/me",
                params={"offset": offset, "limit": limit},
                headers=self._get_headers()
            )
            result = self._handle_response(response)
            return result if result else []
        except Exception as e:
            st.error(f"Error fetching referrals: {str(e)}")
            return []
    
    def get_referral(self, referral_id: int) -> Optional[Dict[str, Any]]:
        """
        Get referral by ID
        GET /referrals/{referral_id}
        """
        try:
            response = requests.get(
                f"{self.base_url}/referrals/{referral_id}",
                headers=self._get_headers()
            )
            return self._handle_response(response)
        except Exception as e:
            return None
    
    def create_referral(self, referral_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a new referral
        POST /referrals/
        """
        try:
            response = requests.post(
                f"{self.base_url}/referrals/",
                json=referral_data,
                headers=self._get_headers()
            )
            return self._handle_response(response)
        except Exception as e:
            st.error(f"Error creating referral: {str(e)}")
            return None
    
    def update_referral(self, referral_id: int, referral_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update referral
        PUT /referrals/{referral_id}
        """
        try:
            response = requests.put(
                f"{self.base_url}/referrals/{referral_id}",
                json=referral_data,
                headers=self._get_headers()
            )
            return self._handle_response(response)
        except Exception as e:
            st.error(f"Error updating referral: {str(e)}")
            return None
    
    def delete_referral(self, referral_id: int) -> bool:
        """
        Delete referral
        DELETE /referrals/{referral_id}
        """
        try:
            response = requests.delete(
                f"{self.base_url}/referrals/{referral_id}",
                headers=self._get_headers()
            )
            return response.status_code == 200
        except Exception as e:
            st.error(f"Error deleting referral: {str(e)}")
            return False


def get_api_client() -> APIClient:
    """Get or create API client instance in session state"""
    if 'api_client' not in st.session_state:
        # Get API URL from secrets or use default
        api_url = "http://localhost:8000"
        try:
            api_url = st.secrets.get("API_URL", "http://localhost:8000")
        except (FileNotFoundError, KeyError):
            # No secrets file or key, use default
            pass
        
        st.session_state.api_client = APIClient(base_url=api_url)
    
    # Set token if available
    if 'token' in st.session_state and st.session_state.token:
        st.session_state.api_client.token = st.session_state.token
    
    return st.session_state.api_client
