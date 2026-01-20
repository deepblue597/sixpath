"""
Router for user READ operations (GET endpoints).
"""
from fastapi import HTTPException, status, APIRouter, Depends
from typing import List
from models.response_models import UserResponse
from utils.dependencies import get_user_service, get_current_user
from services.userService import UserService
from models.input_models import  UserCreate , UserUpdate , AccountCreate

router = APIRouter(prefix="/users", tags=["users"])

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
    #print(current_user)
    user = user_service.get_user(current_user["id"])
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    user.is_me = True
    return user

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

# @router.get("/by-username/{username}", response_model=UserResponse , status_code=status.HTTP_200_OK)
# async def get_user_by_username(
#     username: str,
#     current_user: dict = Depends(get_current_user),
#     user_service: UserService = Depends(get_user_service)
# ):
#     """
#     Get user by username.
    
#     Args:
#         username: Username of the user to retrieve
#         current_user: Current authenticated user (injected dependency)
#         user_service: User service instance (injected dependency)
        
#     Returns:
#         UserResponse model with user details
        
#     Raises:
#         HTTPException: If user not found
#     """
#     user = user_service.user_dao.get_by_username(username)
#     if not user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
#     user_response = UserResponse.model_validate(user)
#     user_response.is_me = (user_response.id == current_user["id"])
    
#     return user_response

@router.get("/", response_model=List[UserResponse], status_code=status.HTTP_200_OK)
async def get_all_users(
    offset: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """
    Get all connections/contacts of the authenticated user.
    
    Args:
        offset: Pagination offset
        limit: Maximum number of results
        current_user: Current authenticated user (injected dependency)
        user_service: User service instance (injected dependency)
        
    Returns:
        List of UserResponse models with the user's connections
    """
    # Get only connections owned by the current user
    connections = user_service.get_users(limit=limit, offset=offset)
    return connections

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
    current_user: dict = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    """
    Create a new connection/contact in your network.
    
    Args:
        user_create: UserCreate model with new connection data
        current_user: Current authenticated user (injected dependency)
        user_service: User service instance (injected dependency)
        
    Returns:
        Created UserResponse model
        
    Raises:
        HTTPException: If user creation fails
    """
    new_user = user_service.create_user(user_create)
    if not new_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Contact creation failed")
    
    return new_user

@router.post("/register_user", status_code=status.HTTP_200_OK)
async def register_user(
    user_create: AccountCreate,
    user_service: UserService = Depends(get_user_service),
):
    """
    Register a new user account.
    
    Args:
        user_create: UserCreate model with new user data
        user_service: User service instance (injected dependency)
        
    Returns:
        Created UserResponse model
        
    Raises:
        HTTPException: If registration fails
    """
    try:
        new_user = user_service.register_user(user_create)
        if not new_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User registration failed (no user returned)")
        return new_user
    except Exception as e:
        import traceback
        error_detail = f"User registration failed: {str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_detail)

@router.post("/{user_id}/change-password", status_code=status.HTTP_200_OK)
async def change_user_password(
    new_password: str,
    current_user: dict = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    """
    Change user's password.
    
    Args:
        user_id: ID of the user whose password is to be changed
        new_password: New plain text password
        user_service: User service instance (injected dependency)
        
    Returns:
        Success message if password change is successful
        
    Raises:
        HTTPException: If user not found or password change fails
    """
    user_id = current_user["id"]
    success = user_service.change_user_password(user_id, new_password)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found or password change failed")
    
    return {"detail": "Password changed successfully"}
