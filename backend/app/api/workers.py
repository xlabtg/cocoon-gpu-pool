"""Worker API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from datetime import datetime, timedelta
from ..core.database import get_db
from ..models.worker import Worker
from ..models.worker_metric import WorkerMetric
from ..schemas.worker import Worker as WorkerSchema, WorkerCreate, WorkerUpdate, WorkerWithMetrics

router = APIRouter(prefix="/workers", tags=["workers"])


@router.get("", response_model=List[WorkerWithMetrics])
def list_workers(
    participant_id: int = None,
    is_active: bool = None,
    db: Session = Depends(get_db)
):
    """List all workers with optional filtering."""
    query = db.query(Worker)

    if participant_id is not None:
        query = query.filter(Worker.participant_id == participant_id)
    if is_active is not None:
        query = query.filter(Worker.is_active == is_active)

    workers = query.all()

    # Enrich with latest metrics
    result = []
    for worker in workers:
        latest_metric = (
            db.query(WorkerMetric)
            .filter(WorkerMetric.worker_id == worker.id)
            .order_by(desc(WorkerMetric.timestamp))
            .first()
        )

        worker_dict = {
            **WorkerSchema.from_orm(worker).dict(),
            "latest_status": latest_metric.status if latest_metric else None,
            "latest_gpu_utilization": latest_metric.gpu_utilization if latest_metric else None,
            "latest_revenue_ton": latest_metric.revenue_ton if latest_metric else None,
            "last_metric_time": latest_metric.timestamp if latest_metric else None,
        }
        result.append(WorkerWithMetrics(**worker_dict))

    return result


@router.get("/{worker_id}", response_model=WorkerWithMetrics)
def get_worker(worker_id: int, db: Session = Depends(get_db)):
    """Get a specific worker by ID."""
    worker = db.query(Worker).filter(Worker.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")

    # Get latest metric
    latest_metric = (
        db.query(WorkerMetric)
        .filter(WorkerMetric.worker_id == worker.id)
        .order_by(desc(WorkerMetric.timestamp))
        .first()
    )

    worker_dict = {
        **WorkerSchema.from_orm(worker).dict(),
        "latest_status": latest_metric.status if latest_metric else None,
        "latest_gpu_utilization": latest_metric.gpu_utilization if latest_metric else None,
        "latest_revenue_ton": latest_metric.revenue_ton if latest_metric else None,
        "last_metric_time": latest_metric.timestamp if latest_metric else None,
    }

    return WorkerWithMetrics(**worker_dict)


@router.post("", response_model=WorkerSchema)
def create_worker(worker: WorkerCreate, db: Session = Depends(get_db)):
    """Create a new worker."""
    db_worker = Worker(**worker.dict())
    db.add(db_worker)
    db.commit()
    db.refresh(db_worker)
    return db_worker


@router.patch("/{worker_id}", response_model=WorkerSchema)
def update_worker(
    worker_id: int,
    worker_update: WorkerUpdate,
    db: Session = Depends(get_db)
):
    """Update a worker."""
    worker = db.query(Worker).filter(Worker.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")

    update_data = worker_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(worker, field, value)

    worker.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(worker)
    return worker


@router.get("/{worker_id}/metrics")
def get_worker_metrics(
    worker_id: int,
    hours: int = Query(24, description="Number of hours of metrics to retrieve"),
    db: Session = Depends(get_db)
):
    """Get historical metrics for a worker."""
    worker = db.query(Worker).filter(Worker.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")

    since = datetime.utcnow() - timedelta(hours=hours)
    metrics = (
        db.query(WorkerMetric)
        .filter(
            WorkerMetric.worker_id == worker_id,
            WorkerMetric.timestamp >= since
        )
        .order_by(WorkerMetric.timestamp)
        .all()
    )

    return {
        "worker_id": worker_id,
        "worker_name": worker.worker_name,
        "period_hours": hours,
        "metrics_count": len(metrics),
        "metrics": [
            {
                "timestamp": m.timestamp.isoformat(),
                "status": m.status,
                "gpu_utilization": m.gpu_utilization,
                "gpu_temperature": m.gpu_temperature,
                "inference_requests_total": m.inference_requests_total,
                "avg_inference_latency_ms": m.avg_inference_latency_ms,
                "revenue_ton": m.revenue_ton,
            }
            for m in metrics
        ]
    }


@router.get("/{worker_id}/stats")
def get_worker_stats(worker_id: int, db: Session = Depends(get_db)):
    """Get aggregated statistics for a worker."""
    worker = db.query(Worker).filter(Worker.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")

    # Get metrics from last 24 hours
    since = datetime.utcnow() - timedelta(hours=24)
    metrics = (
        db.query(WorkerMetric)
        .filter(
            WorkerMetric.worker_id == worker_id,
            WorkerMetric.timestamp >= since
        )
        .all()
    )

    if not metrics:
        return {
            "worker_id": worker_id,
            "message": "No metrics available",
        }

    # Calculate statistics
    total_revenue = sum(m.revenue_ton or 0 for m in metrics)
    avg_utilization = sum(m.gpu_utilization or 0 for m in metrics) / len(metrics)
    total_requests = metrics[-1].inference_requests_total if metrics else 0

    return {
        "worker_id": worker_id,
        "worker_name": worker.worker_name,
        "period_hours": 24,
        "total_revenue_ton": round(total_revenue, 4),
        "avg_gpu_utilization": round(avg_utilization, 2),
        "total_inference_requests": total_requests,
        "uptime_percentage": round(
            len([m for m in metrics if m.status == "healthy"]) / len(metrics) * 100, 2
        ) if metrics else 0,
    }
