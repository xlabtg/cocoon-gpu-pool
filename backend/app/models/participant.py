"""Participant model."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from .base import Base


class Participant(Base):
    """Participant model for GPU pool users."""

    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, index=True)
    ton_wallet_address = Column(String, unique=True, index=True, nullable=False)
    telegram_user_id = Column(Integer, unique=True, index=True, nullable=True)
    username = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=True)
    is_active = Column(Boolean, default=True)
    is_operator = Column(Boolean, default=False)  # Pool operator role
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    workers = relationship("Worker", back_populates="participant")
    payouts = relationship("Payout", back_populates="participant")
    alert_rules = relationship("AlertRule", back_populates="participant")
