from typing import Optional
import logging
from dao.referralDAO import ReferralDAO
from models.response_models import ReferralResponse
from models.input_models import ReferralCreate, ReferralUpdate


logger = logging.getLogger(__name__)

class ReferralService:
    
    def __init__(self, engine):
        self.referral_dao = ReferralDAO(engine)
        
    def get_referral(self, referral_id: int) -> Optional[ReferralResponse]:
        try:
            referral = self.referral_dao.get_referral_by_id(referral_id)
            if referral:
                return ReferralResponse.model_validate(referral)
            return None
        except Exception as e:
            logger.error(f"Error in get_referral service for id {referral_id}: {e}")
            raise e
    
    def create_referral(self, referral_create: ReferralCreate) -> Optional[ReferralResponse]:
        """Create a new referral.
        
        Args:
            referral_create: Referral data
        """
        try:
            referral_data = referral_create.model_dump()
            new_referral = self.referral_dao.create_referral(referral_data)
            if new_referral:
                return ReferralResponse.model_validate(new_referral)
            return None
        except Exception as e:
            logger.error(f"Error in create_referral service with data {referral_create}: {e}")
            raise  # Re-raise the exception so the route can see the actual error
        
    def delete_referral(self, referral_id: int) -> bool:
        return self.referral_dao.delete_referral(referral_id)
    
    def update_referral(self, referral_id: int, referral_update: ReferralUpdate) -> Optional[ReferralResponse]:
        
        try:
            referral_data = referral_update.model_dump(exclude_unset=True, exclude_none=True) # Only include fields that are set and not None
            updated_referral = self.referral_dao.update_referral(referral_id, referral_data)
            if updated_referral:
                return ReferralResponse.model_validate(updated_referral)
            return None
        except Exception as e:
            logger.error(f"Error in update_referral service for id {referral_id} with data {referral_update}: {e}")
            return None
        
    def get_referrals(self , limit , offset) -> list[ReferralResponse]:
        referrals = self.referral_dao.get_referrals(limit , offset)
        return [ReferralResponse.model_validate(ref) for ref in referrals]
    