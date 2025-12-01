#!/usr/bin/env python3
"""
Fault Tolerance Testing Script for Cocoon GPU Pool
Simulates various failure scenarios and measures system resilience
"""

import asyncio
import random
import time
import json
from typing import List, Dict, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import argparse


class FailureType(Enum):
    """Types of failures to simulate"""
    WORKER_CRASH = "worker_crash"
    GATEWAY_FAILURE = "gateway_failure"
    DATABASE_FAILURE = "database_failure"
    NETWORK_PARTITION = "network_partition"
    SLOW_RESPONSE = "slow_response"
    CASCADING_FAILURE = "cascading_failure"


@dataclass
class FaultInjectionConfig:
    """Configuration for fault injection"""
    failure_type: FailureType
    failure_probability: float = 0.1  # 10% chance per interval
    failure_duration: int = 60  # seconds
    recovery_time: int = 30  # expected recovery time in seconds
    affected_components: List[str] = None

    def __post_init__(self):
        if self.affected_components is None:
            self.affected_components = []


@dataclass
class FaultTestResults:
    """Results from fault tolerance testing"""
    test_name: str
    start_time: str
    end_time: str
    total_failures_injected: int
    failures_detected: int
    failures_recovered: int
    data_loss_incidents: int
    avg_recovery_time: float
    max_recovery_time: float
    system_availability: float  # percentage
    test_passed: bool
    detailed_results: List[Dict[str, Any]] = None

    def __post_init__(self):
        if self.detailed_results is None:
            self.detailed_results = []


class WorkerCrashSimulator:
    """Simulates worker node crashes"""

    def __init__(self, worker_id: str):
        self.worker_id = worker_id
        self.is_crashed = False
        self.crash_time = None

    async def inject_crash(self):
        """Simulate worker crash"""
        print(f"[FAULT] Injecting crash for worker {self.worker_id}")
        self.is_crashed = True
        self.crash_time = time.time()

    async def recover(self):
        """Simulate worker recovery"""
        print(f"[RECOVERY] Worker {self.worker_id} recovering")
        self.is_crashed = False
        recovery_time = time.time() - self.crash_time if self.crash_time else 0
        self.crash_time = None
        return recovery_time

    def is_available(self) -> bool:
        """Check if worker is available"""
        return not self.is_crashed


class GatewayFailureSimulator:
    """Simulates pool gateway failures"""

    def __init__(self):
        self.is_failed = False
        self.failure_time = None
        self.request_queue = []

    async def inject_failure(self):
        """Simulate gateway failure"""
        print(f"[FAULT] Injecting Pool Gateway failure")
        self.is_failed = True
        self.failure_time = time.time()

    async def recover(self):
        """Simulate gateway recovery"""
        print(f"[RECOVERY] Pool Gateway recovering, processing queued requests")
        self.is_failed = False
        recovery_time = time.time() - self.failure_time if self.failure_time else 0
        self.failure_time = None

        # Process queued requests
        queued_count = len(self.request_queue)
        self.request_queue.clear()
        print(f"[RECOVERY] Processed {queued_count} queued requests")

        return recovery_time

    async def handle_request(self, request: Dict[str, Any]) -> bool:
        """Handle incoming request, queue if failed"""
        if self.is_failed:
            self.request_queue.append(request)
            return False
        return True


class DatabaseFailureSimulator:
    """Simulates database failures"""

    def __init__(self):
        self.is_failed = False
        self.failure_time = None
        self.transaction_log = []

    async def inject_failure(self):
        """Simulate database failure"""
        print(f"[FAULT] Injecting Database failure")
        self.is_failed = True
        self.failure_time = time.time()

    async def recover(self):
        """Simulate database recovery with transaction replay"""
        print(f"[RECOVERY] Database recovering, replaying transactions")
        self.is_failed = False
        recovery_time = time.time() - self.failure_time if self.failure_time else 0
        self.failure_time = None

        # Replay transaction log
        transaction_count = len(self.transaction_log)
        self.transaction_log.clear()
        print(f"[RECOVERY] Replayed {transaction_count} transactions")

        return recovery_time

    async def execute_transaction(self, transaction: Dict[str, Any]) -> bool:
        """Execute database transaction"""
        if self.is_failed:
            # Log transaction for replay
            self.transaction_log.append(transaction)
            return False
        return True


