from typing import Optional
import logging
from dao.userDAO import UserDAO
from models.response_models import UserResponse
from models.input_models import UserCreate, UserUpdate, AccountCreate
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher


# Initialize password hasher with Argon2 (recommended by OWASP)
pwd_context = PasswordHash((
    Argon2Hasher(),  # Primary hasher
))

logger = logging.getLogger(__name__)

UPDATEBLE_FIELDS = {'first_name', 'last_name', 'email', 'company', 'username',
                    'sector', 'phone', 'linkedin_url', 'how_i_know_them', 
                    'when_i_met_them', 'notes'}

class UserService:
    
    def __init__(self, engine):
        self.user_dao = UserDAO(engine)
        
    def get_user(self, user_id: int) -> Optional[UserResponse]:
        user = self.user_dao.get_user_by_id(user_id)
        if user:
            return UserResponse.model_validate(user)
        return None
    
    def create_user(self, user_create: UserCreate) -> Optional[UserResponse]:
        user_data = user_create.model_dump()
        new_user = self.user_dao.create_user(user_data)
        if new_user:
            return UserResponse.model_validate(new_user)
        return None
    
    
    
    def register_user(self, user_create: AccountCreate) -> Optional[UserResponse]:
        # New user registration with password hashing
        password_hash = pwd_context.hash(user_create.password_hash)
        user_create.password_hash = password_hash
        user_data = user_create.model_dump()
        new_user = self.user_dao.create_user(user_data)
        if new_user:
            return UserResponse.model_validate(new_user)
        return None
    
    def verify_user_password(self, username: str, password: str) -> Optional[UserResponse]:
        user = self.user_dao.get_by_username(username)
        if user and pwd_context.verify(password, user.password):
            return user
        return None
    
    def update_user(self, user_id: int, user_update: UserUpdate) -> Optional[UserResponse]:
        user_data = {k: v for k, v in user_update.model_dump().items() if v is not None and k in UPDATEBLE_FIELDS}
        updated_user = self.user_dao.update_user(user_id, user_data)
        if updated_user:
            return UserResponse.model_validate(updated_user)
        return None
    
    def delete_user(self, user_id: int) -> bool:
        return self.user_dao.delete_user(user_id)
    
    def get_users(self, limit: int = 100, offset: int = 0) -> list[UserResponse]:
        users = self.user_dao.get_users(limit, offset)
        return [UserResponse.model_validate(user) for user in users]