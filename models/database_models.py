from datetime import date
from typing import Optional
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Date, Text, Numeric
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
    is_me: Mapped[bool] = mapped_column(Boolean, default=False)  # True = authenticated app owner, False = connection/contact
    email: Mapped[Optional[str]]
    phone: Mapped[Optional[str]]
    linkedin_url: Mapped[Optional[str]]
    how_i_know_them: Mapped[Optional[str]]  # Use Python type str
    when_i_met_them: Mapped[Optional[date]] = mapped_column(Date, nullable=True)  # Use Python date type
    notes: Mapped[Optional[str]]  # Use Python type str
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at: Mapped[Optional[str]] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    # Authentication fields (only populated for is_me=1)
    username: Mapped[Optional[str]]
    password: Mapped[Optional[str]]
    


class ConnectionModel(Base):
    __tablename__ = 'connections'

    id : Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    person1_id : Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)    #= Column(Integer, ForeignKey('users.id'), nullable=False)
    person2_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)  #= Column(Integer, ForeignKey('users.id'), nullable=False)
    relationship: Mapped[Optional[str]]  # e.g., "colleague", "friend", etc.
    strength: Mapped[Optional[int]]  #= Column(Numeric, nullable=True)  
    context: Mapped[Optional[str]]  # Additional context as JSON
    last_interaction: Mapped[Optional[str]] = mapped_column(DateTime(timezone=True), nullable=True) #Column(DateTime(timezone=True), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), default=func.now(), nullable=False) #= Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[str]] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)#= Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    

class ReferralModel(Base):
    __tablename__ = 'referrals'

    id : Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    referrer_id : Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    company: Mapped[Optional[str]]  # nullable=True)
    position: Mapped[Optional[str]]  # nullable=True)
    application_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)  # Use Python date type
    interview_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)  # Use Python date type
    status: Mapped[Optional[str]]  # e.g., "pending", "accepted", "rejected"
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at: Mapped[Optional[str]] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)