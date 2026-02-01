from typing import Optional
import logging
from dao.userDAO import UserDAO
from models.response_models import FilterOptionResponse, UserResponse
from models.input_models import UserCreate, UserUpdate, AccountCreate
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher


# Initialize password hasher with Argon2 (recommended by OWASP)
pwd_context = PasswordHash((
    Argon2Hasher(),  # Primary hasher
))

logger = logging.getLogger(__name__)

# UPDATEBLE_FIELDS = {'first_name', 'last_name', 'email', 'company', 'username',
#                     'sector', 'phone', 'linkedin_url', 'how_i_know_them', 
#                     'when_i_met_them', 'notes'}

class UserService:
    
    def __init__(self, engine):
        self.user_dao = UserDAO(engine)
        
    def get_user(self, user_id: int) -> Optional[UserResponse]:
        user = self.user_dao.get_user_by_id(user_id)
        if user:
            return UserResponse.model_validate(user)
        return None
    
    def create_user(self, user_create: UserCreate) -> Optional[UserResponse]:
        """Create a new contact/connection in the network.
        
        Args:
            user_create: Contact data
            current_user_id: ID of the authenticated user creating this contact
        """
        user_data = user_create.model_dump()
        # Set owner_id to current authenticated user if not already set
        # if current_user_id and 'owner_id' not in user_data:
        #     user_data['owner_id'] = current_user_id
        new_user = self.user_dao.create_user(user_data)
        if new_user:
            return UserResponse.model_validate(new_user)
        return None
    
    
    
    def register_user(self, user_create: AccountCreate) -> Optional[UserResponse]:
        # New user registration with password hashing
        user_data = user_create.model_dump(exclude={'password'})
        user_data['password'] = pwd_context.hash(user_create.password)
        user_data['is_me'] = True  # Ensure this is set for the account owner
        new_user = self.user_dao.create_user(user_data)
        if new_user:
            return UserResponse.model_validate(new_user)
        return None
    
    def verify_user_password(self, username: str, password: str) -> Optional[UserResponse]:
        user = self.user_dao.get_by_username(username)
        if user and user.password and pwd_context.verify(password, user.password):
            return user
        return None
    
    def update_user(self, user_id: int, user_update: UserUpdate) -> Optional[UserResponse]:
        user_data = user_update.model_dump(exclude_unset=True, exclude_none=True) # Only include fields that are set and not None
        updated_user = self.user_dao.update_user(user_id, user_data)
        if updated_user:
            return UserResponse.model_validate(updated_user)
        return None
    # Service layer (your code): Returns bool to communicate success/failure to the route handler. This allows the route to decide how to respond based on whether the deletion worked.
    def delete_user(self, user_id: int) -> bool:
        return self.user_dao.delete_user(user_id)
    
    def get_users(self, limit: int = 100, offset: int = 0) -> list[UserResponse]:
        users = self.user_dao.get_users(limit, offset)
        return [UserResponse.model_validate(user) for user in users]
    
    # def get_user_connections(self, owner_id: int, limit: int = 100, offset: int = 0) -> list[UserResponse]:
    #     """Get all connections/contacts for a specific authenticated user."""
    #     connections = self.user_dao.get_user_connections(owner_id, limit, offset)
    #     return [UserResponse.model_validate(conn) for conn in connections]
    
    def change_user_password(self, user_id: int, new_password: str) -> bool:
        user = self.user_dao.get_user_by_id(user_id)
        if not user:
            return False
        new_password_hash = pwd_context.hash(new_password)
        update_data = {'password': new_password_hash}
        updated_user = self.user_dao.update_user(user_id, update_data)
        return updated_user is not None
    
    def account_user_exist(self) -> bool:
        return self.user_dao.account_user_exist()
    
    def get_companies_sectors(self) -> FilterOptionResponse:
        """Retrieve distinct companies and sectors from users."""
        return self.user_dao.get_companies_sectors()