"""Payout model."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from .base import Base


class Payout(Base):
    """Payment transaction history model."""

    __tablename__ = "payouts"

    id = Column(Integer, primary_key=True, index=True)
    participant_id = Column(Integer, ForeignKey("participants.id"), nullable=False, index=True)
    transaction_hash = Column(String, unique=True, index=True, nullable=False)
    amount_ton = Column(Float, nullable=False)  # Amount in TON
    amount_usd = Column(Float, nullable=True)  # USD equivalent at time of payout
    from_address = Column(String, nullable=False)  # Pool's TON address
    to_address = Column(String, nullable=False)  # Participant's TON address
    transaction_time = Column(DateTime, nullable=False)
    confirmed = Column(Integer, default=False)  # Blockchain confirmation status
    confirmations = Column(Integer, default=0)
    block_number = Column(Integer, nullable=True)

    # Period information
    period_start = Column(DateTime, nullable=True)
    period_end = Column(DateTime, nullable=True)

    # Stats for the payout period
    total_requests = Column(Integer, default=0)
    total_compute_time_seconds = Column(Float, default=0.0)

    # Additional metadata
    metadata = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    participant = relationship("Participant", back_populates="payouts")
