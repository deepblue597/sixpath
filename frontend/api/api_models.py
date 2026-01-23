"""
Frontend data models for API responses
These mirror backend response models but are independent

Frontend (Streamlit): Use @dataclass for clean, typed data containers
Backend API models: Keep using Pydantic BaseModel
Backend database models: Keep using SQLAlchemy Base with Mapped

"""
from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional, List

@dataclass
class UserResponse():
    id: int
    is_me: bool
    first_name: str
    last_name: str
    created_at: datetime
    username: Optional[str] = None
    company: Optional[str] = None
    sector: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    how_i_know_them: Optional[str] = None
    when_i_met_them: Optional[date] = None
    notes: Optional[str] = None
    updated_at: Optional[datetime] = None

class ConnectionResponse():
    id: int
    person1_id: int
    person2_id: int
    relationship: Optional[str] = None
    strength: Optional[int] = None
    context: Optional[str] = None
    last_interaction: Optional[datetime | date | str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
class ReferralResponse():
    id: int
    referrer_id: int
    company: Optional[str] = None
    position: Optional[str] = None
    application_date: Optional[date] = None
    interview_date: Optional[date] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
