# Economic Model for GPU Resource Pool

## Overview

This document outlines the economic model for TON distribution in the GPU resource pool, including revenue streams, cost structures, reward distribution mechanisms, and incentive alignment strategies.

## Table of Contents

1. [Revenue Streams](#revenue-streams)
2. [Cost Structure](#cost-structure)
3. [Reward Distribution Model](#reward-distribution-model)
4. [Fee Structure](#fee-structure)
5. [Stake Requirements](#stake-requirements)
6. [Incentive Mechanisms](#incentive-mechanisms)
7. [Economic Security](#economic-security)
8. [Financial Projections](#financial-projections)

## Revenue Streams

### Primary Revenue: Inference Payments

The pool earns TON from processing AI inference requests on the Cocoon network.

**Payment Formula:**
```
payment_per_request = tokens_used × price_per_token
```

**Cocoon Network Pricing (as of design):**
- Base price per token: ~0.001 TON (varies by model and market)
- Worker receives: `tokens × worker_fee_per_token`
- Proxy receives: `tokens × (price_per_token - worker_fee_per_token)`

**Pool Implementation:**
- Pool acts as a single proxy entity
- Receives payments at pool-level
- Internal distribution to participants based on contribution

**Revenue Components:**

1. **Worker Fee Revenue**
   ```
   worker_revenue = tokens_processed × worker_fee_per_token
   ```
   - Default `worker_fee_per_token`: 0.0006 TON
   - Pool receives this for processing work

2. **Proxy Commission** (if pool operates proxy)
   ```
   proxy_revenue = tokens_processed × (price_per_token - worker_fee_per_token)
   ```
   - Default commission: ~0.0004 TON per token
   - Additional revenue stream if pool operates its own proxy

### Secondary Revenue: Staking Rewards

Pooled stake can be deployed in TON staking mechanisms.

**Staking Yield:**
- Current TON staking APY: ~3-5%
- Applied to pooled stake (e.g., 2,300 TON)
- Annual return: 69-115 TON

**Distribution:**
- 70% to participants (proportional to stake)
- 30% to pool operator (for infrastructure costs)

## Cost Structure

### Infrastructure Costs

**Pool Gateway & Backend Services:**
- Server hosting: $500-1,000/month
- Load balancers: $100/month
- Database (PostgreSQL, Redis): $200/month
- Monitoring & logging: $100/month
- **Total Backend**: ~$1,000/month = ~250 TON/month (@ $4/TON)

**Blockchain Operations:**
- On-chain contribution updates (daily): 23 participants × 0.01 TON = 0.23 TON/day = ~7 TON/month
- Reward distributions (weekly): 23 participants × 0.005 TON = 0.115 TON/week = ~0.5 TON/month
- Contract management: ~2 TON/month
- **Total Blockchain**: ~10 TON/month

**ML Infrastructure:**
- Training pipeline: $200/month = ~50 TON/month
- Model serving: $100/month = ~25 TON/month
- **Total ML**: ~75 TON/month

**Participant Infrastructure (borne by participants):**
- GPU hardware (amortized): Participant's cost
- Electricity: ~$0.50-1.00/kWh × 24h × 30 days × GPU_power
  - H100 (700W): ~$250-500/month per GPU
- Internet: $50-100/month
- Colocation (optional): $500-2,000/month

**Total Pool Operational Cost:**
- Fixed costs: ~335 TON/month
- Variable costs (as % of revenue): ~5% (support, scaling)

### Break-Even Analysis

**Monthly Revenue Required:**
```
break_even_revenue = fixed_costs / (1 - variable_cost_percentage)
                  = 335 / 0.95
                  = ~353 TON/month
```

**Tokens Needed (at 0.0006 TON per token):**
```
tokens_required = 353 / 0.0006
                = ~588,000 tokens/month
                = ~19,600 tokens/day
```

**Requests Needed (assuming 300 tokens/request):**
```
requests_required = 19,600 / 300
                  = ~65 requests/day
```

**This is easily achievable for a small pool**, making the model economically viable.

## Reward Distribution Model

### Distribution Formula

Rewards are distributed based on weighted contribution scores.

**Epoch Reward Calculation:**

```python
# For each participant in epoch
participant_share = (
    participant_contribution_score /
    total_contribution_score
) × epoch_total_rewards × (1 - pool_fee_percentage)

# Contribution score components (weighted)
contribution_score = (
    0.50 × tokens_processed +
    0.20 × uptime_percentage × max_possible_tokens +
    0.20 × tasks_completed × avg_tokens_per_task +
    0.10 × quality_score × avg_contribution
) × reputation_multiplier
```

**Reputation Multiplier:**
- New participants (< 1 month): 0.8x
- Established participants (1-3 months): 1.0x
- Veteran participants (> 3 months, high uptime): 1.1x
- Top performers (top 10%, consistent quality): 1.2x

**Quality Score Factors:**
- Error rate (lower is better)
- Average latency (lower is better)
- Attestation verification success rate

### Distribution Example

**Scenario:**
- Epoch duration: 7 days
- Total epoch revenue: 100 TON
- Pool fee: 5% (5 TON to operator)
- Distributable: 95 TON
- Participants: 3 (Alice, Bob, Carol)

**Contributions:**

| Participant | Tokens | Uptime % | Tasks | Quality | Reputation | Score |
|-------------|--------|----------|-------|---------|------------|-------|
| Alice | 500K | 99% | 1,500 | 950 | 1.1x | 52,250 |
| Bob | 300K | 95% | 900 | 900 | 1.0x | 29,700 |
| Carol | 200K | 98% | 600 | 920 | 1.0x | 19,840 |
| **Total** | 1M | - | 3,000 | - | - | 101,790 |

**Reward Calculation:**
```
Alice:  (52,250 / 101,790) × 95 = 48.74 TON
Bob:    (29,700 / 101,790) × 95 = 27.70 TON
Carol:  (19,840 / 101,790) × 95 = 18.52 TON
```

**Verification:** 48.74 + 27.70 + 18.52 = 94.96 TON ≈ 95 TON ✓

### Distribution Timeline

**Weekly Epoch Cycle:**

```
Day 0 (Monday):     Epoch N starts
Day 6 (Sunday):     Epoch N ends, backend finalizes contributions
Day 7 (Monday):     Epoch N+1 starts, Epoch N distribution calculated
Day 7 (Monday):     Rewards distributed to participants
```

**Distribution Methods:**

1. **Automatic Distribution** (default):
   - Smart contract distributes to all participants automatically
   - Gas cost ~0.005 TON per participant
   - Funded from pool operator fees

2. **Claim-based Distribution** (optional):
   - Participants claim rewards manually
   - Merkle proof verification
   - Participant pays gas (~0.002 TON)

## Fee Structure

### Pool Operator Fee

**Default: 5% of all rewards**

**Justification:**
- Covers infrastructure costs (~335 TON/month)
- Provides operator incentive
- Competitive with other pooling services

**Example Revenue (1,000 TON/month pool revenue):**
```
operator_fee = 1,000 × 0.05 = 50 TON/month
participant_rewards = 1,000 × 0.95 = 950 TON/month
```

**Fee Range:**
- Minimum recommended: 3% (covers basic costs)
- Maximum reasonable: 10% (market competitive)
- Adjustable by governance (future)

### Transaction Fees

**On-chain Operations:**

| Operation | Estimated Fee | Payer |
|-----------|---------------|-------|
| Participant registration | 0.02 TON | Participant |
| Stake deposit | 0.01 TON | Participant |
| Stake withdrawal request | 0.01 TON | Participant |
| Stake withdrawal completion | 0.01 TON | Participant |
| Reward claim (manual) | 0.002 TON | Participant |
| Contribution update | 0.01 TON | Pool operator |
| Reward distribution | 0.005 TON/participant | Pool operator |

**Gas Optimization Strategies:**
- Batch contribution updates (daily vs. per-task)
- Off-chain calculation, on-chain verification (Merkle proofs)
- Reward distribution batching
- Efficient data structures (dictionaries vs. arrays)

## Stake Requirements

### Minimum Stake

**Default: 100 TON per participant**

**Rationale:**
1. **Sybil Resistance**: Prevents spam registrations
2. **Skin in the Game**: Ensures commitment
3. **Slashing Pool**: Enables penalties for misconduct
4. **Economic Alignment**: Participants care about pool success

**Stake Scaling:**

| GPU Tier | Minimum Stake | Rationale |
|----------|---------------|-----------|
| Entry (1-2 GPUs) | 100 TON | Base requirement |
| Medium (3-4 GPUs) | 200 TON | Higher capacity |
| Large (5-8 GPUs) | 400 TON | Significant contributor |
| Enterprise (9+ GPUs) | 800 TON | Major participant |

### Stake Utilization

**Security Reserve (80%):**
- Locked for security and slashing
- Cannot be utilized for staking yield
- Ensures ability to penalize misconduct

**Staking Pool (20%):**
- Deployed in TON staking
- Generates passive yield
- Distributed to participants

**Example (100 TON stake):**
```
security_reserve = 80 TON (locked)
staking_pool = 20 TON (earning 4% APY)

annual_staking_return = 20 × 0.04 = 0.8 TON
participant_share (70%) = 0.56 TON
operator_share (30%) = 0.24 TON
```

### Withdrawal Mechanics

**Timelock: 7 days**

**Process:**
1. Participant requests withdrawal
2. Worker marked as "withdrawing"
3. 7-day timelock begins
4. During timelock:
   - Participant can cancel
   - Pool can slash if misconduct detected
5. After timelock:
   - Participant completes withdrawal
   - Receives stake (minus any slashing)

**Rationale for 7-day timelock:**
- Allows pool to detect and respond to misconduct
- Discourages rapid entry/exit (wash trading)
- Standard in DeFi protocols
- Balances security and liquidity

## Incentive Mechanisms

### Performance-Based Rewards

**Quality Score Incentives:**

High-quality participants earn bonus multipliers:

```
quality_bonus = {
    >95th percentile: 1.2x rewards,
    >75th percentile: 1.1x rewards,
    >50th percentile: 1.0x rewards,
    <50th percentile: 0.95x rewards,
    <25th percentile: 0.9x rewards
}
```

**Uptime Incentives:**

Consistent uptime rewarded:

```
uptime_bonus = {
    >99.5% uptime: 1.15x,
    >99% uptime: 1.1x,
    >95% uptime: 1.0x,
    <95% uptime: 0.9x,
    <90% uptime: 0.8x
}
```

### Long-Term Participation Rewards

**Tenure Bonuses:**

```python
months_active = (now - join_timestamp) / (30 * 86400)

tenure_bonus = {
    0-1 months: 0.9x,   # New participant penalty
    1-3 months: 1.0x,   # Baseline
    3-6 months: 1.05x,  # Early commitment bonus
    6-12 months: 1.1x,  # Long-term bonus
    >12 months: 1.15x   # Veteran bonus
}
```

**Rationale:**
- Encourages long-term commitment
- Reduces churn
- Rewards early participants
- Builds stable pool

### Referral Program

Participants can refer others and earn bonuses.

**Referral Rewards:**
- Referrer: 2% of referee's rewards for first 3 months
- Referee: 1% bonus on their rewards for first month

**Example:**
```
Alice refers Bob
Bob earns 20 TON in month 1

Alice's referral bonus = 20 × 0.02 = 0.4 TON
Bob's signup bonus = 20 × 0.01 = 0.2 TON
```

**Limits:**
- Maximum 10 referrals per participant
- Referee must maintain >90% uptime for referrer to earn

## Economic Security

### Slashing Mechanism

Participants can be penalized for violations.

**Slashable Offenses:**

| Offense | Penalty | Severity |
|---------|---------|----------|
| Extended downtime (>48h) | 5% stake | Medium |
| Invalid attestation | 10% stake | High |
| Malicious behavior | 25% stake | Critical |
| Repeated violations | 50% stake | Critical |

**Slashing Process:**
1. Pool operator detects violation
2. Submits slashing transaction with evidence
3. Smart contract validates and executes
4. Slashed funds distributed:
   - 50% burned (sent to null address)
   - 50% to pool treasury (for participants)

**Slashing Example:**
```
Participant stake: 100 TON
Offense: Extended downtime (5% penalty)

slashed_amount = 100 × 0.05 = 5 TON
burned = 5 × 0.5 = 2.5 TON
to_treasury = 5 × 0.5 = 2.5 TON

new_stake = 100 - 5 = 95 TON
```

If stake falls below minimum (100 TON), participant is suspended until they top up.

### Attack Resistance

**51% Attack Prevention:**
- No single participant can control >30% of pool resources
- Large participants subject to higher scrutiny
- Governance mechanisms limit operator power

**Sybil Attack Prevention:**
- Minimum stake requirement (100 TON barrier)
- KYC-lite (optional): Link to social accounts
- Reputation system makes new accounts less profitable

**Front-Running Prevention:**
- Contribution scores calculated off-chain, committed on-chain (Merkle root)
- Timestamp-based ordering
- No direct reward visibility before distribution

## Financial Projections

### Small Pool (25 participants, 100 GPUs)

**Assumptions:**
- Average: 4 GPUs per participant
- Utilization: 60%
- Tokens per GPU-hour: 5,000
- Worker fee: 0.0006 TON/token

**Monthly Revenue:**
```
active_gpus = 100 × 0.6 = 60 GPUs
hours_per_month = 30 × 24 = 720 hours
tokens_per_month = 60 × 720 × 5,000 = 216,000,000

revenue = 216M × 0.0006 = 129,600 TON/month
```

**Monthly Distribution:**
```
operator_fee (5%) = 6,480 TON
participant_rewards (95%) = 123,120 TON

avg_participant_reward = 123,120 / 25 = 4,924.8 TON/month
avg_reward_per_gpu = 4,924.8 / 4 = 1,231.2 TON/month
```

**Participant ROI:**
```
participant_costs (per GPU):
  Hardware (H100, amortized): ~$15,000 / 24 months = $625/month = 156 TON
  Electricity (700W @ $0.50/kWh): $250/month = 62.5 TON
  Internet & misc: ~12.5 TON
  Total cost per GPU: ~231 TON/month

revenue_per_gpu = 1,231.2 TON/month
cost_per_gpu = 231 TON/month
profit_per_gpu = 1,000.2 TON/month

ROI = (1,000.2 / 231) × 100 = 433% per month
```

**This is highly profitable**, indicating strong incentives for participation.

### Medium Pool (50 participants, 200 GPUs)

**Revenue:** 259,200 TON/month
**Operator fee:** 12,960 TON/month
**Participant rewards:** 246,240 TON/month
**Avg per participant:** 4,924.8 TON/month (same as small pool)

### Large Pool (100 participants, 400 GPUs)

**Revenue:** 518,400 TON/month
**Operator fee:** 25,920 TON/month
**Participant rewards:** 492,480 TON/month
**Avg per participant:** 4,924.8 TON/month

**Key Insight:** Per-participant rewards scale linearly with pool size, maintaining consistent incentives.

### Pool Operator Profitability

| Pool Size | Operator Fee | Costs | Profit |
|-----------|--------------|-------|--------|
| 25 participants | 6,480 TON | 335 TON | 6,145 TON |
| 50 participants | 12,960 TON | 450 TON | 12,510 TON |
| 100 participants | 25,920 TON | 600 TON | 25,320 TON |

**Operator ROI is excellent**, providing strong incentives to operate pools professionally.

## Conclusion

The economic model is designed to:

1. **Align Incentives**: Participants, operators, and the network all benefit
2. **Ensure Sustainability**: Operator fees cover costs with healthy margins
3. **Promote Quality**: Performance-based rewards encourage excellence
4. **Provide Security**: Staking and slashing protect the pool
5. **Scale Efficiently**: Economics remain favorable as pool grows

The model is **robust, sustainable, and highly attractive** to all stakeholders.
