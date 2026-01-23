# api_service.py
import requests
from typing import Optional, List, Dict, Any
from .api_models import UserResponse, ConnectionResponse, ReferralResponse

class APIClient:
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url
        #self.api_key = api_key
        self.session = requests.Session()
        self.token = None
        self.default_headers = {"Content-Type": "application/json"}


    def set_token(self, token: str):
        """Set authentication token for all future requests"""
        self.token = token
        self.session.headers.update({"Authorization": f"Bearer {token}"})
    
    def clear_token(self):
        """Remove authentication token"""
        self.token = None
        self.session.headers.pop("Authorization", None)
        
        
    def _get_headers(self, custom_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Build headers with token and merge with custom headers"""
        headers = {
            "Content-Type": "application/json",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        if custom_headers:
            headers.update(custom_headers)
        
        return headers
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Dict:
        url = f"{self.base_url}/{endpoint}"
        final_headers = self._get_headers()
        if headers:
            final_headers.update(headers)
        response = requests.get(url, headers=final_headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def post(self, endpoint: str, data: Optional[Dict] = None, headers: Optional[Dict[str, str]] = None) -> Dict:
        url = f"{self.base_url}/{endpoint}"
        final_headers = self._get_headers()
        if headers:
            final_headers.update(headers)
        response = requests.post(url, headers=final_headers, json=data)
        response.raise_for_status()
        return response.json()

    def post_form(self, endpoint: str, form_data: Optional[Dict] = None, headers: Optional[Dict[str, str]] = None) -> Dict:
        """Post form-encoded data (application/x-www-form-urlencoded)."""
        url = f"{self.base_url}/{endpoint}"
        # Use session.post so session headers (Authorization) are preserved
        # Let requests set the Content-Type for form data automatically.
        req_headers = {}
        if headers:
            req_headers.update(headers)
        response = self.session.post(url, headers=req_headers, data=form_data)
        # If the response is not JSON, return text for debugging
        try:
            response.raise_for_status()
            return response.json()
        except requests.HTTPError:
            try:
                return {"status_code": response.status_code, "text": response.text}
            except Exception:
                raise
    
    def put(self, endpoint: str, data: Optional[Dict] = None, headers: Optional[Dict[str, str]] = None) -> Dict:
        url = f"{self.base_url}/{endpoint}"
        final_headers = self._get_headers()
        if headers:
            final_headers.update(headers)
        response = requests.put(url, headers=final_headers, json=data)
        response.raise_for_status()
        return response.json()
    
    def delete(self, endpoint: str, headers: Optional[Dict[str, str]] = None) -> bool:
        url = f"{self.base_url}/{endpoint}"
        final_headers = self._get_headers()
        if headers:
            final_headers.update(headers)
        response = requests.delete(url, headers=final_headers)
        response.raise_for_status()
        return True
    
class UserService:
    def __init__(self, api_client: APIClient):
        self.api_client = api_client

    def get_user(self, user_id: str) -> Optional[UserResponse]:
        try:
            response = self.api_client.get(f"users/{user_id}")
            return UserResponse(**response)
        except Exception:
            return None
        
    
    def get_users(self, limit: int = 100, offset: int = 0) -> List[UserResponse]:
        try:
            
            params = {"limit": limit, "offset": offset}
            response = self.api_client.get("users", params=params)
            return [UserResponse(**user) for user in response]  # Convert list
        except Exception:
            return []
    #TODO: Use the dataclasses for input and output
    def create_user(self, user_data: Dict) -> Optional[UserResponse]:
        try:
            response = self.api_client.post("users", data=user_data)
            return UserResponse(**response)
        except Exception:
            return None
        #return self.api_client.post("users", data=user_data)

    def update_user(self, user_id: str, user_data: Dict) -> Optional[UserResponse]:
        try:
            response = self.api_client.put(f"users/{user_id}", data=user_data)
            return UserResponse(**response)
        except Exception:
            return None
        #return self.api_client.put(f"users/{user_id}", data=user_data)

    def delete_user(self, user_id: str) -> bool:
        return self.api_client.delete(f"users/{user_id}")

class AuthUserService:
    def __init__(self, api_client: APIClient):
        self.api_client = api_client

    def login(self, username: str, password: str) -> Dict:
        # OAuth2PasswordRequestForm expects form-encoded fields: username and password
        form = {"username": username, "password": password}
        return self.api_client.post_form("auth/login", form_data=form)

    def logout(self) -> Dict:
        #headers = {"Authorization": f"Bearer {token}"}
        return self.api_client.post("auth/logout", data={})
    
    # TODO: The headers are not needed if token is set in APIClient
    def get_current_user(self) -> Optional[UserResponse]:
        #headers = {"Authorization": f"Bearer {token}"}
        try:
            response = self.api_client.get("users/me")
            return UserResponse(**response)
        except Exception:   
            return None
        #return self.api_client.get("users/me")

    def register_user(self, user_data: Dict) -> Dict:
        return self.api_client.post("users/register_user", data=user_data)
    
    def change_password(self, user_id: str, new_password: str) -> Dict:
        data = {"new_password": new_password}
        return self.api_client.post(f"users/{user_id}/change-password", data=data)

class ConnectionService:
    
    def __init__(self, api_client: APIClient):
        self.api_client = api_client
    
    #TODO: create Frontend Data Classes 
    def get_connection(self, connection_id: str) -> Dict:
        return self.api_client.get(f"connections/{connection_id}")
    
    def create_connection(self, connection_data: Dict) -> Dict:
        return self.api_client.post("connections", data=connection_data)

    def delete_connection(self, connection_id: str) -> bool:
        return self.api_client.delete(f"connections/{connection_id}")
    
    def update_connection(self, connection_id: str, connection_data: Dict) -> Dict:
        return self.api_client.put(f"connections/{connection_id}", data=connection_data)
    
    def get_connections_of_user(self, user_id: int) -> List[Dict]:
        # user_id is a path parameter 
        # if there were other params there, would be query and would go inside 
        # params = {"limit": 10, "offset": 0} 
        response = self.api_client.get(f"connections/user/{user_id}")
        return response if isinstance(response, list) else []
    
    def get_all_connections(self) -> List[Dict]:
        response = self.api_client.get("connections/all")
        return response if isinstance(response, list) else []

class ReferralService:
    
    def __init__(self, api_client: APIClient):
        self.api_client = api_client
        
    
    def get_current_user_referrals(self, limit: int = 10, offset: int = 0) -> List[Dict]:
        params = {"limit": limit, "offset": offset}
        response = self.api_client.get("referrals/me", params=params)
        return response if isinstance(response, list) else []
    
    def get_referral(self, referral_id: str) -> Dict:
        return self.api_client.get(f"referrals/{referral_id}")
    
    def create_referral(self, referral_data: Dict) -> Dict:
        return self.api_client.post("referrals", data=referral_data)
    
    def delete_referral(self, referral_id: str) -> bool:
        return self.api_client.delete(f"referrals/{referral_id}")
    
    def update_referral(self, referral_id: str, referral_data: Dict) -> Dict:
        return self.api_client.put(f"referrals/{referral_id}", data=referral_data)
    
    
