"""
Router for authentication operations.
"""
from fastapi import HTTPException, status, APIRouter, Depends
from pydantic import BaseModel
from models.response_models import Token
from utils.dependencies import get_user_service
from utils.oath2 import create_access_token, create_password_reset_token, verify_password_reset_token
from services.userService import UserService
from fastapi.security.oauth2 import OAuth2PasswordRequestForm


class ForgotPasswordRequest(BaseModel):
    username: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=Token , status_code=status.HTTP_200_OK)
async def login(
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(get_user_service)
):
    """
    Authenticate user with email and password.
    
    Args:
        email: User's email
        password: User's plain text password
    
    Returns:
        User data (without password) if authentication successful
    
    Raises:
        HTTPException: 401 if credentials are invalid
    """
    try:
        # Verify user credentials
        # user_credentials.username contains the email
        # user_credentials.password contains the password
        user_data = user_service.verify_user_password(user_credentials.username, user_credentials.password)
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Return user data without password
        # Create JWT token with user info
        access_token = create_access_token(data={
            "sub": str(user_data.id),  # "sub" is standard JWT claim for subject/user ID
            "email": user_data.email,
            
            })
        
        return Token(access_token=access_token, token_type="bearer")
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Login error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Service error: {str(e)}")

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout():
    """
    Logout endpoint (placeholder).
    
    Since JWTs are stateless, logout is handled on the client side by deleting the token.
    
    Returns:
        Success message
    """
    return {"message": "Logout successful. Please delete the token on client side."}

@router.post("/service-token", response_model=Token, status_code=status.HTTP_200_OK)
async def generate_service_token(
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(get_user_service),
    expiration_days: int = 365
):
    """
    Generate a long-lived JWT token for service-to-service communication.
    
    This endpoint is designed for creating tokens with extended expiration times
    for automated services (e.g., ML models, batch processors).
    
    Args:
        user_credentials: Service account credentials (email/password)
        expiration_days: Token expiration in days (default: 365)
    
    Returns:
        Long-lived JWT token
    
    Raises:
        HTTPException: 401 if credentials are invalid
    
    Example:
        curl -X POST "http://localhost:8000/auth/service-token?expiration_days=180" \\
             -F "username=model-service@internal.com" \\
             -F "password=123123"
    """
    try:
        # Verify service account credentials
        user_data = user_service.verify_user_password(
            user_credentials.username, 
            user_credentials.password
        )
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid service account credentials"
            )
        
        # Create long-lived token (override default expiration)
        from datetime import timedelta
        expires_delta = timedelta(days=expiration_days)
        
        access_token = create_access_token(
            data={
                "sub": str(user_data.id),
                "email": user_data.email,
                "type": "service_token"  # Mark as service token
            },
            expires_delta=expires_delta
        )
        
        return Token(access_token=access_token, token_type="bearer")
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Service token generation error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Service error: {str(e)}")
    
@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(
    body: ForgotPasswordRequest,
    user_service: UserService = Depends(get_user_service),
):
    """
    Request a password reset token.

    Looks up the user by username. Always returns 200 to prevent username
    enumeration. If the username exists, a short-lived reset token (15 min)
    is returned for the self-hosted flow (no email required).
    """
    user = user_service.get_user_by_username(body.username)
    if not user:
        # Return a generic message — don't reveal whether the username exists
        return {"message": "If the username exists, a reset token has been generated."}
    reset_token = create_password_reset_token(user.id)
    return {"message": "Reset token generated.", "reset_token": reset_token}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    body: ResetPasswordRequest,
    user_service: UserService = Depends(get_user_service),
):
    """
    Reset the user's password using a valid reset token.

    The token must be a password_reset JWT (issued by /auth/forgot-password)
    and must not be expired. No authentication required.
    """
    user_id = verify_password_reset_token(body.token)
    success = user_service.change_user_password(user_id, body.new_password)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"message": "Password reset successfully."}


@router.get("/account-exists", status_code=status.HTTP_200_OK)
async def account_user_exist(
    user_service: UserService = Depends(get_user_service),
):
    """
    Check if any user account exists in the database.
    
    Args:
        user_service: User service instance (injected dependency)
    Returns:
        Boolean indicating if any user account exists
    """
    exists = user_service.account_user_exist()
    return {"account_exists": exists}