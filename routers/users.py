"""
Router for user READ operations (GET endpoints).
"""
from fastapi import HTTPException, status, APIRouter, Depends
from typing import List
from models.response_models import UserResponse
from utils.dependencies import get_user_service, get_current_user
from services.userService import UserService
from models.input_models import  UserCreate , UserUpdate

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/{user_id}", response_model=UserResponse , status_code=status.HTTP_200_OK)
async def get_user(
    user_id: int,
    current_user: dict = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """
    Get user by ID.
    
    Args:
        user_id: ID of the user to retrieve
        current_user: Current authenticated user (injected dependency)
        user_service: User service instance (injected dependency)
        
    Returns:
        UserResponse model with user details
        
    Raises:
        HTTPException: If user not found
    """
    user = user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Set is_me flag
    user.is_me = (user.id == current_user["id"])
    
    return user

@router.get("/by-username/{username}", response_model=UserResponse , status_code=status.HTTP_200_OK)
async def get_user_by_username(
    username: str,
    current_user: dict = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """
    Get user by username.
    
    Args:
        username: Username of the user to retrieve
        current_user: Current authenticated user (injected dependency)
        user_service: User service instance (injected dependency)
        
    Returns:
        UserResponse model with user details
        
    Raises:
        HTTPException: If user not found
    """
    user = user_service.user_dao.get_by_username(username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    user_response = UserResponse.model_validate(user)
    user_response.is_me = (user_response.id == current_user["id"])
    
    return user_response

@router.get("/", response_model=List[UserResponse], status_code=status.HTTP_200_OK)
async def get_all_users(
    offset: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """
    Get all users.
    
    Args:
        current_user: Current authenticated user (injected dependency)
        user_service: User service instance (injected dependency)
        
    Returns:
        List of UserResponse models with user details
    """
    users = user_service.user_dao.get_users(offset=offset, limit=limit)
    user_responses = []
    for user in users:
        user_response = UserResponse.model_validate(user)
        user_response.is_me = (user_response.id == current_user["id"])
        user_responses.append(user_response)
    return user_responses

@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """
    Get current authenticated user's information.
    
    Args:
        current_user: Current authenticated user (injected dependency)
        user_service: User service instance (injected dependency)
        
    Returns:
        UserResponse model with current user's details
    """
    user = user_service.get_user(current_user["id"])
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    user.is_me = True
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
):
    """
    Delete user by ID.
    
    Args:
        user_id: ID of the user to delete
        user_service: User service instance (injected dependency)
        
    Raises:
        HTTPException: If user not found
    """
    success = user_service.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    

@router.put("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    user_service: UserService = Depends(get_user_service),
):
    """
    Update user by ID.
    
    Args:
        user_id: ID of the user to update
        user_update: UserResponse model with updated data
        user_service: User service instance (injected dependency)
        
    Returns:
        Updated UserResponse model
        
    Raises:
        HTTPException: If user not found
    """
    updated_user = user_service.update_user(user_id, user_update)
    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return updated_user

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_create: UserCreate,
    user_service: UserService = Depends(get_user_service),
):
    """
    Create a new user.
    
    Args:
        user_create: UserCreate model with new user data
        user_service: User service instance (injected dependency)
        
    Returns:
        Created UserResponse model
        
    Raises:
        HTTPException: If user creation fails
    """
    new_user = user_service.create_user(user_create)
    if not new_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User creation failed")
    
    return new_user