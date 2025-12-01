"""Payout schemas."""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class PayoutBase(BaseModel):
    """Base payout schema."""

    transaction_hash: str
    amount_ton: float
    amount_usd: Optional[float] = None
    from_address: str
    to_address: str
    transaction_time: datetime


class PayoutCreate(PayoutBase):
    """Payout creation schema."""

    participant_id: int
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    total_requests: int = 0
    total_compute_time_seconds: float = 0.0


class Payout(PayoutBase):
    """Payout response schema."""

    id: int
    participant_id: int
    confirmed: bool
    confirmations: int
    block_number: Optional[int]
    period_start: Optional[datetime]
    period_end: Optional[datetime]
    total_requests: int
    total_compute_time_seconds: float
    created_at: datetime

    class Config:
        from_attributes = True
