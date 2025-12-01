"""Prometheus metrics exporter."""
from prometheus_client import Counter, Gauge, Histogram, Info
from prometheus_client import generate_latest, REGISTRY
from sqlalchemy.orm import Session
from ..models.worker import Worker
from ..models.worker_metric import WorkerMetric
from datetime import datetime, timedelta


# Define Prometheus metrics
worker_status = Gauge(
    'cocoon_worker_status',
    'Worker status (1=healthy, 0.5=degraded, 0=down)',
    ['worker_id', 'worker_name', 'participant_id', 'instance']
)

gpu_utilization = Gauge(
    'cocoon_gpu_utilization',
    'GPU utilization percentage',
    ['worker_id', 'worker_name', 'gpu_id']
)

gpu_memory_used = Gauge(
    'cocoon_gpu_memory_used_gb',
    'GPU memory used in GB',
    ['worker_id', 'worker_name', 'gpu_id']
)

gpu_temperature = Gauge(
    'cocoon_gpu_temperature_celsius',
    'GPU temperature in Celsius',
    ['worker_id', 'worker_name', 'gpu_id']
)

inference_requests_total = Counter(
    'cocoon_inference_requests_total',
    'Total number of inference requests',
    ['worker_id', 'worker_name']
)

inference_requests_failed = Counter(
    'cocoon_inference_requests_failed_total',
    'Total number of failed inference requests',
    ['worker_id', 'worker_name']
)

inference_latency = Histogram(
    'cocoon_inference_latency_seconds',
    'Inference request latency in seconds',
    ['worker_id', 'worker_name'],
    buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0]
)

revenue_ton = Gauge(
    'cocoon_revenue_ton',
    'Revenue in TON cryptocurrency',
    ['worker_id', 'worker_name', 'participant_id']
)

worker_errors = Counter(
    'cocoon_worker_errors_total',
    'Total worker errors',
    ['worker_id', 'worker_name', 'error_type']
)


class PrometheusExporter:
    """Exports Cocoon metrics to Prometheus."""

    def __init__(self, db: Session):
        self.db = db

    def update_metrics(self):
        """Update Prometheus metrics from database."""
        # Get all active workers
        workers = self.db.query(Worker).filter(Worker.is_active == True).all()

        for worker in workers:
            # Get latest metrics
            latest_metric = (
                self.db.query(WorkerMetric)
                .filter(WorkerMetric.worker_id == worker.id)
                .order_by(WorkerMetric.timestamp.desc())
                .first()
            )

            if not latest_metric:
                continue

            labels = {
                'worker_id': str(worker.id),
                'worker_name': worker.worker_name,
                'participant_id': str(worker.participant_id),
                'instance': str(worker.instance_number),
                'gpu_id': '0',  # Assuming single GPU per worker for now
            }

            # Update status
            status_value = {
                'healthy': 1.0,
                'degraded': 0.5,
                'down': 0.0,
                'warning': 0.7,
            }.get(latest_metric.status, 0.0)

            worker_status.labels(
                worker_id=labels['worker_id'],
                worker_name=labels['worker_name'],
                participant_id=labels['participant_id'],
                instance=labels['instance']
            ).set(status_value)

            # Update GPU metrics
            if latest_metric.gpu_utilization is not None:
                gpu_utilization.labels(
                    worker_id=labels['worker_id'],
                    worker_name=labels['worker_name'],
                    gpu_id=labels['gpu_id']
                ).set(latest_metric.gpu_utilization)

            if latest_metric.gpu_memory_used is not None:
                gpu_memory_used.labels(
                    worker_id=labels['worker_id'],
                    worker_name=labels['worker_name'],
                    gpu_id=labels['gpu_id']
                ).set(latest_metric.gpu_memory_used)

            if latest_metric.gpu_temperature is not None:
                gpu_temperature.labels(
                    worker_id=labels['worker_id'],
                    worker_name=labels['worker_name'],
                    gpu_id=labels['gpu_id']
                ).set(latest_metric.gpu_temperature)

            # Update revenue
            if latest_metric.revenue_ton is not None:
                revenue_ton.labels(
                    worker_id=labels['worker_id'],
                    worker_name=labels['worker_name'],
                    participant_id=labels['participant_id']
                ).set(latest_metric.revenue_ton)

            # Update request counters (cumulative)
            # Note: Counter should only increase, so we set to total
            if latest_metric.inference_requests_total is not None:
                # This is a simplification - in production, handle counter resets
                pass  # Counters are updated elsewhere based on deltas

            # Update latency histogram
            if latest_metric.avg_inference_latency_ms is not None:
                latency_seconds = latest_metric.avg_inference_latency_ms / 1000.0
                inference_latency.labels(
                    worker_id=labels['worker_id'],
                    worker_name=labels['worker_name']
                ).observe(latency_seconds)

    def get_metrics(self) -> bytes:
        """Get Prometheus metrics in text format."""
        self.update_metrics()
        return generate_latest(REGISTRY)
