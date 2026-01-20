from typing import Any, Dict, Optional
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, update
import logging
from sqlalchemy.orm import Session
from models.database_models import ConnectionModel
logger = logging.getLogger(__name__)


class ConnectionDAO: 
    
    def __init__(self, engine):
        self.engine = engine
        
    def get_connection_by_id(self, connection_id):
        try:
            with Session(self.engine) as session:
                connection = session.get(ConnectionModel, connection_id)
                return connection
        except Exception as e:
            logger.error(f"Error retrieving connection by id {connection_id}: {e}")
            raise
        
    def get_connections_for_user(self, user_id):
        try:
            with Session(self.engine) as session:
                connections = session.query(ConnectionModel).filter(
                    (ConnectionModel.person1_id == user_id) | 
                    (ConnectionModel.person2_id == user_id)
                ).all()
                return connections
        except Exception as e:
            logger.error(f"Error retrieving connections for user id {user_id}: {e}")
            raise
        
    def create_connection(self, connetion_data: Dict[str, Any]) -> Optional[ConnectionModel]:
        try:
            with Session(self.engine) as session:
                new_connection = ConnectionModel(**connetion_data)
                session.add(new_connection)
                session.commit()
                session.refresh(new_connection)
                return new_connection
        except Exception as e:
            logger.error(f"Error creating connection with data {connetion_data}: {e}")
            raise  # Re-raise the exception to be handled by the service layer
        
    def delete_connection(self, connection_id):
        try:
            with Session(self.engine) as session:
                connection = session.get(ConnectionModel, connection_id)
                if connection:
                    session.delete(connection)
                    session.commit()
                    return True
                else:
                    logger.warning(f"Connection with id {connection_id} not found for deletion.")
                    return False
        except Exception as e:
            logger.error(f"Error deleting connection with id {connection_id}: {e}")
            raise
        
    def delete_connections_for_user(self, user_id):
        try:
            with Session(self.engine) as session:
                connections = session.query(ConnectionModel).filter(
                    (ConnectionModel.person1_id == user_id) | 
                    (ConnectionModel.person2_id == user_id)
                ).all()
                for connection in connections:
                    session.delete(connection)
                session.commit()
                return True
        except Exception as e:
            logger.error(f"Error deleting connections for user id {user_id}: {e}")
            raise
        
    def update_connection(self, connection_id, connetion_data: Dict[str, Any]) -> Optional[ConnectionModel]:
        try:
            with Session(self.engine) as session:
                stmt = (
                    update(ConnectionModel).
                    where(ConnectionModel.id == connection_id).
                    values(**connetion_data)
                )
                result = session.execute(stmt)
                session.commit()
                
                if result.rowcount == 0: # type: ignore
                    logger.warning(f"Connection with id {connection_id} not found for update.")
                    return None
                updated_connection = session.get(ConnectionModel, connection_id)
                return updated_connection
        except Exception as e:
            logger.error(f"Error updating connection with id {connection_id}: {e}")
            raise
        
    