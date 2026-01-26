from typing import Any, Dict, Optional
from sqlalchemy import  update , exists
import logging
from sqlalchemy.orm import Session 
from models.database_models import UserModel
from models.response_models import FilterOptionResponse

logger = logging.getLogger(__name__)

class UserDAO:
    def __init__(self, engine):
        self.engine = engine
    
    
    def get_user_by_id(self, user_id) -> Optional[UserModel]:
        try: 
            with Session(self.engine) as session:
                user = session.get(UserModel, user_id)
                #Premature conversion: DAO shouldn't decide what fields to expose—that's service layer's job.
                return user
        except Exception as e:
            logger.error(f"Error retrieving user by id {user_id}: {e}")
            return None
    
    def create_user(self , user_data: Dict[str, Any]) -> Optional[UserModel]:
        try:
            with Session(self.engine) as session:
                new_user = UserModel(**user_data)
                session.add(new_user)
                session.commit()
                session.refresh(new_user)
                return new_user
        except Exception as e:
            logger.error(f"Error creating user with data {user_data}: {e}")
            return None
        
    def delete_user(self, user_id) -> bool  :
        try:
            with Session(self.engine) as session:
                user = session.get(UserModel, user_id)
                if user:
                    session.delete(user)
                    session.commit()
                    return True
                else:
                    logger.warning(f"User with id {user_id} not found for deletion.")
                    return False
        except Exception as e:
            logger.error(f"Error deleting user with id {user_id}: {e}")
            return False
    
    # use **kwargs or a dictionary approach since updates typically modify only a few fields, not all parameters.
    def update_user(self, user_id: int, user_data: Dict[str , Any] ) -> UserModel | None:
        try:
            with Session(self.engine) as session:
                stmt = (
                    update(UserModel).
                    where(UserModel.id == user_id).
                    values(**user_data)
                )
                result = session.execute(stmt)
                session.commit()
                
                if result.rowcount == 0: # type: ignore
                    logger.warning(f"User with id {user_id} not found for update.")
                    return None
                updated_user = session.get(UserModel, user_id)
                return updated_user
        except Exception as e:
            logger.error(f"Error updating user with id {user_id} and data {user_data}: {e}")
            return None
                
                
        
    def get_users(self, limit , offset) -> list[UserModel]:
        try:
            with Session(self.engine) as session:
                users = session.query(UserModel).limit(limit).offset(offset).all()
                return users
        except Exception as e:
            logger.error(f"Error retrieving all users: {e}")
            return []
        
    def get_by_username(self, username: str) -> Optional[UserModel]:
        try:
            with Session(self.engine) as session:
                user = session.query(UserModel).filter(UserModel.username == username).first()
                return user
        except Exception as e:
            logger.error(f"Error retrieving user by username {username}: {e}")
            return None
    
    # def get_user_connections(self, owner_id: int, limit: int, offset: int) -> list[UserModel]:
    #     """Get all connections/contacts owned by a specific user."""
    #     try:
    #         with Session(self.engine) as session:
    #             connections = (
    #                 session.query(UserModel)
    #                 .filter(UserModel.owner_id == owner_id, UserModel.is_me == False)
    #                 .limit(limit)
    #                 .offset(offset)
    #                 .all()
    #             )
    #             return connections
    #     except Exception as e:
    #         logger.error(f"Error retrieving connections for user {owner_id}: {e}")
    #         return []
    
    def account_user_exist(self) -> bool:
        """Check if any user account exists in the database."""
        try:
            with Session(self.engine) as session:
                user_exists = session.query(exists().where(UserModel.username.isnot(None))).scalar()
                return user_exists
        except Exception as e:
            logger.error(f"Error checking if any user account exists: {e}")
            return False
        
    def get_companies_sectors(self) -> FilterOptionResponse:
        """Retrieve distinct companies and sectors from users."""
        try:
            with Session(self.engine) as session:
                companies = session.query(UserModel.company).distinct().all()
                sectors = session.query(UserModel.sector).distinct().all()
                
                companies = [c[0] for c in companies if c[0]]
                sectors = [s[0] for s in sectors if s[0]]
                return FilterOptionResponse(company=companies, sector=sectors)
                
        except Exception as e:
            logger.error(f"Error retrieving distinct companies and sectors: {e}")
            return FilterOptionResponse(company=[], sector=[])