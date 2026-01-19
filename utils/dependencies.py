"""
Dependency injection for FastAPI routes.
Provides access to services initialized in the lifespan context.
"""
from typing import TYPE_CHECKING, Dict, Any
from fastapi import HTTPException, Depends
from utils.oath2 import verify_access_token, oauth2_scheme

if TYPE_CHECKING:
    from services.userService import UserService

# This will be set by the lifespan context manager in api.py
_user_service: 'UserService | None' = None



def set_user_service(service: 'UserService') -> None:
    """
    Set the user service instance (called from lifespan in api.py).
    
    Args:
        service: UserService instance to be used across the application
    """
    global _user_service
    _user_service = service



def get_user_service() -> 'UserService':
    """
    Dependency to get user service.
    Use this in route handlers with Depends(get_user_service).
    
    Returns:
        UserService instance
        
    Raises:
        HTTPException: If service is not initialized
    """
    if _user_service is None:
        raise HTTPException(status_code=500, detail="Service not initialized")
    return _user_service


def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    Dependency to get the current user from JWT token.
    Use this in route handlers with current_user: dict = Depends(get_current_user).
    
    Args:
        token: JWT token from Authorization header
        
    Returns:
        dict: User data with 'id', 'email', 'role' keys
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    # Verify token and get user data (returns TokenData or raises HTTPException)
    token_data = verify_access_token(token)
    
    # Convert TokenData to dict
    return {
        "id": token_data.id,
        "email": token_data.email,
        "role": token_data.role
    }


# #TODO: This might need refactoring
# def require_role(required_role: str):
#     """
#     Dependency factory to check if user has a specific role.
    
#     Args:
#         required_role: The role required to access the route
    
#     Returns:
#         A dependency function that checks the user's role
        
#     Example:
#         @router.delete("/users/{id}")
#         async def delete_user(
#             user_id: int,
#             current_user = Depends(require_role("admin"))
#         ):
#             # Only admins can delete users
#             ...
#     """
#     async def role_checker(current_user: Dict[str, Any] = Depends(get_current_user)):
#         if current_user.get("role") != required_role:
#             raise HTTPException(
#                 status_code=403,
#                 detail=f"Insufficient permissions. Required role: {required_role}"
#             )
#         return current_user
    
#     return role_checker