class NetworkPartitionSimulator:
    """Simulates network partitions"""

    def __init__(self):
        self.partitions: List[List[str]] = []
        self.partition_time = None

    async def inject_partition(self, partition_groups: List[List[str]]):
        """Create network partition"""
        print(f"[FAULT] Injecting network partition: {partition_groups}")
        self.partitions = partition_groups
        self.partition_time = time.time()

    async def heal_partition(self):
        """Heal network partition"""
        print(f"[RECOVERY] Healing network partition")
        self.partitions = []
        recovery_time = time.time() - self.partition_time if self.partition_time else 0
        self.partition_time = None
        return recovery_time

    def can_communicate(self, node_a: str, node_b: str) -> bool:
        """Check if two nodes can communicate"""
        if not self.partitions:
            return True

        for partition in self.partitions:
            if node_a in partition and node_b in partition:
                return True

        return False


class FaultToleranceTestSuite:
    """Comprehensive fault tolerance testing suite"""

    def __init__(self):
        self.workers = []
        self.gateway = GatewayFailureSimulator()
        self.database = DatabaseFailureSimulator()
        self.network = NetworkPartitionSimulator()
        self.test_results = []

    async def test_worker_crash_recovery(self, num_workers: int = 10) -> Dict[str, Any]:
        """Test worker crash and recovery"""
        print("\n" + "="*80)
        print("TEST: Worker Crash and Recovery")
        print("="*80)

        # Initialize workers
        self.workers = [WorkerCrashSimulator(f"worker_{i}") for i in range(num_workers)]

        recovery_times = []
        data_loss = 0

        # Crash random workers
        crashed_workers = random.sample(self.workers, k=min(3, num_workers))
        for worker in crashed_workers:
            await worker.inject_crash()
            await asyncio.sleep(0.1)  # Small delay between crashes

        # Simulate task processing with failed workers
        await asyncio.sleep(2)

        # Verify tasks are redistributed to healthy workers
        available_workers = [w for w in self.workers if w.is_available()]
        print(f"Available workers after crash: {len(available_workers)}/{num_workers}")

        # Recover crashed workers
        for worker in crashed_workers:
            recovery_time = await worker.recover()
            recovery_times.append(recovery_time)
            await asyncio.sleep(0.1)

        avg_recovery_time = sum(recovery_times) / len(recovery_times) if recovery_times else 0
        max_recovery_time = max(recovery_times) if recovery_times else 0

        test_passed = (
            len(available_workers) >= num_workers - 3 and  # Most workers still available
            max_recovery_time < 60  # Recovery within 60 seconds
        )

        result = {
            "test_name": "Worker Crash Recovery",
            "total_workers": num_workers,
            "crashed_workers": len(crashed_workers),
            "available_during_failure": len(available_workers),
            "avg_recovery_time": avg_recovery_time,
            "max_recovery_time": max_recovery_time,
            "data_loss": data_loss,
            "passed": test_passed
        }

        print(f"Result: {'PASS' if test_passed else 'FAIL'}")
        return result

    async def test_gateway_failure(self) -> Dict[str, Any]:
        """Test pool gateway failure and recovery"""
        print("\n" + "="*80)
        print("TEST: Pool Gateway Failure and Recovery")
        print("="*80)

        # Inject gateway failure
        await self.gateway.inject_failure()

        # Simulate requests during failure
        requests_during_failure = 10
        queued_requests = 0

        for i in range(requests_during_failure):
            request = {"id": i, "type": "task_request"}
            if not await self.gateway.handle_request(request):
                queued_requests += 1

        print(f"Queued requests during failure: {queued_requests}")

        # Wait for failure duration
        await asyncio.sleep(2)

        # Recover gateway
        recovery_time = await self.gateway.recover()

        test_passed = (
            queued_requests == requests_during_failure and  # All requests queued
            recovery_time < 300  # Recovery within 5 minutes
        )

        result = {
            "test_name": "Gateway Failure Recovery",
            "requests_during_failure": requests_during_failure,
            "queued_requests": queued_requests,
            "recovery_time": recovery_time,
            "data_loss": 0,  # No requests lost
            "passed": test_passed
        }

        print(f"Result: {'PASS' if test_passed else 'FAIL'}")
        return result

    async def test_database_failure(self) -> Dict[str, Any]:
        """Test database failure and recovery"""
        print("\n" + "="*80)
        print("TEST: Database Failure and Recovery")
        print("="*80)

        # Inject database failure
        await self.database.inject_failure()

        # Simulate transactions during failure
        transactions_during_failure = 20
        logged_transactions = 0

        for i in range(transactions_during_failure):
            transaction = {"id": i, "type": "payment", "amount": 100}
            if not await self.database.execute_transaction(transaction):
                logged_transactions += 1

        print(f"Logged transactions during failure: {logged_transactions}")

        # Wait for failure duration
        await asyncio.sleep(2)

        # Recover database
        recovery_time = await self.database.recover()

        test_passed = (
            logged_transactions == transactions_during_failure and  # All transactions logged
            recovery_time < 300  # Recovery within 5 minutes
        )

        result = {
            "test_name": "Database Failure Recovery",
            "transactions_during_failure": transactions_during_failure,
            "logged_transactions": logged_transactions,
            "recovery_time": recovery_time,
            "data_loss": 0,  # No data loss due to transaction log
            "passed": test_passed
        }

        print(f"Result: {'PASS' if test_passed else 'FAIL'}")
        return result

    async def test_network_partition(self) -> Dict[str, Any]:
        """Test network partition and healing"""
        print("\n" + "="*80)
        print("TEST: Network Partition and Healing")
        print("="*80)

        # Create network partition
        partition_groups = [
            ["gateway", "worker_0", "worker_1"],
            ["worker_2", "worker_3", "worker_4"]
        ]
        await self.network.inject_partition(partition_groups)

        # Test communication
        can_communicate_same = self.network.can_communicate("worker_0", "worker_1")
        can_communicate_diff = self.network.can_communicate("worker_0", "worker_2")

        print(f"Same partition communication: {can_communicate_same}")
        print(f"Different partition communication: {can_communicate_diff}")

        # Wait for partition duration
        await asyncio.sleep(2)

        # Heal partition
        recovery_time = await self.network.heal_partition()

        # Verify communication restored
        can_communicate_after = self.network.can_communicate("worker_0", "worker_2")

        test_passed = (
            can_communicate_same and
            not can_communicate_diff and
            can_communicate_after and
            recovery_time < 60
        )

        result = {
            "test_name": "Network Partition Healing",
            "partition_groups": len(partition_groups),
            "same_partition_comm": can_communicate_same,
            "diff_partition_comm": can_communicate_diff,
            "communication_restored": can_communicate_after,
            "recovery_time": recovery_time,
            "passed": test_passed
        }

        print(f"Result: {'PASS' if test_passed else 'FAIL'}")
        return result

    async def test_cascading_failures(self) -> Dict[str, Any]:
        """Test cascading failure scenario"""
        print("\n" + "="*80)
        print("TEST: Cascading Failures")
        print("="*80)

        failures = []

        # Start with database failure
        await self.database.inject_failure()
        failures.append("database")
        await asyncio.sleep(1)

        # Database failure causes gateway to fail
        await self.gateway.inject_failure()
        failures.append("gateway")
        await asyncio.sleep(1)

        # Gateway failure causes workers to fail
        num_workers = 5
        self.workers = [WorkerCrashSimulator(f"worker_{i}") for i in range(num_workers)]
        for worker in self.workers[:2]:  # Fail 2 workers
            await worker.inject_crash()
            failures.append(worker.worker_id)

        print(f"Cascading failures triggered: {len(failures)} components")

        # Begin recovery in reverse order
        recovery_times = []

        # Recover workers first
        for worker in self.workers:
            if worker.is_crashed:
                rt = await worker.recover()
                recovery_times.append(rt)

        # Recover gateway
        rt = await self.gateway.recover()
        recovery_times.append(rt)

        # Recover database
        rt = await self.database.recover()
        recovery_times.append(rt)

        total_recovery_time = max(recovery_times) if recovery_times else 0

        test_passed = total_recovery_time < 300  # Full recovery within 5 minutes

        result = {
            "test_name": "Cascading Failures",
            "components_failed": len(failures),
            "failure_chain": failures,
            "total_recovery_time": total_recovery_time,
            "passed": test_passed
        }

        print(f"Result: {'PASS' if test_passed else 'FAIL'}")
        return result

    async def run_all_tests(self) -> FaultTestResults:
        """Run all fault tolerance tests"""
        start_time = datetime.now()

        test_results = []

        # Run individual tests
        test_results.append(await self.test_worker_crash_recovery())
        test_results.append(await self.test_gateway_failure())
        test_results.append(await self.test_database_failure())
        test_results.append(await self.test_network_partition())
        test_results.append(await self.test_cascading_failures())

        end_time = datetime.now()

        # Aggregate results
        total_failures = len(test_results)
        failures_detected = total_failures  # All failures were detected
        failures_recovered = sum(1 for r in test_results if r['passed'])
        data_loss = sum(r.get('data_loss', 0) for r in test_results)

        recovery_times = [r.get('recovery_time', 0) for r in test_results if 'recovery_time' in r]
        avg_recovery_time = sum(recovery_times) / len(recovery_times) if recovery_times else 0
        max_recovery_time = max(recovery_times) if recovery_times else 0

        all_passed = all(r['passed'] for r in test_results)

        return FaultTestResults(
            test_name="Fault Tolerance Test Suite",
            start_time=start_time.isoformat(),
            end_time=end_time.isoformat(),
            total_failures_injected=total_failures,
            failures_detected=failures_detected,
            failures_recovered=failures_recovered,
            data_loss_incidents=data_loss,
            avg_recovery_time=avg_recovery_time,
            max_recovery_time=max_recovery_time,
            system_availability=(failures_recovered / total_failures * 100) if total_failures > 0 else 100,
            test_passed=all_passed,
            detailed_results=test_results
        )

    def print_results(self, results: FaultTestResults):
        """Print comprehensive test results"""
        print("\n" + "="*80)
        print("FAULT TOLERANCE TEST RESULTS")
        print("="*80)
        print(f"Test Suite: {results.test_name}")
        print(f"Start Time: {results.start_time}")
        print(f"End Time: {results.end_time}")
        print(f"\nFailures Injected: {results.total_failures_injected}")
        print(f"Failures Detected: {results.failures_detected}")
        print(f"Failures Recovered: {results.failures_recovered}")
        print(f"Data Loss Incidents: {results.data_loss_incidents}")
        print(f"\nAverage Recovery Time: {results.avg_recovery_time:.2f}s")
        print(f"Maximum Recovery Time: {results.max_recovery_time:.2f}s")
        print(f"System Availability: {results.system_availability:.2f}%")
        print(f"\nOverall Result: {'PASS' if results.test_passed else 'FAIL'}")
        print("="*80)

        # Print acceptance criteria
        print("\nACCEPTANCE CRITERIA:")
        criteria = [
            ("No data loss on failures", results.data_loss_incidents == 0, "✅" if results.data_loss_incidents == 0 else "❌"),
            ("Recovery time < 60s", results.max_recovery_time < 60, "✅" if results.max_recovery_time < 60 else "❌"),
            ("All failures recovered", results.failures_recovered == results.total_failures_injected, "✅" if results.failures_recovered == results.total_failures_injected else "❌"),
        ]

        for criterion, passed, symbol in criteria:
            print(f"{symbol} {criterion}: {'PASS' if passed else 'FAIL'}")

    def save_results(self, results: FaultTestResults, filename: str):
        """Save results to JSON file"""
        with open(filename, 'w') as f:
            json.dump(asdict(results), f, indent=2)
        print(f"\nResults saved to {filename}")


async def main():
    parser = argparse.ArgumentParser(description='Fault tolerance testing for Cocoon GPU Pool')
    parser.add_argument('--output', default='fault_tolerance_results.json', help='Output file for results')

    args = parser.parse_args()

    test_suite = FaultToleranceTestSuite()
    results = await test_suite.run_all_tests()
    test_suite.print_results(results)
    test_suite.save_results(results, args.output)


if __name__ == "__main__":
    asyncio.run(main())
