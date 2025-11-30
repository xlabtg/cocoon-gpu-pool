"""Alert models."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float, JSON, Enum
from sqlalchemy.orm import relationship
import enum
from .base import Base


class AlertSeverity(str, enum.Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertType(str, enum.Enum):
    """Alert type categories."""

    WORKER_DOWN = "worker_down"
    GPU_FAILURE = "gpu_failure"
    HIGH_TEMPERATURE = "high_temperature"
    LOW_PERFORMANCE = "low_performance"
    PAYMENT_RECEIVED = "payment_received"
    PAYMENT_FAILED = "payment_failed"
    REVENUE_THRESHOLD = "revenue_threshold"
    ERROR_RATE_HIGH = "error_rate_high"


class Alert(Base):
    """Alert history model."""

    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_rule_id = Column(Integer, ForeignKey("alert_rules.id"), nullable=True)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=True)
    participant_id = Column(Integer, ForeignKey("participants.id"), nullable=False, index=True)

    alert_type = Column(Enum(AlertType), nullable=False)
    severity = Column(Enum(AlertSeverity), nullable=False)
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)

    triggered_at = Column(DateTime, default=datetime.utcnow, index=True)
    resolved_at = Column(DateTime, nullable=True)
    is_resolved = Column(Boolean, default=False)

    # Notification status
    email_sent = Column(Boolean, default=False)
    telegram_sent = Column(Boolean, default=False)

    # Additional context
    metadata = Column(JSON, nullable=True)


class AlertRule(Base):
    """User-defined alert rules."""

    __tablename__ = "alert_rules"

    id = Column(Integer, primary_key=True, index=True)
    participant_id = Column(Integer, ForeignKey("participants.id"), nullable=False, index=True)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=True)  # Null for all workers

    alert_type = Column(Enum(AlertType), nullable=False)
    is_enabled = Column(Boolean, default=True)

    # Threshold values
    threshold_value = Column(Float, nullable=True)  # Generic threshold
    threshold_duration_seconds = Column(Integer, nullable=True)  # How long before alerting

    # Notification preferences
    notify_email = Column(Boolean, default=True)
    notify_telegram = Column(Boolean, default=True)

    # Cooldown to prevent spam
    cooldown_minutes = Column(Integer, default=30)
    last_triggered = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    participant = relationship("Participant", back_populates="alert_rules")
