from typing import Optional
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Date, Text, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base , Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB


Base = declarative_base()

class UserModel(Base):
    __tablename__ = 'users'

    id : Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    first_name: Mapped[str]
    last_name: Mapped[str] 
    company: Mapped[Optional[str]]
    sector: Mapped[Optional[str]]
    is_me : Mapped[int] = mapped_column(default=0)  # 0 for false,
    email: Mapped[Optional[str]]
    phone: Mapped[Optional[str]]
    linkedin_url: Mapped[Optional[str]]
    how_i_know_them : Mapped[Optional[Text]]  # "Met at conference", "College friend", etc.
    when_i_met_them : Mapped[Optional[Date]]
    notes : Mapped[Optional[Text]]
    created_at : Mapped[DateTime] = mapped_column(DateTime(timezone=True), default_factory=func.now , nullable=False)
    updated_at : Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), onupdate=func.now , nullable=True)
    
    # Authentication fields (only populated for is_me=1)
    username: Mapped[Optional[str]]
    password_hash : Mapped[Optional[str]]
    


# class ConnectionModel(Base):
#     __tablename__ = 'connections'

#     id = Column(Integer, primary_key=True, autoincrement=True)
#     person1_id = Column(Integer, ForeignKey('users.id'), nullable=False)
#     person2_id = Column(Integer, ForeignKey('users.id'), nullable=False)
#     relationship: Mapped[str] nullable=True)  # e.g., "colleague", "friend", etc.
#     strength = Column(Numeric, nullable=True)  
#     context = Mapped[Optional[Text]]  # Additional context as JSON
#     last_interaction = Column(DateTime(timezone=True), nullable=True)
#     notes = Mapped[Optional[Text]]
#     created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
#     updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
# class ReferralModel(Base):
#     __tablename__ = 'referrals'

#     id = Column(Integer, primary_key=True, autoincrement=True)
#     referrer_id = Column(Integer, ForeignKey('users.id'), nullable=False)
#     company: Mapped[str] nullable=True)
#     position: Mapped[str] nullable=True)
#     application_date = Column(Date, nullable=True)
#     interview_date = Column(Date, nullable=True)
#     status: Mapped[str] nullable=True)  # e.g., "pending", "accepted", "rejected"
#     notes = Mapped[Optional[Text]]
#     created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
#     updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
# # Additional models can be defined here as needed