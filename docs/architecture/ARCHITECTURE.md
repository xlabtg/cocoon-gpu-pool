# GPU Resource Pool Architecture for Cocoon Network

## Executive Summary

This document presents a comprehensive architecture for a decentralized GPU resource pool that enables small GPU owners to aggregate their computing power and participate in the Cocoon network. The system combines blockchain-based smart contracts on TON, backend infrastructure for workload management, and ML-driven optimization components.

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Components](#architecture-components)
3. [Component Interactions](#component-interactions)
4. [Data Flow](#data-flow)
5. [Security Considerations](#security-considerations)
6. [Scalability Design](#scalability-design)
7. [Integration Points](#integration-points)

## System Overview

### Objectives

The GPU Resource Pool architecture aims to:

- **Aggregate Resources**: Enable multiple small GPU owners to pool computing power
- **Fair Distribution**: Ensure proportional reward distribution based on contribution
- **High Availability**: Maintain service continuity through redundancy and failover
- **Transparency**: Provide verifiable on-chain tracking of contributions and rewards
- **Optimization**: Maximize profitability through intelligent workload distribution

### Key Stakeholders

1. **Pool Operators**: Entities managing the GPU pool infrastructure
2. **GPU Contributors**: Individual GPU owners contributing resources
3. **Cocoon Network**: The underlying AI inference network
4. **End Users**: Applications and users consuming AI inference services

## Architecture Components

### Layer 1: Blockchain Layer (TON Smart Contracts)

#### 1.1 PoolOperator Contract

**Purpose**: Central registry and governance contract for the GPU pool

**Responsibilities**:
- Pool registration with Cocoon network
- Pool metadata management (name, operator address, fee structure)
- Participant registry reference management
- Emergency shutdown capabilities
- Parameter updates (fees, minimum stake, etc.)

**State Variables**:
```func
- pool_id: int              // Unique pool identifier
- operator_address: slice   // Pool operator wallet
- cocoon_root: slice        // Reference to Cocoon root contract
- pool_state: int           // Active, Paused, Closed
- participant_registry: slice
- reward_distribution: slice
- pool_fee_bps: int         // Pool operator fee in basis points
- min_participant_stake: int
- total_pooled_resources: int
- version: int
```

**Key Operations**:
- `register_pool()`: Register pool with Cocoon network
- `add_participant(address, gpu_spec)`: Register new pool participant
- `remove_participant(address)`: Remove participant from pool
- `update_pool_params(params)`: Update pool configuration
- `emergency_shutdown()`: Pause pool operations
- `withdraw_fees()`: Operator fee withdrawal

#### 1.2 RewardDistribution Contract

**Purpose**: Automated distribution of TON rewards to pool participants

**Responsibilities**:
- Receive payments from Cocoon proxies
- Calculate proportional distributions based on contribution
- Execute reward payouts to participants
- Maintain distribution history
- Handle unclaimed rewards

**State Variables**:
```func
- pool_operator: slice      // Reference to PoolOperator contract
- participant_registry: slice
- total_rewards_received: int
- total_rewards_distributed: int
- distribution_period: int  // Epoch duration
- current_epoch: int
- pending_distributions: cell  // Queue of pending payouts
- distribution_history: cell   // Historical distribution records
```

**Key Operations**:
- `receive_rewards()`: Accept incoming payments from Cocoon network
- `calculate_distribution(epoch)`: Compute reward shares per participant
- `distribute_rewards(epoch)`: Execute payout transactions
- `claim_rewards(participant)`: Allow participants to claim rewards
- `query_participant_rewards(address)`: Get pending rewards for address

**Distribution Algorithm**:
```
participant_share = (participant_contribution / total_pool_contribution) * epoch_rewards
operator_fee = epoch_rewards * pool_fee_bps / 10000
net_participant_share = participant_share * (1 - pool_fee_bps / 10000)
```

#### 1.3 ParticipantRegistry Contract

**Purpose**: Track individual participant contributions and status

**Responsibilities**:
- Maintain participant metadata (GPU specs, stake, status)
- Track contribution metrics (uptime, tasks completed, tokens processed)
- Handle participant stake deposits and withdrawals
- Manage reputation scores
- Enforce minimum stake requirements

**State Variables**:
```func
- pool_operator: slice
- participants: cell        // Dict: address -> ParticipantInfo
- participant_count: int
- total_stake: int
```

**ParticipantInfo Structure**:
```func
{
  owner_address: slice
  worker_address: slice     // Cocoon worker contract address
  gpu_model: int            // Hash of GPU specification
  gpu_count: int
  stake_amount: int
  join_timestamp: int
  status: int               // Active, Inactive, Suspended
  contribution_score: int   // Weighted contribution metric
  total_uptime: int         // Seconds of active operation
  total_tasks: int          // Tasks completed
  total_tokens: int         // Tokens processed
  reputation_score: int     // Performance metric (0-1000)
  last_heartbeat: int
}
```

**Key Operations**:
- `register_participant(owner, gpu_spec, stake)`: Add new participant
- `update_contribution(address, tasks, tokens, uptime)`: Record contribution
- `deposit_stake(participant)`: Increase stake
- `withdraw_stake(participant, amount)`: Decrease stake (with timelock)
- `update_reputation(address, score)`: Update performance score
- `get_participant_info(address)`: Query participant data
- `slash_participant(address, amount, reason)`: Penalty for misconduct

### Layer 2: Backend Infrastructure

#### 2.1 Pool Gateway

**Purpose**: Aggregation point for multiple Cocoon worker instances

**Architecture**:
```
┌─────────────────────────────────────────┐
│          Pool Gateway                   │
│  ┌───────────────────────────────────┐  │
│  │  Load Balancer                    │  │
│  │  - Round Robin                    │  │
│  │  - Weighted Distribution          │  │
│  │  - Health-based Routing           │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │  Request Router                   │  │
│  │  - Model-based routing            │  │
│  │  - GPU capability matching        │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │  Aggregation Manager              │  │
│  │  - Worker pool management         │  │
│  │  - Attestation verification       │  │
│  │  - Session management             │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
         │              │              │
         ▼              ▼              ▼
    Worker-1       Worker-2       Worker-N
```

**Components**:

**2.1.1 Load Balancer**
- Distributes incoming inference requests across healthy workers
- Supports multiple strategies:
  - Round-robin for uniform distribution
  - Weighted routing based on GPU capability
  - Least-connections for optimal utilization
  - Resource-based (GPU memory, compute availability)
- Implements health checks (HTTP/gRPC probes every 10s)
- Circuit breaker pattern for fault isolation

**2.1.2 Request Router**
- Routes requests to appropriate workers based on:
  - Required AI model (matches worker capabilities)
  - GPU memory requirements
  - Compute complexity estimates
  - Geographic proximity (latency optimization)
- Maintains routing table of worker capabilities
- Supports sticky sessions for multi-turn conversations

**2.1.3 Aggregation Manager**
- Manages pool of Cocoon worker instances
- Performs attestation verification using RA-TLS
- Maintains worker registry and status
- Handles worker registration/deregistration
- Monitors worker health and performance metrics
- Implements graceful shutdown procedures

**Technical Stack**:
- Language: Go/Rust (high performance, concurrency)
- Framework: gRPC for inter-service communication
- Storage: Redis for session state, PostgreSQL for metadata
- Monitoring: Prometheus metrics, Grafana dashboards

#### 2.2 Worker Manager

**Purpose**: Manages lifecycle of Cocoon worker instances

**Responsibilities**:
- Automated worker deployment and configuration
- Docker/containerd orchestration for worker containers
- Health monitoring and automatic restart
- Resource allocation and limits
- Log aggregation and analysis
- Worker version management and updates

**Architecture**:
```
┌──────────────────────────────────────────────┐
│         Worker Manager                       │
│                                              │
│  ┌────────────────────────────────────────┐  │
│  │  Deployment Orchestrator               │  │
│  │  - Worker template management          │  │
│  │  - Configuration generation            │  │
│  │  - Automated deployment                │  │
│  └────────────────────────────────────────┘  │
│                                              │
│  ┌────────────────────────────────────────┐  │
│  │  Health Monitor                        │  │
│  │  - Heartbeat tracking                  │  │
│  │  - Performance metrics collection      │  │
│  │  - Anomaly detection                   │  │
│  └────────────────────────────────────────┘  │
│                                              │
│  ┌────────────────────────────────────────┐  │
│  │  Recovery Manager                      │  │
│  │  - Automatic restart on failure        │  │
│  │  - Failover coordination               │  │
│  │  - State recovery                      │  │
│  └────────────────────────────────────────┘  │
└──────────────────────────────────────────────┘
```

**Worker Deployment Process**:
1. Fetch official worker distribution from ci.cocoon.org
2. Verify SHA256 checksum against expected hash
3. Extract and configure worker with pool credentials
4. Set worker coefficient and payment address
5. Initialize TEE/TDX environment
6. Register worker with Pool Gateway
7. Start worker process and monitor

**Configuration Template**:
```yaml
worker:
  pool_id: <pool_identifier>
  proxy_address: <cocoon_proxy_address>
  worker_coefficient: 1000  # 1.0x pricing
  payment_wallet: <pool_reward_contract>
  gpu_devices: [0, 1, 2, 3]  # GPU indices

resources:
  memory_limit: 48GB
  cpu_limit: 16

monitoring:
  metrics_port: 9090
  health_check_interval: 10s
  heartbeat_interval: 30s

security:
  tee_enabled: true
  attestation_required: true
  sealed_keys_path: /var/lib/cocoon/keys
```

#### 2.3 Contribution Tracker

**Purpose**: Monitor and record participant contributions for reward distribution

**Responsibilities**:
- Track task completions per worker
- Monitor token processing counts
- Calculate uptime and availability
- Aggregate metrics per participant
- Submit contribution updates to ParticipantRegistry contract
- Detect and report anomalies

**Data Collection**:
- Task completion events from workers
- Token count from inference responses
- Heartbeat timestamps for uptime calculation
- Resource utilization metrics
- Error rates and quality metrics

**Metrics Aggregation**:
```python
contribution_score = (
    w1 * normalized_tokens_processed +
    w2 * normalized_uptime_percentage +
    w3 * normalized_task_count +
    w4 * quality_score
)

# Default weights
w1 = 0.5  # Tokens processed (primary metric)
w2 = 0.2  # Uptime reliability
w3 = 0.2  # Task completion count
w4 = 0.1  # Quality score
```

**Submission Schedule**:
- Real-time task completion logging
- Hourly contribution summaries
- Daily on-chain submission to ParticipantRegistry
- Epoch-based (weekly) finalization for reward distribution

#### 2.4 Blockchain Interface

**Purpose**: Manage all interactions with TON blockchain smart contracts

**Responsibilities**:
- Transaction submission (contributions, rewards, registrations)
- Event listening (reward distributions, parameter changes)
- Gas management and optimization
- Transaction retry and error handling
- State synchronization

**Components**:

**2.4.1 Transaction Manager**
- Queues blockchain transactions
- Batches multiple operations for gas efficiency
- Handles nonce management
- Implements retry logic with exponential backoff
- Monitors transaction status

**2.4.2 Event Listener**
- Subscribes to smart contract events
- Processes reward distribution events
- Handles pool parameter updates
- Triggers appropriate backend actions

**2.4.3 State Synchronizer**
- Maintains local cache of blockchain state
- Periodically syncs with contracts
- Resolves discrepancies
- Provides fast read access to contract data

**Technology**:
- TON SDK integration
- WebSocket connection to TON node
- SQLite/PostgreSQL for local state cache

### Layer 3: ML Optimization Components

#### 3.1 Profitability Forecasting Engine

**Purpose**: Predict potential earnings for different AI models and optimize model selection

**Approach**: Time-series forecasting using historical data

**Input Features**:
- Historical request volume per model
- Average token count per request
- Price per token trends
- Worker coefficient settings
- Network-wide demand patterns
- Time-of-day patterns
- Day-of-week seasonality

**Model Architecture**:
```
Time-Series Forecasting Model (LSTM/Transformer)
├── Input: Historical metrics (last 30 days)
├── Features: Request volume, token counts, prices
├── Output: Forecasted demand and revenue (next 7 days)
└── Update Frequency: Daily retraining
```

**Forecasting Models**:
- **Short-term (1-24 hours)**: ARIMA or Prophet for hourly predictions
- **Medium-term (1-7 days)**: LSTM networks for daily predictions
- **Long-term (1-4 weeks)**: Transformer models for trend analysis

**Revenue Estimation**:
```python
estimated_revenue = (
    forecasted_request_volume *
    avg_tokens_per_request *
    price_per_token *
    pool_share *
    (1 - pool_fee_percentage)
)

profit_margin = estimated_revenue - operational_costs
```

**Recommendations Output**:
- Top 5 most profitable models to prioritize
- Optimal worker coefficient adjustments
- Suggested GPU allocation strategy
- Expected ROI per model

#### 3.2 Task Distribution Optimizer

**Purpose**: Intelligently distribute inference tasks to maximize throughput and minimize latency

**Optimization Objectives**:
1. **Minimize latency**: Route to geographically close, low-load workers
2. **Maximize throughput**: Balance load across all workers
3. **Optimize costs**: Use most cost-efficient workers for each task
4. **Maximize revenue**: Prioritize high-value tasks

**Algorithms**:

**3.2.1 Multi-Objective Optimization**
```python
# Objective function
score(worker, task) = (
    w_latency * latency_score(worker, task) +
    w_load * load_balance_score(worker) +
    w_capability * capability_match_score(worker, task) +
    w_cost * cost_efficiency_score(worker)
)

# Constraints
- worker.available_memory >= task.memory_requirement
- worker.supports_model(task.model)
- worker.status == HEALTHY
```

**3.2.2 Reinforcement Learning Agent**
- **State**: Current worker loads, queue sizes, recent latencies
- **Action**: Select worker for incoming task
- **Reward**: Combination of task completion time, user satisfaction, revenue
- **Algorithm**: PPO (Proximal Policy Optimization) or DQN

**Training**:
- Offline training on historical data
- Online learning with real-time feedback
- A/B testing for policy evaluation
- Regular model updates (weekly)

**3.2.3 Queuing Theory Model**
- M/M/c queue model for each worker
- Calculate optimal queue sizes
- Predict wait times
- Trigger worker scaling decisions

#### 3.3 Adaptive Load Manager

**Purpose**: Dynamically adjust resource allocation based on network conditions

**Responsibilities**:
- Monitor Cocoon network load and demand
- Detect demand spikes and patterns
- Trigger worker scaling (horizontal/vertical)
- Adjust worker coefficients dynamically
- Implement surge pricing during high demand

**Adaptive Strategies**:

**3.3.1 Auto-Scaling**
```python
if avg_queue_length > SCALE_UP_THRESHOLD:
    if available_idle_gpus > 0:
        deploy_additional_worker()
elif avg_queue_length < SCALE_DOWN_THRESHOLD:
    if worker_count > MIN_WORKERS:
        gracefully_shutdown_worker()
```

**3.3.2 Dynamic Pricing**
```python
# Adjust worker_coefficient based on demand
if network_demand > HIGH_THRESHOLD:
    worker_coefficient *= 1.2  # Increase price 20%
elif network_demand < LOW_THRESHOLD:
    worker_coefficient *= 0.9  # Decrease price 10%

worker_coefficient = max(MIN_COEF, min(MAX_COEF, worker_coefficient))
```

**3.3.3 Resource Prioritization**
- Prioritize high-margin models during congestion
- Implement request queuing with priority levels
- Reserve capacity for premium customers
- Shed low-value load when necessary

**Monitoring Metrics**:
- Average response time per model
- Queue depth per worker
- GPU utilization percentage
- Request rejection rate
- Revenue per GPU-hour

## Component Interactions

### Participant Onboarding Flow

```
Participant → PoolOperator.add_participant()
                    ↓
          ParticipantRegistry.register()
                    ↓
          Stake TON → ParticipantRegistry
                    ↓
          Worker Manager deploys Cocoon worker
                    ↓
          Worker registers with Pool Gateway
                    ↓
          Contribution Tracker starts monitoring
                    ↓
          Participant marked ACTIVE
```

### Request Handling Flow

```
Cocoon Client → Pool Gateway (acting as Proxy)
                    ↓
          Request Router analyzes request
                    ↓
          ML Optimizer selects optimal worker
                    ↓
          Load Balancer routes to selected worker
                    ↓
          Worker processes in TEE
                    ↓
          Response returned to client
                    ↓
          Payment flows to Pool Gateway
                    ↓
          RewardDistribution contract receives funds
```

### Reward Distribution Flow

```
Epoch End Trigger (weekly)
          ↓
ContributionTracker.finalize_epoch()
          ↓
Submit final contributions → ParticipantRegistry
          ↓
RewardDistribution.calculate_distribution()
          ↓
For each participant:
    Calculate share based on contribution_score
          ↓
Execute TON transfers to participant wallets
          ↓
Record distribution on-chain
          ↓
Emit distribution events
```

### Worker Health Monitoring Flow

```
Worker sends heartbeat → Pool Gateway (every 30s)
          ↓
Health Monitor checks:
    - Response time
    - Error rate
    - Resource usage
          ↓
If unhealthy:
    Mark worker DEGRADED
    Reduce traffic allocation
    Alert Worker Manager
          ↓
Worker Manager:
    Attempt restart
    If fails → mark INACTIVE
    Update ParticipantRegistry
          ↓
If recovered:
    Gradual traffic ramp-up
    Mark ACTIVE when stable
```

## Data Flow

### Real-time Data Flows

1. **Inference Requests**
   - Client → Pool Gateway → Worker → Client
   - Latency target: <500ms end-to-end

2. **Heartbeats**
   - Workers → Pool Gateway → Health Monitor
   - Frequency: Every 30 seconds

3. **Metrics**
   - Workers → Contribution Tracker → Metrics DB
   - Real-time streaming

### Batch Data Flows

1. **Contribution Updates**
   - Contribution Tracker → ParticipantRegistry (daily)
   - Batch submission for gas efficiency

2. **Reward Distributions**
   - RewardDistribution → Participants (weekly epochs)
   - Merkle tree for efficient multi-send

3. **ML Model Updates**
   - Training Pipeline → ML Models (weekly)
   - A/B testing before production deployment

## Security Considerations

### Smart Contract Security

1. **Access Control**
   - Role-based permissions (Operator, Participant, Admin)
   - Multi-signature for critical operations
   - Timelock for parameter changes

2. **Economic Security**
   - Minimum stake requirements prevent Sybil attacks
   - Slashing for malicious behavior
   - Fee limits to prevent exploitation

3. **Upgrade Safety**
   - Proxy pattern for upgradeable contracts
   - Governance voting for major changes
   - Emergency pause functionality

### Backend Security

1. **Authentication & Authorization**
   - JWT tokens for API authentication
   - mTLS for inter-service communication
   - TON wallet signature verification

2. **Data Protection**
   - Encryption at rest (AES-256)
   - Encryption in transit (TLS 1.3)
   - Secure key management (HSM or KMS)

3. **TEE Integration**
   - Mandatory attestation verification
   - RA-TLS for worker communication
   - Regular attestation refresh

### Network Security

1. **DDoS Protection**
   - Rate limiting at gateway
   - Request queuing with backpressure
   - Geographic distribution

2. **Isolation**
   - Network segmentation
   - Worker sandboxing
   - Resource quotas

## Scalability Design

### Horizontal Scalability

1. **Pool Gateway**
   - Stateless design allows multiple instances
   - Load balancer distributes across gateways
   - Shared Redis for session state

2. **Worker Pool**
   - Linear scaling with GPU additions
   - No centralization bottlenecks
   - Automatic worker discovery

3. **Smart Contracts**
   - Sharding-ready design
   - Off-chain computation with on-chain verification
   - Merkle proofs for batch operations

### Vertical Scalability

1. **Database Optimization**
   - Read replicas for queries
   - Write batching for efficiency
   - Indexing on high-query columns

2. **Caching Strategy**
   - Redis for hot data
   - CDN for static content
   - Query result caching

### Performance Targets

| Metric | Target | Rationale |
|--------|--------|-----------|
| Request Latency (p95) | <500ms | Competitive with centralized services |
| Throughput | 1000+ req/s per pool | Support medium-scale applications |
| Worker Registration | <30s | Quick onboarding |
| Reward Distribution | <5 min | Fast payout completion |
| Uptime | 99.9% | Enterprise-grade reliability |
| Gateway Failover | <10s | Minimal disruption |

## Integration Points

### Cocoon Network Integration

1. **Contract References**
   - PoolOperator references CocoonRoot for network parameters
   - Workers reference CocoonProxy for payment contracts
   - Attestation verification uses Cocoon's root of trust

2. **Worker Distribution**
   - Fetch official builds from ci.cocoon.org
   - Verify checksums against CocoonRoot contract
   - Use standard worker configuration

3. **Payment Flow**
   - Pool acts as a single proxy entity
   - Receives payments to RewardDistribution contract
   - Distributes internally to participants

### External Integrations

1. **Monitoring & Observability**
   - Prometheus for metrics collection
   - Grafana for visualization
   - ELK stack for log aggregation
   - Alerting via PagerDuty/Slack

2. **Infrastructure**
   - Kubernetes for orchestration
   - Terraform for IaC
   - Ansible for configuration management

3. **Analytics**
   - BigQuery/Snowflake for data warehouse
   - dbt for transformation pipelines
   - Jupyter for analysis

## Next Steps

This architecture document provides the foundation for implementation. Related documentation:

- [Smart Contract Specifications](../contracts/CONTRACTS.md)
- [API Specification](../api/API_SPEC.md)
- [Deployment Guide](../deployment/DEPLOYMENT.md)
- [Economic Model](../economics/ECONOMIC_MODEL.md)
- [Migration Plan](../MIGRATION_PLAN.md)
