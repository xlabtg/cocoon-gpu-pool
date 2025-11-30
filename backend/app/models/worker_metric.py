"""Worker metrics model."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from .base import Base


class WorkerMetric(Base):
    """Time-series metrics for GPU workers."""

    __tablename__ = "worker_metrics"

    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # Performance metrics
    gpu_utilization = Column(Float, nullable=True)  # 0-100%
    gpu_memory_used = Column(Float, nullable=True)  # GB
    gpu_memory_total = Column(Float, nullable=True)  # GB
    gpu_temperature = Column(Float, nullable=True)  # Celsius
    gpu_power_usage = Column(Float, nullable=True)  # Watts

    # Request metrics
    inference_requests_total = Column(Integer, default=0)
    inference_requests_success = Column(Integer, default=0)
    inference_requests_failed = Column(Integer, default=0)
    avg_inference_latency_ms = Column(Float, nullable=True)

    # Revenue metrics
    revenue_ton = Column(Float, default=0.0)  # TON earned
    requests_per_minute = Column(Float, nullable=True)

    # Raw stats from worker
    raw_stats = Column(JSON, nullable=True)  # Full /jsonstats response
    raw_perf = Column(JSON, nullable=True)  # Full /perf response

    # Status
    status = Column(String, default="healthy")  # healthy, degraded, down

    # Relationships
    worker = relationship("Worker", back_populates="metrics")
