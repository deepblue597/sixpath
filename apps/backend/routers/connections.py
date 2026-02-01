"""
Router for connection operations.
"""
from fastapi import HTTPException, status, APIRouter, Depends
from typing import List
from models.response_models import ConnectionNameResponse, ConnectionResponse
from utils.dependencies import get_connection_service, get_current_user
from services.connectionService import ConnectionService
from models.input_models import  ConnectionCreate , ConnectionUpdate
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/connections", tags=["connections"])



@router.get("/all", response_model=List[ConnectionResponse], status_code=status.HTTP_200_OK)
async def get_all_connections(
    current_user: dict = Depends(get_current_user),
    connection_service: ConnectionService = Depends(get_connection_service)
):
    """
    Get all connections in the system.
    
    Args:
        current_user: Current authenticated user (injected dependency)
        connection_service: Connection service instance (injected dependency)
    
    Returns:
        List of ConnectionResponse models
    """
    connections = connection_service.get_connections()
    return connections

@router.get("/{connection_id}", response_model=ConnectionResponse , status_code=status.HTTP_200_OK)
async def get_connection(
    connection_id: int,
    current_user: dict = Depends(get_current_user),
    connection_service: ConnectionService = Depends(get_connection_service)
):
    """
    Get connection by ID.
    
    Args:
        connection_id: ID of the connection to retrieve
        current_user: Current authenticated user (injected dependency)
        connection_service: Connection service instance (injected dependency)
        
    Returns:
        ConnectionResponse model with connection details
        
    Raises:
        HTTPException: If connection not found
    """
    connection = connection_service.get_connection(connection_id)
    if not connection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Connection not found")
    
    return connection

@router.post("/", response_model=ConnectionResponse, status_code=status.HTTP_201_CREATED)
async def create_connection(
    connection_create: ConnectionCreate,
    current_user: dict = Depends(get_current_user),
    connection_service: ConnectionService = Depends(get_connection_service)
):
    """
    Create a new connection.
    
    Args:
        connection_create: Connection data
        current_user: Current authenticated user (injected dependency)
        connection_service: Connection service instance (injected dependency)
        
    Returns:
        ConnectionResponse model with created connection details
    """
    try:
        new_connection = connection_service.create_connection(connection_create)
        if not new_connection:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create connection")
        return new_connection
    except HTTPException:
        raise  # Re-raise HTTPException as-is without wrapping
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error creating connection: {str(e)}")

@router.delete("/{connection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_connection(
    connection_id: int,
    current_user: dict = Depends(get_current_user),
    connection_service: ConnectionService = Depends(get_connection_service)
):
    """
    Delete a connection by ID.
    
    Args:
        connection_id: ID of the connection to delete
        current_user: Current authenticated user (injected dependency)
        connection_service: Connection service instance (injected dependency)
        
    Raises:
        HTTPException: If deletion fails
    """
    #Route layer: Uses the boolean to either return 204 (success) or raise an HTTPException (failure), but doesn't pass the boolean to the client.
    success = connection_service.delete_connection(connection_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to delete connection")
    

@router.put("/{connection_id}", response_model=ConnectionResponse, status_code=status.HTTP_200_OK)
async def update_connection(
    connection_id: int,
    connection_update: ConnectionUpdate,
    current_user: dict = Depends(get_current_user),
    connection_service: ConnectionService = Depends(get_connection_service)
):
    """
    Update a connection by ID.
    
    Args:
        connection_id: ID of the connection to update
        connection_update: ConnectionUpdate model with updated data
        current_user: Current authenticated user (injected dependency)
        connection_service: Connection service instance (injected dependency)
        
    Returns:
        Updated ConnectionResponse model
        
    Raises:
        HTTPException: If connection not found
    """
    try:
        updated_connection = connection_service.update_connection(connection_id, connection_update)
        if not updated_connection:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Connection not found")
        return updated_connection
    except HTTPException:
        raise
    except IntegrityError as ie:
        # Database constraint violation (e.g., strength check)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid data: {str(ie.orig) if hasattr(ie, 'orig') else str(ie)}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error updating connection: {str(e)}")

@router.get("/user/{user_id}", response_model=List[ConnectionResponse], status_code=status.HTTP_200_OK)
async def get_connections_for_user(
    user_id: int,
    current_user: dict = Depends(get_current_user),
    connection_service: ConnectionService = Depends(get_connection_service)
):
    """
    Get all connections for a specific user.
    
    Args:
        user_id: ID of the user whose connections to retrieve
        current_user: Current authenticated user (injected dependency)
        connection_service: Connection service instance (injected dependency)
    
    Returns:
        List of ConnectionResponse models
    """
    connections = connection_service.get_connections_for_user(user_id)
    return connections


@router.get("/first-last-name/{connection_id}", response_model=ConnectionNameResponse, status_code=status.HTTP_200_OK)
async def get_first_last_name_by_connection_id(
    connection_id: int,
    current_user: dict = Depends(get_current_user),
    connection_service: ConnectionService = Depends(get_connection_service)
):
    """
    Get the first and last name of a connection by ID.
    
    Args:
        connection_id: ID of the connection
        current_user: Current authenticated user (injected dependency)
        connection_service: Connection service instance (injected dependency)
    Returns:
        Full name string (first + last) of the connection
    """
    full_names = connection_service.get_first_last_name_by_connection_id(connection_id)
    if not full_names:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Connection not found")
    return full_names