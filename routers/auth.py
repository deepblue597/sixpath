"""
Router for authentication operations.
"""
from fastapi import HTTPException, status, APIRouter, Depends
from models.response_models import Token
from utils.dependencies import get_user_service
from utils.oath2 import create_access_token
from services.userService import UserService
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

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