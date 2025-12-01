#!/usr/bin/env python3
"""
Task Allocation Testing Script for Cocoon GPU Pool
Tests task distribution efficiency and fairness under high load
"""

import asyncio
import random
import time
import json
import statistics
from typing import List, Dict, Any
from dataclasses import dataclass, asdict, field
from datetime import datetime
import argparse


@dataclass
class TaskAllocationMetrics:
    """Metrics for task allocation performance"""
    test_name: str
    start_time: str
    end_time: str
    total_workers: int
    total_tasks: int
    tasks_allocated: int
    tasks_pending: int
    avg_allocation_latency: float
    p50_allocation_latency: float
    p95_allocation_latency: float
    p99_allocation_latency: float
    allocation_fairness_score: float  # Gini coefficient (0 = perfectly fair)
    worker_distribution: Dict[str, int] = field(default_factory=dict)
    test_passed: bool = False


class Task:
    """Represents a computation task"""

    def __init__(self, task_id: str, priority: int = 0, gpu_memory_required: int = 1024):
        self.task_id = task_id
        self.priority = priority
        self.gpu_memory_required = gpu_memory_required
        self.created_at = time.time()
        self.allocated_at = None
        self.worker_id = None

    def allocate_to_worker(self, worker_id: str):
        """Allocate task to a worker"""
        self.worker_id = worker_id
        self.allocated_at = time.time()

    def get_allocation_latency(self) -> float:
        """Get time from creation to allocation"""
        if self.allocated_at:
            return self.allocated_at - self.created_at
        return 0.0


class Worker:
    """Represents a GPU worker node"""

    def __init__(self, worker_id: str, gpu_memory: int = 24576, compute_capability: str = "8.9"):
        self.worker_id = worker_id
        self.gpu_memory = gpu_memory
        self.compute_capability = compute_capability
        self.available_memory = gpu_memory
        self.allocated_tasks: List[Task] = []
        self.completed_tasks: int = 0
        self.is_active = True

    def can_accept_task(self, task: Task) -> bool:
        """Check if worker can accept a task"""
        return (
            self.is_active and
            self.available_memory >= task.gpu_memory_required
        )

    def allocate_task(self, task: Task) -> bool:
        """Allocate a task to this worker"""
        if self.can_accept_task(task):
            self.allocated_tasks.append(task)
            self.available_memory -= task.gpu_memory_required
            task.allocate_to_worker(self.worker_id)
            return True
        return False

    def complete_task(self, task: Task):
        """Mark a task as completed"""
        if task in self.allocated_tasks:
            self.allocated_tasks.remove(task)
            self.available_memory += task.gpu_memory_required
            self.completed_tasks += 1


class TaskAllocationStrategy:
    """Base class for task allocation strategies"""

    def allocate(self, task: Task, workers: List[Worker]) -> Worker:
        """Allocate task to a worker"""
        raise NotImplementedError


class RoundRobinAllocation(TaskAllocationStrategy):
    """Round-robin task allocation"""

    def __init__(self):
        self.current_index = 0

    def allocate(self, task: Task, workers: List[Worker]) -> Worker:
        """Allocate using round-robin"""
        active_workers = [w for w in workers if w.is_active and w.can_accept_task(task)]
        if not active_workers:
            return None

        # Find next available worker
        for _ in range(len(active_workers)):
            worker = active_workers[self.current_index % len(active_workers)]
            self.current_index += 1
            if worker.can_accept_task(task):
                return worker

        return None


class LeastLoadedAllocation(TaskAllocationStrategy):
    """Allocate to worker with least load"""

    def allocate(self, task: Task, workers: List[Worker]) -> Worker:
        """Allocate to least loaded worker"""
        available_workers = [w for w in workers if w.can_accept_task(task)]
        if not available_workers:
            return None

        # Sort by current load (number of allocated tasks)
        available_workers.sort(key=lambda w: len(w.allocated_tasks))
        return available_workers[0]


