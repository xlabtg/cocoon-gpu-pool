#!/usr/bin/env python3
"""
Load Testing Script for Cocoon GPU Pool
Tests system performance with 1000+ concurrent participants
"""

import asyncio
import time
import json
import statistics
from typing import List, Dict, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import aiohttp
import argparse


@dataclass
class LoadTestConfig:
    """Configuration for load testing"""
    base_url: str = "http://localhost:8000"
    num_workers: int = 1000
    ramp_up_time: int = 300  # seconds
    test_duration: int = 3600  # seconds
    tasks_per_worker: int = 10
    think_time: float = 1.0  # seconds between requests
    timeout: int = 30  # request timeout


@dataclass
class WorkerMetrics:
    """Metrics for a single worker"""
    worker_id: str
    requests_sent: int = 0
    requests_succeeded: int = 0
    requests_failed: int = 0
    total_response_time: float = 0.0
    min_response_time: float = float('inf')
    max_response_time: float = 0.0
    response_times: List[float] = None

    def __post_init__(self):
        if self.response_times is None:
            self.response_times = []


@dataclass
class LoadTestResults:
    """Aggregated load test results"""
    test_name: str
    start_time: str
    end_time: str
    duration: float
    total_workers: int
    total_requests: int
    successful_requests: int
    failed_requests: int
    requests_per_second: float
    avg_response_time: float
    p50_response_time: float
    p95_response_time: float
    p99_response_time: float
    min_response_time: float
    max_response_time: float
    error_rate: float


class LoadTestClient:
    """Simulated worker client for load testing"""

    def __init__(self, worker_id: str, config: LoadTestConfig):
        self.worker_id = worker_id
        self.config = config
        self.metrics = WorkerMetrics(worker_id=worker_id)
        self.session = None

    async def initialize(self):
        """Initialize HTTP session"""
        timeout = aiohttp.ClientTimeout(total=self.config.timeout)
        self.session = aiohttp.ClientSession(timeout=timeout)

    async def cleanup(self):
        """Clean up resources"""
        if self.session:
            await self.session.close()

    async def register_worker(self) -> bool:
        """Register worker with pool gateway"""
        url = f"{self.config.base_url}/api/v1/workers/register"
        payload = {
            "worker_id": self.worker_id,
            "gpu_model": "NVIDIA RTX 4090",
            "gpu_memory": 24576,
            "compute_capability": "8.9",
            "attestation_quote": f"mock_quote_{self.worker_id}"
        }

        start_time = time.time()
        try:
            async with self.session.post(url, json=payload) as response:
                elapsed = time.time() - start_time
                self.metrics.requests_sent += 1
                self.metrics.response_times.append(elapsed)

                if response.status == 200:
                    self.metrics.requests_succeeded += 1
                    self.metrics.total_response_time += elapsed
                    self.metrics.min_response_time = min(self.metrics.min_response_time, elapsed)
                    self.metrics.max_response_time = max(self.metrics.max_response_time, elapsed)
                    return True
                else:
                    self.metrics.requests_failed += 1
                    return False
        except Exception as e:
            elapsed = time.time() - start_time
            self.metrics.requests_sent += 1
            self.metrics.requests_failed += 1
            print(f"Worker {self.worker_id} registration failed: {e}")
            return False

    async def request_task(self) -> Dict[str, Any]:
        """Request a task from pool gateway"""
        url = f"{self.config.base_url}/api/v1/tasks/request"
        payload = {"worker_id": self.worker_id}

        start_time = time.time()
        try:
            async with self.session.post(url, json=payload) as response:
                elapsed = time.time() - start_time
                self.metrics.requests_sent += 1
                self.metrics.response_times.append(elapsed)

                if response.status == 200:
                    self.metrics.requests_succeeded += 1
                    self.metrics.total_response_time += elapsed
                    self.metrics.min_response_time = min(self.metrics.min_response_time, elapsed)
                    self.metrics.max_response_time = max(self.metrics.max_response_time, elapsed)
                    return await response.json()
                else:
                    self.metrics.requests_failed += 1
                    return None
        except Exception as e:
            elapsed = time.time() - start_time
            self.metrics.requests_sent += 1
            self.metrics.requests_failed += 1
            return None

    async def submit_result(self, task_id: str, result: str) -> bool:
        """Submit task result"""
        url = f"{self.config.base_url}/api/v1/tasks/submit"
        payload = {
            "worker_id": self.worker_id,
            "task_id": task_id,
            "result": result,
            "signature": f"mock_signature_{task_id}"
        }

        start_time = time.time()
        try:
            async with self.session.post(url, json=payload) as response:
                elapsed = time.time() - start_time
                self.metrics.requests_sent += 1
                self.metrics.response_times.append(elapsed)

                if response.status == 200:
                    self.metrics.requests_succeeded += 1
                    self.metrics.total_response_time += elapsed
                    self.metrics.min_response_time = min(self.metrics.min_response_time, elapsed)
                    self.metrics.max_response_time = max(self.metrics.max_response_time, elapsed)
                    return True
                else:
                    self.metrics.requests_failed += 1
                    return False
        except Exception as e:
            elapsed = time.time() - start_time
            self.metrics.requests_sent += 1
            self.metrics.requests_failed += 1
            return False

    async def run_worker_lifecycle(self):
        """Simulate complete worker lifecycle"""
        await self.initialize()

        try:
            # Register worker
            if not await self.register_worker():
                print(f"Worker {self.worker_id} failed to register")
                return

            # Process tasks
            for _ in range(self.config.tasks_per_worker):
                # Request task
                task = await self.request_task()
                if task:
                    # Simulate computation
                    await asyncio.sleep(0.1)

                    # Submit result
                    await self.submit_result(task.get('task_id', 'unknown'), "result_data")

                # Think time between requests
                await asyncio.sleep(self.config.think_time)

        finally:
            await self.cleanup()


