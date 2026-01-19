# from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, update
# import logging
# from sqlalchemy.orm import Session
# from database_models import ConnectionModel

# logger = logging.getLogger(__name__)

# UPDATABLE_FIELDS = {'person1_id', 'person2_id', 'relationship', 'strength', 
#                     'context', 'last_interaction', 'notes'}

# class Connection: 
    
#     def __init__(self, engine):
#         self.engine = engine
        
#     def get_connection_by_id(self, connection_id):
#         try:
#             with Session(self.engine) as session:
#                 connection = session.get(ConnectionModel, connection_id)
#                 return connection
#         except Exception as e:
#             logger.error(f"Error retrieving connection by id {connection_id}: {e}")
#             return None
        
#     def get_connections_for_user(self, user_id):
#         try:
#             with Session(self.engine) as session:
#                 connections = session.query(ConnectionModel).filter(
#                     (ConnectionModel.person1_id == user_id) | 
#                     (ConnectionModel.person2_id == user_id)
#                 ).all()
#                 return connections
#         except Exception as e:
#             logger.error(f"Error retrieving connections for user id {user_id}: {e}")
#             return []
        
#     def create_connection(self, *, person1_id, person2_id, relationship=None, strength=None, context=None, last_interaction=None, notes=None):
#         try:
#             new_connection = ConnectionModel(
#                 person1_id=person1_id,
#                 person2_id=person2_id,
#                 relationship=relationship,
#                 strength=strength,
#                 context=context,
#                 last_interaction=last_interaction,
#                 notes=notes
#             )
#             with Session(self.engine) as session:
#                 session.add(new_connection)
#                 session.commit()
#                 session.refresh(new_connection)
#                 return new_connection
#         except Exception as e:
#             logger.error(f"Error creating connection between {person1_id} and {person2_id}: {e}")
#             return None
        
#     def delete_connection(self, connection_id):
#         try:
#             with Session(self.engine) as session:
#                 connection = session.get(ConnectionModel, connection_id)
#                 if connection:
#                     session.delete(connection)
#                     session.commit()
#                     return True
#                 else:
#                     logger.warning(f"Connection with id {connection_id} not found for deletion.")
#                     return False
#         except Exception as e:
#             logger.error(f"Error deleting connection with id {connection_id}: {e}")
#             return False
        
#     def delete_connections_for_user(self, user_id):
#         try:
#             with Session(self.engine) as session:
#                 connections = session.query(ConnectionModel).filter(
#                     (ConnectionModel.person1_id == user_id) | 
#                     (ConnectionModel.person2_id == user_id)
#                 ).all()
#                 for connection in connections:
#                     session.delete(connection)
#                 session.commit()
#                 return True
#         except Exception as e:
#             logger.error(f"Error deleting connections for user id {user_id}: {e}")
#             return False
        
#     def update_connection(self, connection_id, **kwargs):
#         try:
#             with Session(self.engine) as session:
#                 connection = session.get(ConnectionModel, connection_id)
#                 if not connection:
#                     logger.warning(f"Connection with id {connection_id} not found for update.")
#                     return None
#                 for key, value in kwargs.items():
#                     if key in UPDATABLE_FIELDS:
#                         setattr(connection, key, value)
#                 session.commit()
#                 session.refresh(connection)
#                 return connection
#         except Exception as e:
#             logger.error(f"Error updating connection with id {connection_id}: {e}")
#             return None