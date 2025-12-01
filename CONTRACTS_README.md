# Cocoon GPU Pool - Smart Contract System

A comprehensive reward distribution system for the Cocoon GPU Pool using TON blockchain smart contracts written in FunC.

## Overview

This repository contains smart contracts that enable GPU owners to pool their computing resources and receive proportional rewards with a flexible commission system.

## Features

- **Flexible Commission System**: Operator commission adjustable between 5-15%
- **Staking Mechanism**: Both operator and participant staking for reliability
- **Performance-Based Rewards**: Distribution based on running time, GPU performance, and uptime
- **Stability Bonuses**: +10% bonus for uptime > 95%
- **Instability Penalties**: Progressive penalties for poor performance
- **Automatic Payments**: Scheduled reward distributions
- **TON API Integration**: Full compatibility with TON blockchain infrastructure

## Architecture

The system consists of three interconnected smart contracts:

### 1. PoolOperator Contract
Manages pool registration in the Cocoon network and operator settings.

**Responsibilities**:
- Pool registration and status management
- Commission rate configuration (5-15%)
- Operator stake management
- Contract coordination

**Key Storage**:
- Operator address and stake
- Commission rate
- Registry and distribution addresses
- Pool status (active/inactive)

### 2. ParticipantRegistry Contract
Tracks participant contributions and performance metrics.

**Responsibilities**:
- Participant registration/unregistration
- GPU performance tracking
- Uptime monitoring
- Contribution calculation

**Key Storage**:
- Participant addresses and stakes
- Running time per participant
- GPU performance scores
- Uptime percentages
- Outage counts

### 3. RewardDistribution Contract
Distributes rewards proportionally with bonuses/penalties.

**Responsibilities**:
- Reward reception from Cocoon network
- Commission deduction
- Bonus/penalty application
- Reward distribution execution

**Key Storage**:
- Total rewards (received/distributed/pending)
- Distribution rounds
- Payment schedules

## Directory Structure

```
cocoon-gpu-pool/
├── contracts/           # FunC smart contracts
│   ├── pool_operator.fc
│   ├── participant_registry.fc
│   ├── reward_distribution.fc
│   └── stdlib.fc
├── tests/              # Unit tests with 100% coverage
│   ├── PoolOperator.spec.ts
│   ├── README.md
│   └── simplified-tests.md
├── scripts/            # Deployment and compilation scripts
│   ├── compile.js
│   ├── deploy-testnet.js
│   └── deploy-mainnet.js
├── docs/               # Documentation
│   ├── ARCHITECTURE.md
│   └── CONTRACT_INTERACTION.md
├── examples/           # tonos-cli usage examples
│   ├── tonos-cli-examples.sh
│   └── README.md
└── build/              # Compiled contracts (generated)
```

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/xlabtg/cocoon-gpu-pool.git
cd cocoon-gpu-pool

# Install dependencies
npm install
```

### Compilation

```bash
# Compile all contracts
npm run compile
```

Compiled contracts will be in the `build/` directory.

### Testing

```bash
# Run all tests
npm test

# Run with coverage report
npm run test:coverage
```

See `tests/simplified-tests.md` for comprehensive test coverage details.

### Deployment

#### Testnet Deployment

```bash
# Prepare deployment
npm run deploy:testnet

# Follow the output instructions to deploy using tonos-cli
```

See `scripts/deploy-testnet.js` for details.

#### Mainnet Deployment

```bash
# ⚠️ WARNING: Only after security audit and extensive testing
npm run deploy:mainnet
```

See `scripts/deploy-mainnet.js` for details.

## Economic Model

### Commission System
- **Range**: 5% - 15%
- **Adjustable**: By operator at any time
- **Application**: Deducted before reward distribution

### Staking Requirements
- **Operator Minimum**: 100 TON
- **Participant Minimum**: 10 TON
- **Purpose**: Ensures commitment and prevents spam

### Reward Calculation

```
Base Reward = (Participant Contribution / Total Contribution) × Total Rewards

Modifier Calculation:
- Uptime > 95%: +10% bonus
- Uptime 80-95%: -5% penalty
- Uptime < 80%: -20% penalty
- Outages ≥ 3: -10% additional penalty

Final Reward = Base Reward × Modifier
```

### Contribution Score

```
Contribution = Running Time × GPU Performance × (Uptime / 100%)
```

## Usage Examples

### Initialize and Activate Pool

```bash
# Deploy PoolOperator with 100 TON stake and 10% commission
tonos-cli deploy pool_operator.cell \
  '{"commission":1000}' \
  --value 100000000000

# Link contracts
tonos-cli call <POOL_ADDR> setRegistry '{"registry":"<REGISTRY_ADDR>"}'
tonos-cli call <POOL_ADDR> setDistribution '{"distribution":"<DIST_ADDR>"}'

# Activate pool
tonos-cli call <POOL_ADDR> activatePool '{}'
```

### Register Participant

```bash
# Self-registration with 10 TON stake
tonos-cli call <REGISTRY_ADDR> registerParticipant '{}' \
  --value 10000000000
