"""Alert management service."""
import logging
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from ..models.alert import Alert, AlertRule, AlertType, AlertSeverity
from ..models.worker import Worker
from ..models.worker_metric import WorkerMetric
from ..models.participant import Participant

logger = logging.getLogger(__name__)


class AlertManager:
    """Manages alert rules and triggers notifications."""

    def __init__(self, db: Session):
        self.db = db

    def check_worker_down(self, worker: Worker) -> Optional[Alert]:
        """Check if a worker is down."""
        if not worker.last_seen:
            return None

        time_since_seen = datetime.utcnow() - worker.last_seen
        if time_since_seen.total_seconds() > 300:  # 5 minutes
            return self.create_alert(
                participant_id=worker.participant_id,
                worker_id=worker.id,
                alert_type=AlertType.WORKER_DOWN,
                severity=AlertSeverity.CRITICAL,
                title=f"Worker {worker.worker_name} is down",
                message=f"Worker {worker.worker_name} has not been seen for {int(time_since_seen.total_seconds())} seconds",
            )
        return None

    def check_high_temperature(self, worker: Worker, latest_metric: WorkerMetric) -> Optional[Alert]:
        """Check if GPU temperature is too high."""
        if not latest_metric or not latest_metric.gpu_temperature:
            return None

        threshold = 85.0  # Celsius
        if latest_metric.gpu_temperature > threshold:
            return self.create_alert(
                participant_id=worker.participant_id,
                worker_id=worker.id,
                alert_type=AlertType.HIGH_TEMPERATURE,
                severity=AlertSeverity.WARNING,
                title=f"High GPU temperature on {worker.worker_name}",
                message=f"GPU temperature is {latest_metric.gpu_temperature}°C (threshold: {threshold}°C)",
                metadata={"temperature": latest_metric.gpu_temperature, "threshold": threshold}
            )
        return None

    def check_low_performance(self, worker: Worker, latest_metric: WorkerMetric) -> Optional[Alert]:
        """Check if worker performance is low."""
        if not latest_metric or not latest_metric.gpu_utilization:
            return None

        # Check if GPU utilization is consistently low
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        recent_metrics = self.db.query(WorkerMetric).filter(
            and_(
                WorkerMetric.worker_id == worker.id,
                WorkerMetric.timestamp >= one_hour_ago
            )
        ).all()

        if len(recent_metrics) < 4:  # Not enough data
            return None

        avg_utilization = sum(m.gpu_utilization or 0 for m in recent_metrics) / len(recent_metrics)
        threshold = 20.0  # 20% utilization

        if avg_utilization < threshold and worker.is_active:
            return self.create_alert(
                participant_id=worker.participant_id,
                worker_id=worker.id,
                alert_type=AlertType.LOW_PERFORMANCE,
                severity=AlertSeverity.INFO,
                title=f"Low GPU utilization on {worker.worker_name}",
                message=f"Average GPU utilization over last hour: {avg_utilization:.1f}% (threshold: {threshold}%)",
                metadata={"avg_utilization": avg_utilization, "threshold": threshold}
            )
        return None

    def check_error_rate(self, worker: Worker, latest_metric: WorkerMetric) -> Optional[Alert]:
        """Check if error rate is too high."""
        if not latest_metric:
            return None

        total = latest_metric.inference_requests_total or 0
        failed = latest_metric.inference_requests_failed or 0

        if total == 0:
            return None

        error_rate = (failed / total) * 100
        threshold = 10.0  # 10% error rate

        if error_rate > threshold:
            return self.create_alert(
                participant_id=worker.participant_id,
                worker_id=worker.id,
                alert_type=AlertType.ERROR_RATE_HIGH,
                severity=AlertSeverity.ERROR,
                title=f"High error rate on {worker.worker_name}",
                message=f"Error rate: {error_rate:.1f}% ({failed}/{total} requests failed)",
                metadata={"error_rate": error_rate, "failed": failed, "total": total}
            )
        return None

    def create_alert(
        self,
        participant_id: int,
        alert_type: AlertType,
        severity: AlertSeverity,
        title: str,
        message: str,
        worker_id: Optional[int] = None,
        alert_rule_id: Optional[int] = None,
        metadata: Optional[dict] = None,
    ) -> Alert:
        """Create a new alert."""
        # Check if there's a recent unresolved alert of the same type
        recent_cutoff = datetime.utcnow() - timedelta(minutes=30)
        existing = self.db.query(Alert).filter(
            and_(
                Alert.participant_id == participant_id,
                Alert.worker_id == worker_id,
                Alert.alert_type == alert_type,
                Alert.is_resolved == False,
                Alert.triggered_at >= recent_cutoff
            )
        ).first()

        if existing:
            logger.info(f"Skipping duplicate alert: {alert_type} for worker {worker_id}")
            return existing

        alert = Alert(
            participant_id=participant_id,
            worker_id=worker_id,
            alert_rule_id=alert_rule_id,
            alert_type=alert_type,
            severity=severity,
            title=title,
            message=message,
            metadata=metadata,
        )

        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)

        logger.info(f"Created alert {alert.id}: {title}")
        return alert

    def check_all_workers(self):
        """Check all active workers for alert conditions."""
        workers = self.db.query(Worker).filter(Worker.is_active == True).all()

        alerts_created = 0
        for worker in workers:
            # Get latest metric
            latest_metric = self.db.query(WorkerMetric).filter(
                WorkerMetric.worker_id == worker.id
            ).order_by(WorkerMetric.timestamp.desc()).first()

            # Run all checks
            checks = [
                self.check_worker_down(worker),
                self.check_high_temperature(worker, latest_metric) if latest_metric else None,
                self.check_low_performance(worker, latest_metric) if latest_metric else None,
                self.check_error_rate(worker, latest_metric) if latest_metric else None,
            ]

            for alert in checks:
                if alert:
                    alerts_created += 1

        logger.info(f"Alert check complete. Created {alerts_created} new alerts.")
        return alerts_created

    def resolve_alert(self, alert_id: int):
        """Mark an alert as resolved."""
        alert = self.db.query(Alert).filter(Alert.id == alert_id).first()
        if alert and not alert.is_resolved:
            alert.is_resolved = True
            alert.resolved_at = datetime.utcnow()
            self.db.commit()
            logger.info(f"Resolved alert {alert_id}")

    def get_active_alerts(self, participant_id: Optional[int] = None) -> List[Alert]:
        """Get all active (unresolved) alerts."""
        query = self.db.query(Alert).filter(Alert.is_resolved == False)
        if participant_id:
            query = query.filter(Alert.participant_id == participant_id)
        return query.order_by(Alert.triggered_at.desc()).all()
