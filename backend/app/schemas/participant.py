"""Participant schemas."""
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class ParticipantBase(BaseModel):
    """Base participant schema."""

    ton_wallet_address: str
    telegram_user_id: Optional[int] = None
    username: Optional[str] = None
    email: Optional[EmailStr] = None


class ParticipantCreate(ParticipantBase):
    """Participant creation schema."""

    pass


class ParticipantUpdate(BaseModel):
    """Participant update schema."""

    telegram_user_id: Optional[int] = None
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


class Participant(ParticipantBase):
    """Participant response schema."""

    id: int
    is_active: bool
    is_operator: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ParticipantStats(Participant):
    """Participant with statistics."""

    total_workers: int = 0
    active_workers: int = 0
    total_revenue_ton: float = 0.0
    total_payouts: int = 0
    last_payout_date: Optional[datetime] = None