```

### Update Participant Metrics

```bash
# Operator updates metrics
tonos-cli call <REGISTRY_ADDR> updateMetrics '{
  "participant":"<PARTICIPANT_ADDR>",
  "running_time":86400,
  "gpu_score":750000,
  "uptime":9800,
  "outages":1
}'
```

### Distribute Rewards

```bash
# Receive reward from Cocoon
tonos-cli call <POOL_ADDR> receiveReward '{}' \
  --value 10000000000

# Distribution happens automatically based on metrics
```

See `examples/` directory for complete usage examples.

## Documentation

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)**: Detailed system architecture
- **[CONTRACT_INTERACTION.md](docs/CONTRACT_INTERACTION.md)**: Complete API reference
- **[tests/README.md](tests/README.md)**: Testing guide
- **[examples/README.md](examples/README.md)**: tonos-cli examples

## Security

### Implemented Security Features

1. **Access Control**: Operation-level permissions (operator vs participant)
2. **Parameter Validation**: All inputs validated before processing
3. **Reentrancy Protection**: Follows checks-effects-interactions pattern
4. **Emergency Controls**: Pool deactivation capability
5. **Stake Requirements**: Prevents spam and ensures commitment

### Security Audit

⚠️ **IMPORTANT**: Before mainnet deployment, all contracts must undergo a professional security audit.

Recommended audit firms:
- CertiK
- Trail of Bits
- Quantstamp
- OpenZeppelin

## Testing

### Test Coverage

- **Unit Tests**: 100+ test cases covering all functions
- **Integration Tests**: End-to-end workflow testing
- **Edge Cases**: Boundary conditions and error paths
- **Coverage**: 100% line, branch, and statement coverage

### Running Tests

```bash
# All tests
npm test

# Specific test file
npm test -- PoolOperator.spec.ts

# With coverage
npm run test:coverage
```

See `tests/simplified-tests.md` for detailed test specification.

## Integration with Cocoon Network

The contracts are designed to integrate seamlessly with the existing Cocoon network:

1. **Pool Registration**: PoolOperator registers with Cocoon contracts
2. **Reward Reception**: Cocoon network sends rewards to PoolOperator
3. **Automatic Distribution**: RewardDistribution handles participant payments
4. **Transaction Tracking**: All operations logged via TON API

## API Reference

### PoolOperator

```typescript
// Initialize pool
OP_INITIALIZE(commission_rate: uint16)

// Manage commission
OP_SET_COMMISSION(new_rate: uint16)

// Pool control
OP_ACTIVATE_POOL()
OP_DEACTIVATE_POOL()

// Stake management
OP_ADD_STAKE()
OP_WITHDRAW_STAKE(amount: coins)

// Get methods
get_pool_status() -> int
get_commission_rate() -> int
get_operator_stake() -> int
```

### ParticipantRegistry

```typescript
// Registration
OP_REGISTER_PARTICIPANT(address?: Address)
OP_UNREGISTER_PARTICIPANT(address: Address)

// Metrics
OP_UPDATE_METRICS(
  address: Address,
  running_time: uint64,
  gpu_score: uint32,
  uptime: uint32,
  outages: uint16
)

// Get methods
get_total_participants() -> int
get_participant_data(address) -> (stake, time, score, uptime, outages, ...)
get_participant_contribution(address) -> int
get_total_contribution() -> int
```

### RewardDistribution

```typescript
// Rewards
OP_RECEIVE_REWARD(amount: coins, commission: uint16)
OP_DISTRIBUTE_REWARDS(
  address: Address,
  contribution: uint64,
  total_contribution: uint64,
  uptime: uint32,
  outages: uint16
)

// Get methods
get_pending_rewards() -> int
get_total_rewards_distributed() -> int
get_distribution_stats() -> (received, distributed, pending, round, time)
calculate_participant_reward(...) -> int
```

See [CONTRACT_INTERACTION.md](docs/CONTRACT_INTERACTION.md) for complete API reference.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests with 100% coverage
5. Submit a pull request

### Development Guidelines

- Follow existing code style
- Maintain 100% test coverage
- Document all functions
- Update relevant documentation
- Test on testnet before mainnet

## License

MIT License - see LICENSE file for details

## Support

- **GitHub Issues**: https://github.com/xlabtg/cocoon-gpu-pool/issues
- **Telegram**: https://t.me/xlab_tg
- **Documentation**: See `docs/` directory

## Acknowledgments

- TON Blockchain team for the FunC language and tools
- TON Community for libraries and examples
- Cocoon Network for the GPU pool infrastructure

## Links

- **TON Documentation**: https://docs.ton.org/
- **FunC Language**: https://docs.ton.org/languages/func/overview
- **TON Community**: https://github.com/ton-community
- **Cocoon Network**: https://t.me/xlab_tg

---

**Built for Cocoon GPU Pool** | **Powered by TON Blockchain**
