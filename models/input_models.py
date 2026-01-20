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
    
# Creation of the User of the app (the authenticated owner)
class AccountCreate(UserBase):
    username: str
    password: str  # Plain text password (will be hashed in service layer)
    is_me: bool = True  # Always true for the account owner

# Model for creating a connection/contact (people in your network)
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
