#!/usr/bin/env python3
"""
Payment System Testing Script for Cocoon GPU Pool
Tests payment processing speed and reliability with TON blockchain
"""

import asyncio
import time
import json
import statistics
import hashlib
from typing import List, Dict, Any
from dataclasses import dataclass, asdict, field
from datetime import datetime
from enum import Enum
import argparse


class PaymentStatus(Enum):
    """Payment status enumeration"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class Payment:
    """Represents a payment transaction"""
    payment_id: str
    worker_id: str
    amount: float  # in TON
    timestamp: float
    status: PaymentStatus = PaymentStatus.PENDING
    confirmation_time: float = 0.0
    blockchain_tx_hash: str = ""
    retries: int = 0


@dataclass
class PaymentTestMetrics:
    """Metrics for payment system testing"""
    test_name: str
    start_time: str
    end_time: str
    total_payments: int
    successful_payments: int
    failed_payments: int
    timeout_payments: int
    avg_processing_time: float
    p50_processing_time: float
    p95_processing_time: float
    p99_processing_time: float
    min_processing_time: float
    max_processing_time: float
    success_rate: float
    total_amount_processed: float
    payments_per_second: float
    reconciliation_accuracy: float
    double_payment_detected: int
    test_passed: bool
    detailed_payments: List[Dict[str, Any]] = field(default_factory=list)


class TONBlockchainSimulator:
    """Simulates TON blockchain for payment testing"""

    def __init__(self, avg_confirmation_time: float = 2.0, failure_rate: float = 0.01):
        self.avg_confirmation_time = avg_confirmation_time
        self.failure_rate = failure_rate
        self.transactions: Dict[str, Payment] = {}
        self.blockchain_height = 0

    async def submit_transaction(self, payment: Payment) -> str:
        """Submit transaction to blockchain"""
        # Simulate network delay
        await asyncio.sleep(0.1)

        # Simulate occasional failures
        import random
        if random.random() < self.failure_rate:
            raise Exception("Blockchain transaction failed")

        # Generate transaction hash
        tx_hash = hashlib.sha256(
            f"{payment.payment_id}{payment.worker_id}{payment.amount}".encode()
        ).hexdigest()

        self.transactions[tx_hash] = payment
        return tx_hash

    async def wait_for_confirmation(self, tx_hash: str, timeout: float = 30.0) -> bool:
        """Wait for transaction confirmation"""
        import random

        # Simulate variable confirmation time
        confirmation_time = random.gauss(self.avg_confirmation_time, 0.5)
        confirmation_time = max(0.5, min(confirmation_time, timeout))

        await asyncio.sleep(confirmation_time)

        # Simulate occasional timeout
        if random.random() < 0.05:  # 5% timeout rate
            return False

        self.blockchain_height += 1
        return True

    async def get_transaction_status(self, tx_hash: str) -> PaymentStatus:
        """Get transaction status from blockchain"""
        if tx_hash not in self.transactions:
            return PaymentStatus.FAILED

        # Simulate status check delay
        await asyncio.sleep(0.05)

        return PaymentStatus.CONFIRMED

    def get_balance(self, wallet_address: str) -> float:
        """Get wallet balance"""
        # Mock balance retrieval
        return 1000000.0  # Mock balance


class PaymentProcessor:
    """Processes payments for worker rewards"""

    def __init__(self, blockchain: TONBlockchainSimulator):
        self.blockchain = blockchain
        self.payments: List[Payment] = []
        self.payment_ledger: Dict[str, Payment] = {}
        self.processing_times: List[float] = []

    async def process_payment(self, worker_id: str, amount: float) -> Payment:
        """Process a single payment"""
        payment_id = f"pay_{len(self.payments):06d}"
        payment = Payment(
            payment_id=payment_id,
            worker_id=worker_id,
            amount=amount,
            timestamp=time.time()
        )

        start_time = time.time()

        try:
            # Submit to blockchain
            tx_hash = await self.blockchain.submit_transaction(payment)
            payment.blockchain_tx_hash = tx_hash

            # Wait for confirmation
            confirmed = await self.blockchain.wait_for_confirmation(tx_hash, timeout=30.0)

            if confirmed:
                payment.status = PaymentStatus.CONFIRMED
                payment.confirmation_time = time.time() - start_time
            else:
                payment.status = PaymentStatus.TIMEOUT

        except Exception as e:
            payment.status = PaymentStatus.FAILED
            payment.confirmation_time = time.time() - start_time

        self.payments.append(payment)
        self.payment_ledger[payment.payment_id] = payment
        self.processing_times.append(payment.confirmation_time)

        return payment

    async def batch_process_payments(self, payments_data: List[Dict[str, Any]]) -> List[Payment]:
        """Process multiple payments in batch"""
        tasks = []
        for payment_data in payments_data:
            task = self.process_payment(
                payment_data['worker_id'],
                payment_data['amount']
            )
            tasks.append(task)

        # Process in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions
        successful_payments = [r for r in results if isinstance(r, Payment)]
        return successful_payments

    def reconcile_payments(self) -> float:
        """Reconcile payments and return accuracy"""
        total_expected = sum(p.amount for p in self.payments if p.status == PaymentStatus.CONFIRMED)
        total_recorded = sum(p.amount for p in self.payment_ledger.values() if p.status == PaymentStatus.CONFIRMED)

        if total_expected == 0:
            return 100.0

        accuracy = (total_recorded / total_expected) * 100
        return accuracy

    def detect_double_payments(self) -> int:
        """Detect duplicate payments to same worker"""
        worker_payments = {}
        double_payments = 0

        for payment in self.payments:
            if payment.status == PaymentStatus.CONFIRMED:
                key = f"{payment.worker_id}_{payment.amount}_{int(payment.timestamp)}"
                if key in worker_payments:
                    double_payments += 1
                else:
                    worker_payments[key] = payment

        return double_payments


class PaymentLoadTester:
    """Load tester for payment system"""

    def __init__(self, blockchain: TONBlockchainSimulator):
        self.blockchain = blockchain
        self.processor = PaymentProcessor(blockchain)

    async def test_sequential_payments(self, num_payments: int) -> PaymentTestMetrics:
        """Test sequential payment processing"""
        print(f"\nTesting {num_payments} sequential payments...")
        start_time = datetime.now()

        for i in range(num_payments):
            worker_id = f"worker_{i % 100:03d}"
            amount = round(random.uniform(0.1, 10.0), 2)
            await self.processor.process_payment(worker_id, amount)

            if (i + 1) % 100 == 0:
                print(f"Processed {i + 1} payments")

        end_time = datetime.now()
        return self._generate_metrics("Sequential Payments", start_time, end_time)

    async def test_concurrent_payments(self, num_payments: int) -> PaymentTestMetrics:
        """Test concurrent payment processing"""
        print(f"\nTesting {num_payments} concurrent payments...")
        start_time = datetime.now()

        # Generate payment data
        import random
        payments_data = [
            {
                'worker_id': f"worker_{i % 100:03d}",
                'amount': round(random.uniform(0.1, 10.0), 2)
            }
            for i in range(num_payments)
        ]

        # Process in batches to avoid overwhelming the system
        batch_size = 50
        for i in range(0, num_payments, batch_size):
            batch = payments_data[i:i + batch_size]
            await self.processor.batch_process_payments(batch)

            if (i + batch_size) % 200 == 0:
                print(f"Processed {min(i + batch_size, num_payments)} payments")

        end_time = datetime.now()
        return self._generate_metrics("Concurrent Payments", start_time, end_time)

    async def test_high_frequency_payments(self, duration: int = 60) -> PaymentTestMetrics:
        """Test high-frequency payment processing"""
        print(f"\nTesting high-frequency payments for {duration}s...")
        start_time = datetime.now()

        end_time_target = time.time() + duration
        payment_count = 0

        while time.time() < end_time_target:
            import random
            worker_id = f"worker_{random.randint(0, 99):03d}"
            amount = round(random.uniform(0.1, 10.0), 2)
            asyncio.create_task(self.processor.process_payment(worker_id, amount))
            payment_count += 1

            # Small delay to simulate realistic payment rate
            await asyncio.sleep(0.1)

        # Wait for all payments to complete
        await asyncio.sleep(5)

        end_time = datetime.now()
        return self._generate_metrics("High-Frequency Payments", start_time, end_time)

    async def test_retry_mechanism(self, num_payments: int) -> PaymentTestMetrics:
        """Test payment retry mechanism"""
        print(f"\nTesting payment retry mechanism with {num_payments} payments...")
        start_time = datetime.now()

        import random
        for i in range(num_payments):
            worker_id = f"worker_{i % 100:03d}"
            amount = round(random.uniform(0.1, 10.0), 2)

            payment = await self.processor.process_payment(worker_id, amount)

            # Retry failed payments
            max_retries = 3
            while payment.status == PaymentStatus.FAILED and payment.retries < max_retries:
                print(f"Retrying payment {payment.payment_id} (attempt {payment.retries + 1})")
                payment.retries += 1
                payment = await self.processor.process_payment(worker_id, amount)

        end_time = datetime.now()
        return self._generate_metrics("Payment Retry", start_time, end_time)

    def _generate_metrics(self, test_name: str, start_time: datetime,
                         end_time: datetime) -> PaymentTestMetrics:
        """Generate test metrics"""
        duration = (end_time - start_time).total_seconds()

        payments = self.processor.payments
        processing_times = self.processor.processing_times

        successful = sum(1 for p in payments if p.status == PaymentStatus.CONFIRMED)
        failed = sum(1 for p in payments if p.status == PaymentStatus.FAILED)
        timeout = sum(1 for p in payments if p.status == PaymentStatus.TIMEOUT)

        processing_times_sorted = sorted(processing_times)

        reconciliation = self.processor.reconcile_payments()
        double_payments = self.processor.detect_double_payments()

        # Calculate success rate
        total = len(payments)
        success_rate = (successful / total * 100) if total > 0 else 0

        # Check acceptance criteria
        test_passed = (
            success_rate > 99.9 and
            (statistics.mean(processing_times) < 5.0 if processing_times else False) and
            reconciliation == 100.0 and
            double_payments == 0
        )

        return PaymentTestMetrics(
            test_name=test_name,
            start_time=start_time.isoformat(),
            end_time=end_time.isoformat(),
            total_payments=total,
            successful_payments=successful,
            failed_payments=failed,
            timeout_payments=timeout,
            avg_processing_time=statistics.mean(processing_times) if processing_times else 0,
            p50_processing_time=self._percentile(processing_times_sorted, 50),
            p95_processing_time=self._percentile(processing_times_sorted, 95),
            p99_processing_time=self._percentile(processing_times_sorted, 99),
            min_processing_time=min(processing_times) if processing_times else 0,
            max_processing_time=max(processing_times) if processing_times else 0,
            success_rate=success_rate,
            total_amount_processed=sum(p.amount for p in payments if p.status == PaymentStatus.CONFIRMED),
            payments_per_second=total / duration if duration > 0 else 0,
            reconciliation_accuracy=reconciliation,
            double_payment_detected=double_payments,
            test_passed=test_passed
        )

    @staticmethod
    def _percentile(data: List[float], percentile: int) -> float:
        """Calculate percentile"""
        if not data:
            return 0.0
        index = int(len(data) * percentile / 100)
        return data[min(index, len(data) - 1)]

    def print_results(self, metrics: PaymentTestMetrics):
        """Print test results"""
        print("\n" + "="*80)
        print("PAYMENT SYSTEM TEST RESULTS")
        print("="*80)
        print(f"Test: {metrics.test_name}")
        print(f"Start Time: {metrics.start_time}")
        print(f"End Time: {metrics.end_time}")
        print(f"\nTotal Payments: {metrics.total_payments}")
        print(f"Successful: {metrics.successful_payments}")
        print(f"Failed: {metrics.failed_payments}")
        print(f"Timeout: {metrics.timeout_payments}")
        print(f"Success Rate: {metrics.success_rate:.2f}%")
        print(f"\nProcessing Time:")
        print(f"  Average: {metrics.avg_processing_time:.2f}s")
        print(f"  P50: {metrics.p50_processing_time:.2f}s")
        print(f"  P95: {metrics.p95_processing_time:.2f}s")
        print(f"  P99: {metrics.p99_processing_time:.2f}s")
        print(f"  Min: {metrics.min_processing_time:.2f}s")
        print(f"  Max: {metrics.max_processing_time:.2f}s")
        print(f"\nThroughput: {metrics.payments_per_second:.2f} payments/s")
        print(f"Total Amount: {metrics.total_amount_processed:.2f} TON")
        print(f"Reconciliation Accuracy: {metrics.reconciliation_accuracy:.2f}%")
        print(f"Double Payments Detected: {metrics.double_payment_detected}")
        print(f"\nTest Result: {'PASS' if metrics.test_passed else 'FAIL'}")
        print("="*80)

        # Acceptance criteria
        print("\nACCEPTANCE CRITERIA:")
        criteria = [
            ("Success rate > 99.9%", metrics.success_rate > 99.9,
             "✅" if metrics.success_rate > 99.9 else "❌"),
            ("Average processing < 5s", metrics.avg_processing_time < 5.0,
             "✅" if metrics.avg_processing_time < 5.0 else "❌"),
            ("100% reconciliation", metrics.reconciliation_accuracy == 100.0,
             "✅" if metrics.reconciliation_accuracy == 100.0 else "❌"),
            ("No double payments", metrics.double_payment_detected == 0,
             "✅" if metrics.double_payment_detected == 0 else "❌"),
        ]

        for criterion, passed, symbol in criteria:
            print(f"{symbol} {criterion}: {'PASS' if passed else 'FAIL'}")

    def save_results(self, metrics: PaymentTestMetrics, filename: str):
        """Save results to JSON"""
        with open(filename, 'w') as f:
            json.dump(asdict(metrics), f, indent=2)
        print(f"\nResults saved to {filename}")


async def main():
    parser = argparse.ArgumentParser(description='Payment system testing for Cocoon GPU Pool')
    parser.add_argument('--payments', type=int, default=1000, help='Number of payments to test')
    parser.add_argument('--test-type', choices=['sequential', 'concurrent', 'highfreq', 'retry', 'all'],
                       default='all', help='Type of test to run')
    parser.add_argument('--confirmation-time', type=float, default=2.0,
                       help='Average blockchain confirmation time (seconds)')
    parser.add_argument('--failure-rate', type=float, default=0.01,
                       help='Blockchain failure rate (0.0-1.0)')
    parser.add_argument('--output', default='payment_test_results.json', help='Output file')

    args = parser.parse_args()

    # Initialize blockchain simulator
    blockchain = TONBlockchainSimulator(
        avg_confirmation_time=args.confirmation_time,
        failure_rate=args.failure_rate
    )

    tester = PaymentLoadTester(blockchain)

    if args.test_type == 'all':
        # Run all tests
        tests = [
            ('sequential', lambda: tester.test_sequential_payments(args.payments)),
            ('concurrent', lambda: tester.test_concurrent_payments(args.payments)),
            ('highfreq', lambda: tester.test_high_frequency_payments(60)),
            ('retry', lambda: tester.test_retry_mechanism(100)),
        ]

        all_results = []
        for test_name, test_func in tests:
            # Reset processor for each test
            tester.processor = PaymentProcessor(blockchain)

            print(f"\n{'='*80}")
            print(f"Running {test_name.upper()} test")
            print(f"{'='*80}")

            metrics = await test_func()
            tester.print_results(metrics)
            tester.save_results(metrics, f"payment_{test_name}_results.json")
            all_results.append((test_name, metrics))

        # Print summary
        print(f"\n{'='*80}")
        print("TEST SUMMARY")
        print(f"{'='*80}")
        for test_name, metrics in all_results:
            status = "PASS" if metrics.test_passed else "FAIL"
            print(f"{test_name:<15} {status:<6} Success: {metrics.success_rate:.1f}% "
                  f"Avg Time: {metrics.avg_processing_time:.2f}s")

    else:
        test_map = {
            'sequential': lambda: tester.test_sequential_payments(args.payments),
            'concurrent': lambda: tester.test_concurrent_payments(args.payments),
            'highfreq': lambda: tester.test_high_frequency_payments(60),
            'retry': lambda: tester.test_retry_mechanism(args.payments),
        }

        metrics = await test_map[args.test_type]()
        tester.print_results(metrics)
        tester.save_results(metrics, args.output)


if __name__ == "__main__":
    import random
    asyncio.run(main())
