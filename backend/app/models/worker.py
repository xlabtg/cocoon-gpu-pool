"""Worker model."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship
from .base import Base


class Worker(Base):
    """GPU worker instance model."""

    __tablename__ = "workers"

    id = Column(Integer, primary_key=True, index=True)
    participant_id = Column(Integer, ForeignKey("participants.id"), nullable=False)
    worker_name = Column(String, nullable=False)
    instance_number = Column(Integer, nullable=False)  # 0, 1, 2, etc.
    host = Column(String, nullable=False, default="localhost")
    stats_port = Column(Integer, nullable=False)  # 12000, 12010, etc.
    cid = Column(String, nullable=True)  # TDX guest CID
    price_coefficient = Column(Float, default=1.0)  # Pricing multiplier
    is_active = Column(Boolean, default=True)
    last_seen = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    participant = relationship("Participant", back_populates="workers")
    metrics = relationship("WorkerMetric", back_populates="worker")
