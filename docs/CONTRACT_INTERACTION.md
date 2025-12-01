# Contract Interaction Guide

This document provides detailed instructions for interacting with the Cocoon GPU Pool smart contracts.

## Table of Contents

1. [Contract Overview](#contract-overview)
2. [Operation Codes](#operation-codes)
3. [PoolOperator Interactions](#pooloperator-interactions)
4. [ParticipantRegistry Interactions](#participantregistry-interactions)
5. [RewardDistribution Interactions](#rewarddistribution-interactions)
6. [Get Methods](#get-methods)
7. [Common Workflows](#common-workflows)

## Contract Overview

The system consists of three interconnected smart contracts:

- **PoolOperator**: Manages pool operations and operator settings
- **ParticipantRegistry**: Tracks participant contributions and metrics
- **RewardDistribution**: Handles reward calculations and distributions

## Operation Codes

### PoolOperator Operations

| Code | Operation | Description |
|------|-----------|-------------|
| 1 | OP_INITIALIZE | Initialize the contract |
| 2 | OP_SET_COMMISSION | Update commission rate |
| 3 | OP_ADD_STAKE | Add operator stake |
| 4 | OP_ACTIVATE_POOL | Activate the pool |
| 5 | OP_DEACTIVATE_POOL | Deactivate the pool |
| 6 | OP_WITHDRAW_STAKE | Withdraw operator stake |
| 7 | OP_RECEIVE_REWARD | Receive rewards from Cocoon |
| 8 | OP_SET_REGISTRY | Set registry address |
| 9 | OP_SET_DISTRIBUTION | Set distribution address |

### ParticipantRegistry Operations

| Code | Operation | Description |
|------|-----------|-------------|
| 1 | OP_INITIALIZE | Initialize the contract |
| 10 | OP_REGISTER_PARTICIPANT | Register a new participant |
| 11 | OP_UNREGISTER_PARTICIPANT | Remove a participant |
| 12 | OP_UPDATE_METRICS | Update participant metrics |
| 13 | OP_ADD_PARTICIPANT_STAKE | Add to participant stake |
| 14 | OP_WITHDRAW_PARTICIPANT_STAKE | Withdraw participant stake |

### RewardDistribution Operations

| Code | Operation | Description |
|------|-----------|-------------|
| 1 | OP_INITIALIZE | Initialize the contract |
| 7 | OP_RECEIVE_REWARD | Receive rewards from operator |
| 20 | OP_DISTRIBUTE_REWARDS | Distribute to a participant |
| 21 | OP_MANUAL_DISTRIBUTE | Trigger manual distribution |

## PoolOperator Interactions

### Initialize Pool

```
Message Body:
- op (uint32): 1
- commission_rate (uint16): 500-1500 (5%-15%)

Value: >= 100 TON (operator stake)
```

Example:
```javascript
{
  op: 1,
  commission: 1000  // 10%
}
// Send with 100+ TON
```

### Update Commission

```
Message Body:
- op (uint32): 2
- new_commission (uint16): 500-1500

Sender: Operator only
```

### Set Registry Address

```
Message Body:
- op (uint32): 8
- registry_address (address): ParticipantRegistry contract address

Sender: Operator only
```

### Set Distribution Address

```
Message Body:
- op (uint32): 9
- distribution_address (address): RewardDistribution contract address

Sender: Operator only
```

### Activate Pool

```
Message Body:
- op (uint32): 4

Requirements:
- Operator stake >= 100 TON
- Registry address set
- Distribution address set

Sender: Operator only
```

### Deactivate Pool

```
Message Body:
- op (uint32): 5

Sender: Operator only
```

### Add Stake

```
Message Body:
- op (uint32): 3

Value: Amount to add to stake

Sender: Operator only
```

### Withdraw Stake

```
Message Body:
- op (uint32): 6
- withdraw_amount (coins): Amount to withdraw

Requirements:
- Pool must be inactive

Sender: Operator only
```

## ParticipantRegistry Interactions

### Register Participant

```
Message Body:
- op (uint32): 10
- participant_address (address): Optional, defaults to sender

Value: >= 10 TON (participant stake)

Sender: Operator or participant
```

Example:
```javascript
// Self-registration
{
  op: 10
}
// Send with 10+ TON

// Operator registering others
{
  op: 10,
  participant: "EQD_..."
}
```

### Unregister Participant

```
Message Body:
- op (uint32): 11
- participant_address (address): Address to unregister

Sender: Operator or participant themselves
```

### Update Metrics

```
Message Body:
- op (uint32): 12
- participant_address (address): Address to update
- running_time (uint64): Total running time in seconds
- gpu_score (uint32): GPU performance score (0-1000000)
- uptime (uint32): Uptime percentage * 100 (e.g., 9500 = 95%)
- outages (uint16): Number of outages

Sender: Operator only
```

Example:
```javascript
{
  op: 12,
  participant: "EQD_...",
  running_time: 86400,  // 1 day
  gpu_score: 750000,    // High performance
  uptime: 9800,         // 98% uptime
  outages: 1            // 1 outage
}
```

### Add Participant Stake

```
Message Body:
- op (uint32): 13

Value: Amount to add

Sender: Participant
```

### Withdraw Participant Stake

```
Message Body:
- op (uint32): 14
- withdraw_amount (coins): Amount to withdraw

Requirements:
- Remaining stake >= 10 TON

Sender: Participant
```

## RewardDistribution Interactions

### Initialize

```
Message Body:
- op (uint32): 1
- registry_address (address): ParticipantRegistry address

Sender: Operator
```

### Receive Reward (from PoolOperator)

```
Message Body:
- op (uint32): 7
- reward_amount (coins): Total reward amount
- commission_rate (uint16): Commission rate

Sender: PoolOperator only
```

### Manual Distribution Trigger

```
Message Body:
- op (uint32): 21

Sender: Operator only
```

### Distribute to Participant

```
Message Body:
- op (uint32): 20
- participant_address (address): Recipient
- contribution (uint64): Participant's contribution score
- total_contribution (uint64): Total pool contribution
- uptime (uint32): Participant uptime
- outages (uint16): Participant outages

Sender: Operator only
```

Example:
```javascript
{
  op: 20,
  participant: "EQD_...",
  contribution: 1000000,
  total_contribution: 5000000,  // 20% share
  uptime: 9600,                 // 96% uptime -> bonus
  outages: 2                    // Low outages
}
```

## Get Methods

### PoolOperator Get Methods

```typescript
// Get pool status (0 = inactive, 1 = active)
get_pool_status() -> int

// Get commission rate in basis points
get_commission_rate() -> int

// Get operator stake amount
get_operator_stake() -> int

// Get operator address
get_operator_address() -> slice

// Get registry contract address
get_registry_address() -> slice

// Get distribution contract address
get_distribution_address() -> slice

// Get all pool data
get_pool_data() -> (slice, int, int, int, slice, slice)
```

### ParticipantRegistry Get Methods

```typescript
// Get total number of participants
get_total_participants() -> int

// Get participant data
get_participant_data(slice participant_addr) -> (int, int, int, int, int, int, int)
// Returns: (stake, running_time, gpu_score, uptime, outages, last_update, reg_time)

// Get participant contribution score
get_participant_contribution(slice participant_addr) -> int

// Get total pool contribution
get_total_contribution() -> int

// Get operator address
get_operator_address() -> slice
```

### RewardDistribution Get Methods

```typescript
// Get total rewards received
get_total_rewards_received() -> int

// Get total rewards distributed
get_total_rewards_distributed() -> int

// Get pending rewards
get_pending_rewards() -> int

// Get current distribution round
get_distribution_round() -> int

// Get last distribution timestamp
get_last_distribution_time() -> int

// Get operator address
get_operator_address() -> slice

// Get registry address
get_registry_address() -> slice

// Get distribution statistics
get_distribution_stats() -> (int, int, int, int, int)
// Returns: (total_received, total_distributed, pending, round, last_time)

// Calculate participant reward estimate
calculate_participant_reward(int contribution, int total_contribution, int uptime, int outages) -> int
```

## Common Workflows

### 1. Initial Setup

```
1. Deploy PoolOperator with operator stake
2. Deploy ParticipantRegistry
3. Deploy RewardDistribution with registry address
4. Set registry address in PoolOperator
5. Set distribution address in PoolOperator
6. Activate pool
```

### 2. Participant Registration

```
1. Participant sends registration message with stake
2. Operator updates participant metrics periodically
3. Participant contribution is calculated automatically
```

### 3. Reward Distribution

```
1. Cocoon network sends rewards to PoolOperator
2. PoolOperator forwards to RewardDistribution
3. Operator commission is deducted
4. Operator triggers distribution
5. RewardDistribution queries ParticipantRegistry
6. Rewards are calculated with bonuses/penalties
7. Payments are sent to participants
```

### 4. Commission Update

```
1. Operator sends update commission message
2. New commission takes effect immediately
3. Future distributions use new rate
```

### 5. Pool Deactivation

```
1. Operator deactivates pool
2. No new rewards accepted
3. Operator can withdraw stake
4. Participants can withdraw stakes
```

## Error Codes

| Code | Name | Description |
|------|------|-------------|
| 401 | ERROR_UNAUTHORIZED | Sender not authorized |
| 402 | ERROR_INVALID_COMMISSION | Commission not in 5-15% range |
| 403 | ERROR_INSUFFICIENT_STAKE | Stake below minimum |
| 404 | ERROR_POOL_INACTIVE | Pool not active |
| 405 | ERROR_INVALID_ADDRESS | Invalid address provided |
| 406 | ERROR_ALREADY_INITIALIZED | Contract already initialized |
| 407 | ERROR_PARTICIPANT_EXISTS | Participant already registered |
| 408 | ERROR_PARTICIPANT_NOT_FOUND | Participant not found |
| 409 | ERROR_INVALID_UPTIME | Uptime not in valid range |
| 410 | ERROR_INSUFFICIENT_REWARDS | Not enough rewards to distribute |
| 411 | ERROR_INVALID_AMOUNT | Invalid amount specified |
| 412 | ERROR_DISTRIBUTION_FAILED | Distribution failed |

## Economic Parameters

### Commission
- Minimum: 5% (500 basis points)
- Maximum: 15% (1500 basis points)
- Adjustable by operator

### Stakes
- Operator minimum: 100 TON
- Participant minimum: 10 TON

### Bonuses and Penalties
- Stability bonus: +10% for uptime > 95%
- Minor penalty: -5% for uptime 80-95%
- Major penalty: -20% for uptime < 80%
- Outage penalty: -10% for 3+ outages

### Uptime Calculation
- Stored as: uptime * 100 (e.g., 9500 = 95%)
- Range: 0-10000 (0%-100%)
- Precision: 0.01%
