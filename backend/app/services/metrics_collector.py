"""Metrics collector service for scraping worker endpoints."""
import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, Any
import aiohttp
from sqlalchemy.orm import Session
from ..models.worker import Worker
from ..models.worker_metric import WorkerMetric
from ..core.config import settings

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Collects metrics from GPU workers."""

    def __init__(self, db: Session):
        self.db = db
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Context manager entry."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=5)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.session:
            await self.session.close()

    async def fetch_worker_stats(
        self, worker: Worker, endpoint: str = "/jsonstats"
    ) -> Optional[Dict[str, Any]]:
        """Fetch JSON stats from a worker endpoint."""
        if not self.session:
            raise RuntimeError("MetricsCollector must be used as context manager")

        url = f"http://{worker.host}:{worker.stats_port}{endpoint}"
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.warning(
                        f"Worker {worker.id} returned status {response.status} for {url}"
                    )
                    return None
        except asyncio.TimeoutError:
            logger.error(f"Timeout fetching stats from worker {worker.id} at {url}")
            return None
        except aiohttp.ClientError as e:
            logger.error(f"Error fetching stats from worker {worker.id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching stats from worker {worker.id}: {e}")
            return None

    async def fetch_worker_perf(self, worker: Worker) -> Optional[Dict[str, Any]]:
        """Fetch performance metrics from worker /perf endpoint."""
        return await self.fetch_worker_stats(worker, "/perf")

    def parse_metrics(
        self,
        stats: Optional[Dict[str, Any]],
        perf: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Parse raw stats and perf data into structured metrics."""
        metrics = {
            "raw_stats": stats,
            "raw_perf": perf,
            "status": "healthy",
        }

        if not stats and not perf:
            metrics["status"] = "down"
            return metrics

        # Parse GPU metrics from stats
        if stats:
            # Example parsing - adjust based on actual response format
            if "gpu" in stats:
                gpu_data = stats["gpu"]
                metrics["gpu_utilization"] = gpu_data.get("utilization")
                metrics["gpu_memory_used"] = gpu_data.get("memory_used")
                metrics["gpu_memory_total"] = gpu_data.get("memory_total")
                metrics["gpu_temperature"] = gpu_data.get("temperature")
                metrics["gpu_power_usage"] = gpu_data.get("power_usage")

            # Parse request metrics
            if "requests" in stats:
                req_data = stats["requests"]
                metrics["inference_requests_total"] = req_data.get("total", 0)
                metrics["inference_requests_success"] = req_data.get("success", 0)
                metrics["inference_requests_failed"] = req_data.get("failed", 0)

            # Parse revenue
            if "revenue" in stats:
                metrics["revenue_ton"] = stats["revenue"].get("ton", 0.0)

        # Parse performance metrics
        if perf:
            if "latency" in perf:
                metrics["avg_inference_latency_ms"] = perf["latency"].get("avg_ms")
            if "throughput" in perf:
                metrics["requests_per_minute"] = perf["throughput"].get("rpm")

        # Determine status based on metrics
        if metrics.get("gpu_utilization", 0) == 0:
            metrics["status"] = "degraded"
        if metrics.get("gpu_temperature", 0) > 85:
            metrics["status"] = "warning"

        return metrics

    async def collect_worker_metrics(self, worker: Worker) -> Optional[WorkerMetric]:
        """Collect metrics for a single worker."""
        logger.info(f"Collecting metrics for worker {worker.id} ({worker.worker_name})")

        # Fetch data from both endpoints
        stats = await self.fetch_worker_stats(worker, "/jsonstats")
        perf = await self.fetch_worker_perf(worker)

        # Parse metrics
        parsed = self.parse_metrics(stats, perf)

        # Update worker last_seen
        worker.last_seen = datetime.utcnow()
        self.db.add(worker)

        # Create metric record
        metric = WorkerMetric(
            worker_id=worker.id,
            timestamp=datetime.utcnow(),
            **parsed
        )
        self.db.add(metric)
        self.db.commit()
        self.db.refresh(metric)

        logger.info(
            f"Collected metrics for worker {worker.id}: "
            f"status={metric.status}, "
            f"gpu_util={metric.gpu_utilization}%"
        )

        return metric

    async def collect_all_workers(self):
        """Collect metrics for all active workers."""
        workers = self.db.query(Worker).filter(Worker.is_active == True).all()

        if not workers:
            logger.info("No active workers to monitor")
            return

        logger.info(f"Collecting metrics for {len(workers)} active workers")

        # Collect metrics concurrently
        tasks = [self.collect_worker_metrics(worker) for worker in workers]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Log any errors
        for worker, result in zip(workers, results):
            if isinstance(result, Exception):
                logger.error(f"Error collecting metrics for worker {worker.id}: {result}")

        logger.info("Metrics collection completed")


async def run_metrics_collector(db: Session):
    """Run the metrics collector once."""
    async with MetricsCollector(db) as collector:
        await collector.collect_all_workers()