class LoadTestOrchestrator:
    """Orchestrates load testing across multiple workers"""

    def __init__(self, config: LoadTestConfig):
        self.config = config
        self.workers: List[LoadTestClient] = []
        self.results: List[WorkerMetrics] = []

    async def run_test(self) -> LoadTestResults:
        """Execute load test"""
        print(f"Starting load test with {self.config.num_workers} workers")
        print(f"Ramp-up time: {self.config.ramp_up_time}s")
        print(f"Test duration: {self.config.test_duration}s")

        start_time = datetime.now()

        # Create workers
        self.workers = [
            LoadTestClient(f"worker_{i:05d}", self.config)
            for i in range(self.config.num_workers)
        ]

        # Ramp up workers gradually
        ramp_delay = self.config.ramp_up_time / self.config.num_workers
        tasks = []

        for i, worker in enumerate(self.workers):
            if i > 0:
                await asyncio.sleep(ramp_delay)
            tasks.append(asyncio.create_task(worker.run_worker_lifecycle()))

            if (i + 1) % 100 == 0:
                print(f"Spawned {i + 1} workers")

        # Wait for all workers to complete
        print(f"All workers spawned, waiting for completion...")
        await asyncio.gather(*tasks, return_exceptions=True)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Aggregate metrics
        self.results = [worker.metrics for worker in self.workers]
        return self._aggregate_results(start_time, end_time, duration)

    def _aggregate_results(self, start_time: datetime, end_time: datetime,
                          duration: float) -> LoadTestResults:
        """Aggregate metrics from all workers"""
        total_requests = sum(m.requests_sent for m in self.results)
        successful_requests = sum(m.requests_succeeded for m in self.results)
        failed_requests = sum(m.requests_failed for m in self.results)

        # Collect all response times
        all_response_times = []
        for metrics in self.results:
            all_response_times.extend(metrics.response_times)

        all_response_times.sort()

        return LoadTestResults(
            test_name="Load Test - 1000+ Workers",
            start_time=start_time.isoformat(),
            end_time=end_time.isoformat(),
            duration=duration,
            total_workers=self.config.num_workers,
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            requests_per_second=total_requests / duration if duration > 0 else 0,
            avg_response_time=statistics.mean(all_response_times) if all_response_times else 0,
            p50_response_time=self._percentile(all_response_times, 50),
            p95_response_time=self._percentile(all_response_times, 95),
            p99_response_time=self._percentile(all_response_times, 99),
            min_response_time=min(all_response_times) if all_response_times else 0,
            max_response_time=max(all_response_times) if all_response_times else 0,
            error_rate=(failed_requests / total_requests * 100) if total_requests > 0 else 0
        )

    @staticmethod
    def _percentile(data: List[float], percentile: int) -> float:
        """Calculate percentile of data"""
        if not data:
            return 0.0
        index = int(len(data) * percentile / 100)
        return data[min(index, len(data) - 1)]

    def print_results(self, results: LoadTestResults):
        """Print test results"""
        print("\n" + "="*80)
        print("LOAD TEST RESULTS")
        print("="*80)
        print(f"Test Name: {results.test_name}")
        print(f"Start Time: {results.start_time}")
        print(f"End Time: {results.end_time}")
        print(f"Duration: {results.duration:.2f}s")
        print(f"\nWorkers: {results.total_workers}")
        print(f"Total Requests: {results.total_requests}")
        print(f"Successful: {results.successful_requests}")
        print(f"Failed: {results.failed_requests}")
        print(f"Error Rate: {results.error_rate:.2f}%")
        print(f"\nThroughput: {results.requests_per_second:.2f} req/s")
        print(f"\nResponse Times:")
        print(f"  Average: {results.avg_response_time*1000:.2f}ms")
        print(f"  P50: {results.p50_response_time*1000:.2f}ms")
        print(f"  P95: {results.p95_response_time*1000:.2f}ms")
        print(f"  P99: {results.p99_response_time*1000:.2f}ms")
        print(f"  Min: {results.min_response_time*1000:.2f}ms")
        print(f"  Max: {results.max_response_time*1000:.2f}ms")
        print("="*80)

        # Check acceptance criteria
        print("\nACCEPTANCE CRITERIA:")
        self._check_criteria(results)

    def _check_criteria(self, results: LoadTestResults):
        """Check if results meet acceptance criteria"""
        criteria = [
            ("System handles 1000+ workers", results.total_workers >= 1000, "✅" if results.total_workers >= 1000 else "❌"),
            ("P95 latency < 500ms", results.p95_response_time < 0.5, "✅" if results.p95_response_time < 0.5 else "❌"),
            ("P99 latency < 2000ms", results.p99_response_time < 2.0, "✅" if results.p99_response_time < 2.0 else "❌"),
            ("Error rate < 1%", results.error_rate < 1.0, "✅" if results.error_rate < 1.0 else "❌"),
        ]

        for criterion, passed, symbol in criteria:
            print(f"{symbol} {criterion}: {'PASS' if passed else 'FAIL'}")

    def save_results(self, results: LoadTestResults, filename: str):
        """Save results to JSON file"""
        with open(filename, 'w') as f:
            json.dump(asdict(results), f, indent=2)
        print(f"\nResults saved to {filename}")


async def main():
    parser = argparse.ArgumentParser(description='Load testing for Cocoon GPU Pool')
    parser.add_argument('--url', default='http://localhost:8000', help='Base URL of the pool gateway')
    parser.add_argument('--workers', type=int, default=1000, help='Number of workers to simulate')
    parser.add_argument('--ramp-up', type=int, default=300, help='Ramp-up time in seconds')
    parser.add_argument('--duration', type=int, default=3600, help='Test duration in seconds')
    parser.add_argument('--tasks', type=int, default=10, help='Tasks per worker')
    parser.add_argument('--output', default='load_test_results.json', help='Output file for results')

    args = parser.parse_args()

    config = LoadTestConfig(
        base_url=args.url,
        num_workers=args.workers,
        ramp_up_time=args.ramp_up,
        test_duration=args.duration,
        tasks_per_worker=args.tasks
    )

    orchestrator = LoadTestOrchestrator(config)
    results = await orchestrator.run_test()
    orchestrator.print_results(results)
    orchestrator.save_results(results, args.output)


if __name__ == "__main__":
    asyncio.run(main())
