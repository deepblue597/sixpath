from pydantic import BaseModel

# Base model with common user fields
class UserBase(BaseModel):
    first_name: str
    last_name: str
    company: str | None = None
    sector: str | None = None
    email: str | None = None
    phone: str | None = None
    linkedin_url: str | None = None
    how_i_know_them: str | None = None
    when_i_met_them: str | None = None
    notes: str | None = None
    
# Creation of the User of the app
class AccountCreate(UserBase):
    username: str
    password_hash: str
    is_me: bool = False

# Model for creating a new user
class UserCreate(UserBase):
    pass
    
# Model for updating an existing user
class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    company: str | None = None
    sector: str | None = None
    username: str | None = None
    email: str | None = None
    phone: str | None = None
    linkedin_url: str | None = None
    how_i_know_them: str | None = None
    when_i_met_them: str | None = None
    notes: str | None = None
