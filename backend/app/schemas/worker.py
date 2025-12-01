"""Worker schemas."""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class WorkerBase(BaseModel):
    """Base worker schema."""

    worker_name: str
    instance_number: int
    host: str = "localhost"
    stats_port: int
    cid: Optional[str] = None
    price_coefficient: float = 1.0


class WorkerCreate(WorkerBase):
    """Worker creation schema."""

    participant_id: int


class WorkerUpdate(BaseModel):
    """Worker update schema."""

    worker_name: Optional[str] = None
    is_active: Optional[bool] = None
    price_coefficient: Optional[float] = None


class Worker(WorkerBase):
    """Worker response schema."""

    id: int
    participant_id: int
    is_active: bool
    last_seen: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WorkerWithMetrics(Worker):
    """Worker with latest metrics."""

    latest_status: Optional[str] = None
    latest_gpu_utilization: Optional[float] = None
    latest_revenue_ton: Optional[float] = None
    last_metric_time: Optional[datetime] = None