class BestFitAllocation(TaskAllocationStrategy):
    """Allocate to worker with best-fitting resources"""

    def allocate(self, task: Task, workers: List[Worker]) -> Worker:
        """Allocate using best-fit strategy"""
        available_workers = [w for w in workers if w.can_accept_task(task)]
        if not available_workers:
            return None

        # Sort by available memory (ascending) to find best fit
        available_workers.sort(key=lambda w: w.available_memory)

        # Find worker with minimum available memory that can fit the task
        for worker in available_workers:
            if worker.available_memory >= task.gpu_memory_required:
                return worker

        return None


class TaskQueue:
    """Task queue with priority support"""

    def __init__(self):
        self.queue: List[Task] = []

    def enqueue(self, task: Task):
        """Add task to queue"""
        self.queue.append(task)
        # Sort by priority (higher priority first)
        self.queue.sort(key=lambda t: t.priority, reverse=True)

    def dequeue(self) -> Task:
        """Remove and return highest priority task"""
        if self.queue:
            return self.queue.pop(0)
        return None

    def size(self) -> int:
        """Get queue size"""
        return len(self.queue)

    def peek(self) -> Task:
        """Look at next task without removing"""
        return self.queue[0] if self.queue else None


class TaskAllocationSimulator:
    """Simulates task allocation under various conditions"""

    def __init__(self, num_workers: int, strategy: TaskAllocationStrategy):
        self.workers = [
            Worker(f"worker_{i:04d}", gpu_memory=24576)
            for i in range(num_workers)
        ]
        self.strategy = strategy
        self.task_queue = TaskQueue()
        self.completed_tasks: List[Task] = []
        self.allocation_latencies: List[float] = []

    async def generate_tasks(self, num_tasks: int, duration: int):
        """Generate tasks over a duration"""
        tasks_per_second = num_tasks / duration

        for i in range(num_tasks):
            task = Task(
                task_id=f"task_{i:06d}",
                priority=random.randint(1, 10),
                gpu_memory_required=random.choice([1024, 2048, 4096, 8192])
            )
            self.task_queue.enqueue(task)

            # Simulate task arrival pattern
            await asyncio.sleep(1.0 / tasks_per_second)

    async def allocate_tasks(self):
        """Continuously allocate tasks to workers"""
        while True:
            task = self.task_queue.dequeue()
            if not task:
                await asyncio.sleep(0.1)
                continue

            # Find suitable worker
            worker = self.strategy.allocate(task, self.workers)

            if worker:
                success = worker.allocate_task(task)
                if success:
                    latency = task.get_allocation_latency()
                    self.allocation_latencies.append(latency)
                else:
                    # Re-queue task if allocation failed
                    self.task_queue.enqueue(task)
                    await asyncio.sleep(0.1)
            else:
                # No suitable worker, re-queue
                self.task_queue.enqueue(task)
                await asyncio.sleep(0.1)

    async def process_tasks(self):
        """Simulate task processing by workers"""
        while True:
            for worker in self.workers:
                if worker.allocated_tasks:
                    # Simulate task completion (random)
                    if random.random() < 0.1:  # 10% chance per iteration
                        task = random.choice(worker.allocated_tasks)
                        worker.complete_task(task)
                        self.completed_tasks.append(task)

            await asyncio.sleep(0.5)

    async def run_simulation(self, num_tasks: int, duration: int) -> TaskAllocationMetrics:
        """Run complete allocation simulation"""
        print(f"Starting task allocation simulation")
        print(f"Workers: {len(self.workers)}, Tasks: {num_tasks}, Duration: {duration}s")

        start_time = datetime.now()

        # Start allocation and processing
        allocator_task = asyncio.create_task(self.allocate_tasks())
        processor_task = asyncio.create_task(self.process_tasks())
        generator_task = asyncio.create_task(self.generate_tasks(num_tasks, duration))

        # Wait for task generation to complete
        await generator_task

        # Wait a bit more for allocation to catch up
        await asyncio.sleep(5)

        # Stop allocation and processing
        allocator_task.cancel()
        processor_task.cancel()

        end_time = datetime.now()

        # Calculate metrics
        return self._calculate_metrics(start_time, end_time, num_tasks)

    def _calculate_metrics(self, start_time: datetime, end_time: datetime,
                          total_tasks: int) -> TaskAllocationMetrics:
        """Calculate allocation metrics"""
        # Count tasks by worker
        worker_task_counts = {w.worker_id: w.completed_tasks for w in self.workers}

        # Calculate fairness (Gini coefficient)
        fairness_score = self._calculate_gini_coefficient(list(worker_task_counts.values()))

        # Calculate latency percentiles
        self.allocation_latencies.sort()

        return TaskAllocationMetrics(
            test_name=f"Task Allocation Test - {self.strategy.__class__.__name__}",
            start_time=start_time.isoformat(),
            end_time=end_time.isoformat(),
            total_workers=len(self.workers),
            total_tasks=total_tasks,
            tasks_allocated=len(self.completed_tasks) + sum(len(w.allocated_tasks) for w in self.workers),
            tasks_pending=self.task_queue.size(),
            avg_allocation_latency=statistics.mean(self.allocation_latencies) if self.allocation_latencies else 0,
            p50_allocation_latency=self._percentile(self.allocation_latencies, 50),
            p95_allocation_latency=self._percentile(self.allocation_latencies, 95),
            p99_allocation_latency=self._percentile(self.allocation_latencies, 99),
            allocation_fairness_score=fairness_score,
            worker_distribution=worker_task_counts,
            test_passed=self._check_acceptance_criteria(fairness_score)
        )

    @staticmethod
    def _calculate_gini_coefficient(values: List[int]) -> float:
        """Calculate Gini coefficient for fairness (0 = perfect equality)"""
        if not values or sum(values) == 0:
            return 0.0

        sorted_values = sorted(values)
        n = len(sorted_values)
        cumsum = 0
        for i, value in enumerate(sorted_values):
            cumsum += (n - i) * value

        return (2 * cumsum) / (n * sum(sorted_values)) - (n + 1) / n

    @staticmethod
    def _percentile(data: List[float], percentile: int) -> float:
        """Calculate percentile"""
        if not data:
            return 0.0
        index = int(len(data) * percentile / 100)
        return data[min(index, len(data) - 1)]

    def _check_acceptance_criteria(self, fairness_score: float) -> bool:
        """Check if results meet acceptance criteria"""
        return (
            fairness_score < 0.2 and  # Fair distribution
            (self._percentile(self.allocation_latencies, 95) < 0.5 if self.allocation_latencies else False) and  # P95 < 500ms
            self.task_queue.size() < total_tasks * 0.05  # Less than 5% pending
        )

    def print_results(self, metrics: TaskAllocationMetrics):
        """Print simulation results"""
        print("\n" + "="*80)
        print("TASK ALLOCATION TEST RESULTS")
        print("="*80)
        print(f"Test: {metrics.test_name}")
        print(f"Start Time: {metrics.start_time}")
        print(f"End Time: {metrics.end_time}")
        print(f"\nWorkers: {metrics.total_workers}")
        print(f"Total Tasks: {metrics.total_tasks}")
        print(f"Tasks Allocated: {metrics.tasks_allocated}")
        print(f"Tasks Pending: {metrics.tasks_pending}")
        print(f"\nAllocation Latency:")
        print(f"  Average: {metrics.avg_allocation_latency*1000:.2f}ms")
        print(f"  P50: {metrics.p50_allocation_latency*1000:.2f}ms")
        print(f"  P95: {metrics.p95_allocation_latency*1000:.2f}ms")
        print(f"  P99: {metrics.p99_allocation_latency*1000:.2f}ms")
        print(f"\nFairness Score (Gini): {metrics.allocation_fairness_score:.3f}")
        print(f"  (0.0 = perfectly fair, 1.0 = completely unfair)")
        print("\nWorker Distribution (top 10):")

        sorted_workers = sorted(metrics.worker_distribution.items(),
                              key=lambda x: x[1], reverse=True)
        for worker_id, task_count in sorted_workers[:10]:
            print(f"  {worker_id}: {task_count} tasks")

        print(f"\nTest Result: {'PASS' if metrics.test_passed else 'FAIL'}")
        print("="*80)

        # Acceptance criteria
        print("\nACCEPTANCE CRITERIA:")
        criteria = [
            ("Fair distribution (Gini < 0.2)", metrics.allocation_fairness_score < 0.2,
             "✅" if metrics.allocation_fairness_score < 0.2 else "❌"),
            ("P95 latency < 500ms", metrics.p95_allocation_latency < 0.5,
             "✅" if metrics.p95_allocation_latency < 0.5 else "❌"),
            ("Pending tasks < 5%", metrics.tasks_pending < metrics.total_tasks * 0.05,
             "✅" if metrics.tasks_pending < metrics.total_tasks * 0.05 else "❌"),
        ]

        for criterion, passed, symbol in criteria:
            print(f"{symbol} {criterion}: {'PASS' if passed else 'FAIL'}")

    def save_results(self, metrics: TaskAllocationMetrics, filename: str):
        """Save results to JSON file"""
        with open(filename, 'w') as f:
            json.dump(asdict(metrics), f, indent=2)
        print(f"\nResults saved to {filename}")


