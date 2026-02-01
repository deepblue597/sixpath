from fastapi import HTTPException, status, APIRouter, Depends
from typing import List
from models.response_models import ReferralResponse
from utils.dependencies import get_referral_service, get_current_user
from services.referralService import ReferralService
from models.input_models import  ReferralCreate , ReferralUpdate , AccountCreate  

router = APIRouter(prefix="/referrals", tags=["referrals"])

@router.get("/me", response_model=List[ReferralResponse], status_code=status.HTTP_200_OK)
async def get_current_user_referrals(
    offset: int = 0,
    limit: int = 10,
    current_user: dict = Depends(get_current_user),
    referral_service: ReferralService = Depends(get_referral_service)
):
    """
    Get current authenticated user's referrals.
    
    Args:
        current_user: Current authenticated user (injected dependency)
        referral_service: Referral service instance (injected dependency)
        
    Returns:
        List of ReferralResponse models with current user's referrals
    """
    #user_id = current_user["id"]
    referrals = referral_service.get_referrals(limit=limit, offset=offset)
    return referrals

@router.get("/{referral_id}", response_model=ReferralResponse , status_code=status.HTTP_200_OK)
async def get_referral(
    referral_id: int,
    current_user: dict = Depends(get_current_user),
    referral_service: ReferralService = Depends(get_referral_service)
):
    """
    Get referral by ID.
    
    Args:
        referral_id: ID of the referral to retrieve
        current_user: Current authenticated user (injected dependency)
        referral_service: Referral service instance (injected dependency)
        
    Returns:
        ReferralResponse model with referral details
        
    Raises:
        HTTPException: If referral not found
    """
    
    referral = referral_service.get_referral(referral_id)
    if not referral:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Referral not found")
    
    return referral

@router.post("/", response_model=ReferralResponse, status_code=status.HTTP_201_CREATED)
async def create_referral(
    referral_create: ReferralCreate,
    current_user: dict = Depends(get_current_user),
    referral_service: ReferralService = Depends(get_referral_service)
):
    """
    Create a new referral.
    
    Args:
        referral_create: Referral data
        current_user: Current authenticated user (injected dependency)
        referral_service: Referral service instance (injected dependency)
        
    Returns:
        ReferralResponse model with created referral details
    """
    # FastAPI automatically catches unhandled exceptions and returns 500. Your service layer should only handle expected cases (404).
    new_referral = referral_service.create_referral(referral_create)
    if not new_referral:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create referral")
    return new_referral


@router.delete("/{referral_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_referral(
    referral_id: int,
    current_user: dict = Depends(get_current_user),
    referral_service: ReferralService = Depends(get_referral_service)
):
    """
    Delete referral by ID.
    
    Args:
        referral_id: ID of the referral to delete
        current_user: Current authenticated user (injected dependency)
        referral_service: Referral service instance (injected dependency)
        
    Raises:
        HTTPException: If referral not found
    """
    success = referral_service.delete_referral(referral_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Referral not found")
    
@router.put("/{referral_id}", response_model=ReferralResponse, status_code=status.HTTP_200_OK)
async def update_referral(
    referral_id: int,
    referral_update: ReferralUpdate,
    current_user: dict = Depends(get_current_user),
    referral_service: ReferralService = Depends(get_referral_service)
):
    """
    Update referral by ID.
    
    Args:
        referral_id: ID of the referral to update
        referral_update: ReferralUpdate model with updated data
        current_user: Current authenticated user (injected dependency)
        referral_service: Referral service instance (injected dependency)
        
    Returns:
        Updated ReferralResponse model
        
    Raises:
        HTTPException: If referral not found
    """
    updated_referral = referral_service.update_referral(referral_id, referral_update)
    if not updated_referral:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Referral not found")
    
    return updated_referral

