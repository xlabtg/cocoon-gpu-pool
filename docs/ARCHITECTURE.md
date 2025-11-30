# Cocoon GPU Pool - Smart Contract Architecture

## Overview

This document describes the architecture of the reward distribution system through TON smart contracts with flexible commission for the Cocoon GPU Pool.

## System Components

### 1. PoolOperator Contract
**Purpose**: Manages the registration of the pool in the Cocoon network and oversees pool operations.

**Responsibilities**:
- Register and manage pool in Cocoon network
- Set and update operator commission (5-15%)
- Manage operator stake for reliability guarantee
- Handle operator permissions and roles
- Coordinate with RewardDistribution and ParticipantRegistry

**Key Storage**:
- Operator address
- Commission rate (5-15%)
- Operator stake amount
- Pool status (active/inactive)
- References to RewardDistribution and ParticipantRegistry contracts

### 2. RewardDistribution Contract
**Purpose**: Distributes rewards proportionally to participant contributions with commission deduction.

**Responsibilities**:
- Receive rewards from the Cocoon network
- Calculate reward shares based on participant contributions
- Deduct operator commission (5-15%)
- Apply stability bonuses (uptime > 95%)
- Apply instability penalties (frequent outages)
- Execute automatic scheduled payments
- Track transaction history

**Key Storage**:
- Total rewards pool
- Commission percentage
- Distribution rounds
- Payment schedule
- Pending distributions

**Economic Model**:
- Base reward = participant contribution ratio × total rewards
- Operator commission = total rewards × commission rate
- Stability bonus = base reward × bonus percentage (if uptime > 95%)
- Instability penalty = base reward × penalty percentage (if frequent outages)
- Final reward = base reward + stability bonus - instability penalty - operator commission

### 3. ParticipantRegistry Contract
**Purpose**: Tracks and manages participant contributions and performance metrics.

**Responsibilities**:
- Register/unregister participants
- Track GPU performance metrics
- Monitor uptime and availability
- Calculate contribution scores
- Maintain participant staking balances
- Record performance history

**Key Storage**:
- Participant addresses and metadata
- Running time per participant
- GPU performance scores
- Uptime percentages
- Participant stakes
- Performance history

**Contribution Calculation**:
- Contribution score = (running time × GPU performance score × uptime factor)
- Total pool contribution = sum of all participant contributions
- Individual share = participant contribution / total pool contribution

## Contract Interactions

```
Cocoon Network
      |
      v
[PoolOperator] <---> [ParticipantRegistry]
      |                      |
      |                      v
      +----------> [RewardDistribution]
                            |
                            v
                     Participants
```

### Flow 1: Pool Registration
1. PoolOperator deploys and registers with Cocoon network
2. PoolOperator deploys ParticipantRegistry and RewardDistribution
3. PoolOperator stakes reliability guarantee

### Flow 2: Participant Registration
1. Participant calls ParticipantRegistry to register
2. Participant stakes required amount
3. ParticipantRegistry updates registry and notifies PoolOperator

### Flow 3: Contribution Tracking
1. ParticipantRegistry continuously tracks:
   - Running time
   - GPU performance
   - Uptime percentage
2. Metrics are stored and updated periodically

### Flow 4: Reward Distribution
1. Cocoon network sends rewards to PoolOperator
2. PoolOperator forwards rewards to RewardDistribution
3. RewardDistribution queries ParticipantRegistry for contribution data
4. RewardDistribution calculates shares:
   - Deducts operator commission
   - Applies bonuses/penalties
   - Distributes to participants
5. Automatic scheduled payments execute

## Security Considerations

1. **Access Control**: Only authorized addresses can:
   - Update commission rates (operator)
   - Register participants (verified addresses)
   - Distribute rewards (PoolOperator)

2. **Parameter Validation**:
   - Commission rate must be 5-15%
   - Uptime must be 0-100%
   - Stake amounts must meet minimum requirements

3. **Reentrancy Protection**: All external calls follow checks-effects-interactions pattern

4. **Emergency Controls**:
   - Pause/unpause functionality
   - Emergency withdrawal for operator stake
   - Grace periods for parameter changes

## Economic Parameters

### Commission System
- **Minimum Commission**: 5%
- **Maximum Commission**: 15%
- **Default Commission**: 10%

### Staking Requirements
- **Operator Stake**: Ensures operator reliability and commitment
- **Participant Stake**: Ensures participant commitment and prevents spam

### Bonus/Penalty System
- **Stability Bonus**: +10% for uptime > 95%
- **Minor Instability Penalty**: -5% for uptime 80-95%
- **Major Instability Penalty**: -20% for uptime < 80%
- **Frequent Outage Penalty**: Additional -10% for > 3 outages per week

## Integration Points

### Cocoon Network Integration
- Compatible with existing Cocoon contracts
- Follows Cocoon protocol for pool registration
- Receives rewards through standard Cocoon interface

### TON API Integration
- Transaction tracking via TON API
- Event emission for monitoring
- Support for automatic scheduled payments

## Deployment Strategy

### Testnet Deployment
1. Deploy PoolOperator
2. Deploy ParticipantRegistry
3. Deploy RewardDistribution
4. Link contracts together
5. Register with Cocoon testnet
6. Test with simulated participants

### Mainnet Deployment
1. Audit all contracts
2. Deploy PoolOperator with operator stake
3. Deploy ParticipantRegistry
4. Deploy RewardDistribution
5. Link contracts and verify
6. Register with Cocoon mainnet
7. Gradual rollout with monitoring

## Testing Strategy

### Unit Tests
- Test each contract function independently
- Test parameter validation
- Test access controls
- Test edge cases

### Integration Tests
- Test contract interactions
- Test reward distribution flows
- Test participant lifecycle
- Test emergency scenarios

### Coverage Requirements
- 100% line coverage
- All edge cases covered
- All error paths tested
- All access controls verified