async def run_comparative_tests():
    """Run tests with different allocation strategies"""
    strategies = [
        ("Round Robin", RoundRobinAllocation()),
        ("Least Loaded", LeastLoadedAllocation()),
        ("Best Fit", BestFitAllocation()),
    ]

    num_workers = 100
    num_tasks = 10000
    duration = 60  # seconds

    results = []

    for strategy_name, strategy in strategies:
        print(f"\n{'='*80}")
        print(f"Testing {strategy_name} Strategy")
        print(f"{'='*80}")

        simulator = TaskAllocationSimulator(num_workers, strategy)
        metrics = await simulator.run_simulation(num_tasks, duration)
        simulator.print_results(metrics)
        simulator.save_results(metrics, f"task_allocation_{strategy_name.lower().replace(' ', '_')}.json")

        results.append((strategy_name, metrics))

    # Print comparison
    print(f"\n{'='*80}")
    print("STRATEGY COMPARISON")
    print(f"{'='*80}")
    print(f"{'Strategy':<20} {'Fairness':<12} {'P95 Latency':<15} {'Pending':<10} {'Result'}")
    print("-" * 80)

    for strategy_name, metrics in results:
        print(f"{strategy_name:<20} {metrics.allocation_fairness_score:<12.3f} "
              f"{metrics.p95_allocation_latency*1000:<15.2f}ms "
              f"{metrics.tasks_pending:<10} {'PASS' if metrics.test_passed else 'FAIL'}")


async def main():
    parser = argparse.ArgumentParser(description='Task allocation testing for Cocoon GPU Pool')
    parser.add_argument('--workers', type=int, default=100, help='Number of workers')
    parser.add_argument('--tasks', type=int, default=10000, help='Number of tasks')
    parser.add_argument('--duration', type=int, default=60, help='Test duration in seconds')
    parser.add_argument('--strategy', choices=['roundrobin', 'leastloaded', 'bestfit', 'all'],
                       default='all', help='Allocation strategy to test')
    parser.add_argument('--output', default='task_allocation_results.json', help='Output file')

    args = parser.parse_args()

    if args.strategy == 'all':
        await run_comparative_tests()
    else:
        strategy_map = {
            'roundrobin': RoundRobinAllocation(),
            'leastloaded': LeastLoadedAllocation(),
            'bestfit': BestFitAllocation(),
        }

        strategy = strategy_map[args.strategy]
        simulator = TaskAllocationSimulator(args.workers, strategy)
        metrics = await simulator.run_simulation(args.tasks, args.duration)
        simulator.print_results(metrics)
        simulator.save_results(metrics, args.output)


if __name__ == "__main__":
    # Make total_tasks available for acceptance criteria check
    total_tasks = 10000
    asyncio.run(main())
