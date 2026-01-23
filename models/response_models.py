from pydantic import ConfigDict
from models.input_models import UserBase
from pydantic import BaseModel
from datetime import datetime, date

class UserResponse(UserBase):
    id: int
    is_me: bool
    username: str | None = None
    created_at: datetime
    updated_at: datetime | None = None

    # Pydantic v2 syntax
    model_config = ConfigDict(from_attributes=True)
    
    
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: int | None = None
    email: str | None = None
    role: str | None = None
    
class ConnectionResponse(BaseModel):
    id: int
    person1_id: int
    person2_id: int
    relationship: str | None = None
    strength: int | None = None
    context: str | None = None
    last_interaction: datetime | date | str | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime | None = None
    
    model_config = ConfigDict(from_attributes=True)
    
class ReferralResponse(BaseModel):
    id: int
    referrer_id: int
    company: str | None = None
    position: str | None = None
    application_date: date | None = None
    interview_date: date | None = None
    status: str | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)