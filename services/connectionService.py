from typing import Optional
import logging
from dao.connectionDAO import ConnectionDAO 
from dao.userDAO import UserDAO
from models.response_models import ConnectionResponse
from models.input_models import ConnectionCreate, ConnectionUpdate


logger = logging.getLogger(__name__)

class ConnectionService:
    
    def __init__(self, engine):
        self.connection_dao = ConnectionDAO(engine)
        self.user_dao = UserDAO(engine)
        
    def get_connection(self, connection_id: int) -> Optional[ConnectionResponse]:
        try:
            connection = self.connection_dao.get_connection_by_id(connection_id)
            if connection:
                return ConnectionResponse.model_validate(connection)
            return None
        except Exception as e:
            logger.error(f"Error in get_connection service for id {connection_id}: {e}")
            return None
    
    def create_connection(self, connection_create: ConnectionCreate) -> Optional[ConnectionResponse]:
        """Create a new contact/connection in the network.
        
        Args:
            connection_create: Connection data
        """
        try:
            connection_data = connection_create.model_dump()
            new_connection = self.connection_dao.create_connection(connection_data)
            if new_connection:
                return ConnectionResponse.model_validate(new_connection)
            return None
        except Exception as e:
            logger.error(f"Error in create_connection service with data {connection_create}: {e}")
            raise  # Re-raise the exception so the route can see the actual error
        
    def delete_connection(self, connection_id: int) -> bool:
        return self.connection_dao.delete_connection(connection_id)
    
    def update_connection(self, connection_id: int, connection_update: ConnectionUpdate) -> Optional[ConnectionResponse]:
        
        try:
            connection_data = connection_update.model_dump(exclude_unset=True, exclude_none=True) # Only include fields that are set and not None
            updated_connection = self.connection_dao.update_connection(connection_id, connection_data)
            if updated_connection:
                return ConnectionResponse.model_validate(updated_connection)
            return None
        except Exception as e:
            logger.error(f"Error in update_connection service for id {connection_id} with data {connection_update}: {e}")
            return None
        
        
    def get_connections_for_user(self, user_id: int) -> list[ConnectionResponse]:
        connections = self.connection_dao.get_connections_for_user(user_id)
        return [ConnectionResponse.model_validate(conn) for conn in connections]
    
    
    def delete_connections_for_user(self, user_id: int) -> bool:
        return self.connection_dao.delete_connections_for_user(user_id)
    
    def get_connections(self) -> list[ConnectionResponse]:
        connections = self.connection_dao.get_connections()
        return [ConnectionResponse.model_validate(conn) for conn in connections]
    
    def get_first_last_name_by_connection_id(self, connection_id: int) -> Optional[str]:
        try: 
            connection = self.get_connection(connection_id)
            if connection:
                user_id = connection.person2_id  # Assuming we want the username of person2
                # Here you would typically call UserService or UserDAO to get the username
                user = self.user_dao.get_user_by_id(user_id)
                if user:
                    return user.first_name + ' ' + user.last_name
            return None
        except Exception as e:
            logger.error(f"Error in get_username_by_connection_id service for id {connection_id}: {e}")
            return None
        
    # get all_user