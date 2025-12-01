# tonos-cli Usage Examples

This directory contains examples of how to interact with the Cocoon GPU Pool smart contracts using tonos-cli.

## Prerequisites

1. **Install tonos-cli**

   Download from: https://github.com/tonlabs/tonos-cli/releases

   ```bash
   wget https://github.com/tonlabs/tonos-cli/releases/latest/download/tonos-cli-linux
   chmod +x tonos-cli-linux
   sudo mv tonos-cli-linux /usr/local/bin/tonos-cli
   ```

2. **Generate Keys**

   ```bash
   tonos-cli genkey operator.keys.json
   tonos-cli genkey participant.keys.json
   ```

3. **Get Testnet TON**

   - Get your address: `tonos-cli genaddr <contract>.tvc --abi <contract>.abi.json --setkey operator.keys.json`
   - Request testnet TON from: https://t.me/testgiver_ton_bot

## Quick Start

1. **Compile Contracts**

   ```bash
   npm run compile
   ```

2. **Review Examples**

   ```bash
   cat examples/tonos-cli-examples.sh
   ```

3. **Run Examples**

   The examples script shows all operations. Execute them one by one, replacing placeholder addresses with actual deployed addresses.

## Example Workflows

### 1. Deploy All Contracts

```bash
# Deploy PoolOperator
tonos-cli deploy \
  --abi contracts/pool_operator.abi.json \
  --sign operator.keys.json \
  --wc 0 \
  build/pool_operator.cell \
  '{"commission":1000}' \
  --value 100000000000

# Deploy ParticipantRegistry
tonos-cli deploy \
  --abi contracts/participant_registry.abi.json \
  --sign operator.keys.json \
  --wc 0 \
  build/participant_registry.cell \
  '{}' \
  --value 1000000000

# Deploy RewardDistribution
tonos-cli deploy \
  --abi contracts/reward_distribution.abi.json \
  --sign operator.keys.json \
  --wc 0 \
  build/reward_distribution.cell \
  '{"registry":"<REGISTRY_ADDR>"}' \
  --value 1000000000
```

### 2. Link Contracts

```bash
# Set registry in PoolOperator
tonos-cli call <POOL_OPERATOR_ADDR> \
  setRegistry \
  '{"registry":"<REGISTRY_ADDR>"}' \
  --sign operator.keys.json \
  --abi contracts/pool_operator.abi.json

# Set distribution in PoolOperator
tonos-cli call <POOL_OPERATOR_ADDR> \
  setDistribution \
  '{"distribution":"<DISTRIBUTION_ADDR>"}' \
  --sign operator.keys.json \
  --abi contracts/pool_operator.abi.json
```

### 3. Activate Pool

```bash
tonos-cli call <POOL_OPERATOR_ADDR> \
  activatePool \
  '{}' \
  --sign operator.keys.json \
  --abi contracts/pool_operator.abi.json
```

### 4. Register Participant

```bash
tonos-cli call <REGISTRY_ADDR> \
  registerParticipant \
  '{}' \
  --sign participant.keys.json \
  --abi contracts/participant_registry.abi.json \
  --value 10000000000
```

### 5. Update Metrics

```bash
tonos-cli call <REGISTRY_ADDR> \
  updateMetrics \
  '{
    "participant":"<PARTICIPANT_ADDR>",
    "running_time":86400,
    "gpu_score":750000,
    "uptime":9800,
    "outages":1
  }' \
  --sign operator.keys.json \
  --abi contracts/participant_registry.abi.json
```

### 6. Query State

```bash
# Get pool status
tonos-cli run <POOL_OPERATOR_ADDR> \
  get_pool_status \
  '{}' \
  --abi contracts/pool_operator.abi.json

# Get participant data
tonos-cli run <REGISTRY_ADDR> \
  get_participant_data \
  '{"participant":"<PARTICIPANT_ADDR>"}' \
  --abi contracts/participant_registry.abi.json

# Get pending rewards
tonos-cli run <DISTRIBUTION_ADDR> \
  get_pending_rewards \
  '{}' \
  --abi contracts/reward_distribution.abi.json
```

## Network Configuration

### Testnet

```bash
export NETWORK="--url https://testnet.toncenter.com/api/v2/jsonRPC"
tonos-cli config --url https://testnet.toncenter.com/api/v2/jsonRPC
```

### Mainnet

```bash
export NETWORK="--url https://toncenter.com/api/v2/jsonRPC"
tonos-cli config --url https://toncenter.com/api/v2/jsonRPC
```

## Important Notes

1. **Gas Fees**: All operations require gas fees. Ensure wallet has sufficient TON.

2. **Stake Requirements**:
   - Operator: Minimum 100 TON
   - Participant: Minimum 10 TON

3. **Commission Range**: 5-15% (500-1500 basis points)

4. **Uptime Format**: Percentage × 100 (e.g., 9500 = 95%)

5. **Error Handling**: Check transaction status after each operation

## Troubleshooting

### Transaction Failed

Check the error code in the transaction result and refer to the error codes in docs/CONTRACT_INTERACTION.md.

### Insufficient Funds

Ensure wallet has enough TON for:
- Transaction value
- Gas fees (~0.1-1 TON per transaction)

### Invalid Parameters

Verify:
- Addresses are correct and in proper format
- Numeric values are within allowed ranges
- Required permissions (operator vs participant)

## Reference

For complete API documentation, see:
- [docs/CONTRACT_INTERACTION.md](../docs/CONTRACT_INTERACTION.md)
- [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md)

## Support

For issues or questions:
- GitHub: https://github.com/xlabtg/cocoon-gpu-pool/issues
- Telegram: https://t.me/xlab_tg
