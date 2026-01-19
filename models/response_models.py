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