from pydantic import ConfigDict
from models.input_models import UserBase
from pydantic import BaseModel

class UserResponse(UserBase):
    id: int
    is_me: bool
    username: str | None = None

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
    strength: float | None = None
    context: str | None = None
    last_interaction: str | None = None
    notes: str | None = None

    model_config = ConfigDict(from_attributes=True)