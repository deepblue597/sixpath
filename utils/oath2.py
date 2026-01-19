from datetime import datetime, timedelta, timezone
from typing import Annotated
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from models.response_models import TokenData
from config import get_settings

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login") 

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    Create a JWT access token.
    
    Args:
        data: Dictionary containing claims to encode in the token
        expires_delta: Optional custom expiration time
    
    Returns:
        Encoded JWT token as a string
    """
    # Get settings (loads from .env file)
    settings = get_settings()
    
    # Create a copy of the data to encode
    to_encode = data.copy()
    
    # Determine expiration time
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    
    # Add expiration time to the payload
    to_encode.update({"exp": expire})
    
    # Encode the JWT token
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.jwt_secret_key,  # Access from settings
        algorithm=settings.jwt_algorithm  # Access from settings
    )
    return encoded_jwt

def verify_access_token(token: str) -> TokenData:
    """
    Verify and decode a JWT access token.
    
    Args:
        token: JWT token string to verify
    
    Returns:
        Decoded token payload
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    settings = get_settings()
    
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        return TokenData(
            id=int(payload.get("sub")),
            email=payload.get("email"),
            role=payload.get("role")
        )
        #return payload
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    
    return verify_access_token(token)



