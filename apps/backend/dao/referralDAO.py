from typing import Any, Dict, Optional
from sqlalchemy import  update
import logging
from sqlalchemy.orm import Session
from models.database_models import ReferralModel

logger = logging.getLogger(__name__)


class ReferralDAO:
    
    def __init__(self, engine):
        self.engine = engine
        
    def get_referral_by_id(self, referral_id) -> Optional[ReferralModel]:
        try: 
            with Session(self.engine) as session:
                referral = session.get(ReferralModel, referral_id)
                return referral
        except Exception as e:
            logger.error(f"Error retrieving referral by id {referral_id}: {e}")
            return None
        
    def create_referral(self , referral_data: Dict[str, Any]) -> Optional[ReferralModel]:
        try:
            with Session(self.engine) as session:
                new_referral = ReferralModel(**referral_data)
                session.add(new_referral)
                session.commit()
                session.refresh(new_referral)
                return new_referral
        except Exception as e:
            logger.error(f"Error creating referral with data {referral_data}: {e}")
            return None
        
    def delete_referral(self, referral_id) -> bool  :
        try:
            with Session(self.engine) as session:
                referral = session.get(ReferralModel, referral_id)
                if referral:
                    session.delete(referral)
                    session.commit()
                    return True
                else:
                    logger.warning(f"Referral with id {referral_id} not found for deletion.")
                    return False
        except Exception as e:
            logger.error(f"Error deleting referral with id {referral_id}: {e}")
            return False
        
    def update_referral(self, referral_id: int, referral_data: Dict[str , Any] ) -> ReferralModel | None:
        try:
            with Session(self.engine) as session:
                stmt = (
                    update(ReferralModel).
                    where(ReferralModel.id == referral_id).
                    values(**referral_data)
                )
                result = session.execute(stmt)
                session.commit()
                
                if result.rowcount == 0: # type: ignore
                    logger.warning(f"Referral with id {referral_id} not found for update.")
                    return None
                
                updated_referral = session.get(ReferralModel, referral_id)
                return updated_referral
        except Exception as e:
            logger.error(f"Error updating referral with id {referral_id}: {e}")
            return None
        
    def get_referrals(self, limit , offset) -> list[ReferralModel]:
        try:
            with Session(self.engine) as session:
                referrals = session.query(ReferralModel).limit(limit).offset(offset).all()
                return referrals
        except Exception as e:
            logger.error(f"Error retrieving referrals with limit {limit} and offset {offset}: {e}")
            return []