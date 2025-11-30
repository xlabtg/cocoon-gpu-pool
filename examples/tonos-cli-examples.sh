#!/bin/bash

# TON OS CLI Examples for Cocoon GPU Pool Smart Contracts
# This script demonstrates how to interact with the contracts using tonos-cli

# Prerequisites:
# 1. Install tonos-cli: https://github.com/tonlabs/tonos-cli
# 2. Generate wallet keys
# 3. Fund wallet with testnet TON

# Configuration
NETWORK="--url https://testnet.toncenter.com/api/v2/jsonRPC"
OPERATOR_KEY="operator.keys.json"
PARTICIPANT_KEY="participant.keys.json"

# Contract addresses (replace with actual deployed addresses)
POOL_OPERATOR_ADDR="EQD_POOL_OPERATOR_ADDRESS"
PARTICIPANT_REGISTRY_ADDR="EQD_REGISTRY_ADDRESS"
REWARD_DISTRIBUTION_ADDR="EQD_DISTRIBUTION_ADDRESS"

echo "=========================================="
echo "Cocoon GPU Pool - tonos-cli Examples"
echo "=========================================="
echo ""

# ==========================================
# Part 1: Generate Keys
# ==========================================
echo "Part 1: Generate Keys"
echo "----------------------------------------"

echo "Generate operator keys:"
echo "tonos-cli genkey $OPERATOR_KEY"
echo ""

echo "Generate participant keys:"
echo "tonos-cli genkey $PARTICIPANT_KEY"
echo ""

# ==========================================
# Part 2: Deploy Contracts
# ==========================================
echo "Part 2: Deploy Contracts"
echo "----------------------------------------"

echo "Compile contracts first with:"
echo "npm run compile"
echo ""

echo "Deploy PoolOperator:"
echo "tonos-cli $NETWORK deploy \\"
echo "  --abi contracts/pool_operator.abi.json \\"
echo "  --sign $OPERATOR_KEY \\"
echo "  --wc 0 \\"
echo "  build/pool_operator.cell \\"
echo "  '{\"commission\":1000}' \\"
echo "  --value 100000000000"
echo ""

echo "Deploy ParticipantRegistry:"
echo "tonos-cli $NETWORK deploy \\"
echo "  --abi contracts/participant_registry.abi.json \\"
echo "  --sign $OPERATOR_KEY \\"
echo "  --wc 0 \\"
echo "  build/participant_registry.cell \\"
echo "  '{}' \\"
echo "  --value 1000000000"
echo ""

echo "Deploy RewardDistribution:"
echo "tonos-cli $NETWORK deploy \\"
echo "  --abi contracts/reward_distribution.abi.json \\"
echo "  --sign $OPERATOR_KEY \\"
echo "  --wc 0 \\"
echo "  build/reward_distribution.cell \\"
echo "  '{\"registry\":\"$PARTICIPANT_REGISTRY_ADDR\"}' \\"
echo "  --value 1000000000"
echo ""

# ==========================================
# Part 3: Link Contracts
# ==========================================
echo "Part 3: Link Contracts"
echo "----------------------------------------"

echo "Set registry address in PoolOperator:"
echo "tonos-cli $NETWORK call $POOL_OPERATOR_ADDR \\"
echo "  setRegistry \\"
echo "  '{\"registry\":\"$PARTICIPANT_REGISTRY_ADDR\"}' \\"
echo "  --sign $OPERATOR_KEY \\"
echo "  --abi contracts/pool_operator.abi.json"
echo ""

echo "Set distribution address in PoolOperator:"
echo "tonos-cli $NETWORK call $POOL_OPERATOR_ADDR \\"
echo "  setDistribution \\"
echo "  '{\"distribution\":\"$REWARD_DISTRIBUTION_ADDR\"}' \\"
echo "  --sign $OPERATOR_KEY \\"
echo "  --abi contracts/pool_operator.abi.json"
echo ""

# ==========================================
# Part 4: Pool Management
# ==========================================
echo "Part 4: Pool Management"
echo "----------------------------------------"

echo "Activate pool:"
echo "tonos-cli $NETWORK call $POOL_OPERATOR_ADDR \\"
echo "  activatePool \\"
echo "  '{}' \\"
echo "  --sign $OPERATOR_KEY \\"
echo "  --abi contracts/pool_operator.abi.json"
echo ""

echo "Update commission rate to 12%:"
echo "tonos-cli $NETWORK call $POOL_OPERATOR_ADDR \\"
echo "  setCommission \\"
echo "  '{\"commission\":1200}' \\"
echo "  --sign $OPERATOR_KEY \\"
echo "  --abi contracts/pool_operator.abi.json"
echo ""

echo "Add operator stake:"
echo "tonos-cli $NETWORK call $POOL_OPERATOR_ADDR \\"
echo "  addStake \\"
echo "  '{}' \\"
echo "  --sign $OPERATOR_KEY \\"
echo "  --abi contracts/pool_operator.abi.json \\"
echo "  --value 50000000000"
echo ""

# ==========================================
# Part 5: Participant Management
# ==========================================
echo "Part 5: Participant Management"
echo "----------------------------------------"

echo "Register participant (self-registration):"
echo "tonos-cli $NETWORK call $PARTICIPANT_REGISTRY_ADDR \\"
echo "  registerParticipant \\"
echo "  '{}' \\"
echo "  --sign $PARTICIPANT_KEY \\"
echo "  --abi contracts/participant_registry.abi.json \\"
echo "  --value 10000000000"
echo ""

echo "Update participant metrics (operator only):"
echo "tonos-cli $NETWORK call $PARTICIPANT_REGISTRY_ADDR \\"
echo "  updateMetrics \\"
echo "  '{
    \"participant\":\"<PARTICIPANT_ADDRESS>\",
    \"running_time\":86400,
    \"gpu_score\":750000,
    \"uptime\":9800,
    \"outages\":1
  }' \\"
echo "  --sign $OPERATOR_KEY \\"
echo "  --abi contracts/participant_registry.abi.json"
echo ""

echo "Add participant stake:"
echo "tonos-cli $NETWORK call $PARTICIPANT_REGISTRY_ADDR \\"
echo "  addParticipantStake \\"
echo "  '{}' \\"
echo "  --sign $PARTICIPANT_KEY \\"
echo "  --abi contracts/participant_registry.abi.json \\"
echo "  --value 5000000000"
echo ""

# ==========================================
# Part 6: Reward Distribution
# ==========================================
echo "Part 6: Reward Distribution"
echo "----------------------------------------"

echo "Receive reward from Cocoon (via PoolOperator):"
echo "tonos-cli $NETWORK call $POOL_OPERATOR_ADDR \\"
echo "  receiveReward \\"
echo "  '{}' \\"
echo "  --sign cocoon_network.keys.json \\"
echo "  --abi contracts/pool_operator.abi.json \\"
echo "  --value 10000000000"
echo ""

echo "Trigger manual distribution:"
echo "tonos-cli $NETWORK call $REWARD_DISTRIBUTION_ADDR \\"
echo "  manualDistribute \\"
echo "  '{}' \\"
echo "  --sign $OPERATOR_KEY \\"
echo "  --abi contracts/reward_distribution.abi.json"
echo ""

echo "Distribute to specific participant:"
echo "tonos-cli $NETWORK call $REWARD_DISTRIBUTION_ADDR \\"
echo "  distributeRewards \\"
echo "  '{
    \"participant\":\"<PARTICIPANT_ADDRESS>\",
    \"contribution\":1000000,
    \"total_contribution\":5000000,
    \"uptime\":9600,
    \"outages\":2
  }' \\"
echo "  --sign $OPERATOR_KEY \\"
echo "  --abi contracts/reward_distribution.abi.json"
echo ""

# ==========================================
# Part 7: Query State (Get Methods)
# ==========================================
echo "Part 7: Query State (Get Methods)"
echo "----------------------------------------"

echo "Get pool status:"
echo "tonos-cli $NETWORK run $POOL_OPERATOR_ADDR \\"
echo "  get_pool_status \\"
echo "  '{}' \\"
echo "  --abi contracts/pool_operator.abi.json"
echo ""

echo "Get commission rate:"
echo "tonos-cli $NETWORK run $POOL_OPERATOR_ADDR \\"
echo "  get_commission_rate \\"
echo "  '{}' \\"
echo "  --abi contracts/pool_operator.abi.json"
echo ""

echo "Get operator stake:"
echo "tonos-cli $NETWORK run $POOL_OPERATOR_ADDR \\"
echo "  get_operator_stake \\"
echo "  '{}' \\"
echo "  --abi contracts/pool_operator.abi.json"
echo ""

echo "Get total participants:"
echo "tonos-cli $NETWORK run $PARTICIPANT_REGISTRY_ADDR \\"
echo "  get_total_participants \\"
echo "  '{}' \\"
echo "  --abi contracts/participant_registry.abi.json"
echo ""

echo "Get participant data:"
echo "tonos-cli $NETWORK run $PARTICIPANT_REGISTRY_ADDR \\"
echo "  get_participant_data \\"
echo "  '{\"participant\":\"<PARTICIPANT_ADDRESS>\"}' \\"
echo "  --abi contracts/participant_registry.abi.json"
echo ""

echo "Get participant contribution:"
echo "tonos-cli $NETWORK run $PARTICIPANT_REGISTRY_ADDR \\"
echo "  get_participant_contribution \\"
echo "  '{\"participant\":\"<PARTICIPANT_ADDRESS>\"}' \\"
echo "  --abi contracts/participant_registry.abi.json"
echo ""

echo "Get total pool contribution:"
echo "tonos-cli $NETWORK run $PARTICIPANT_REGISTRY_ADDR \\"
echo "  get_total_contribution \\"
echo "  '{}' \\"
echo "  --abi contracts/participant_registry.abi.json"
echo ""

echo "Get pending rewards:"
echo "tonos-cli $NETWORK run $REWARD_DISTRIBUTION_ADDR \\"
echo "  get_pending_rewards \\"
echo "  '{}' \\"
echo "  --abi contracts/reward_distribution.abi.json"
echo ""

echo "Get distribution statistics:"
echo "tonos-cli $NETWORK run $REWARD_DISTRIBUTION_ADDR \\"
echo "  get_distribution_stats \\"
echo "  '{}' \\"
echo "  --abi contracts/reward_distribution.abi.json"
echo ""

echo "Calculate participant reward estimate:"
echo "tonos-cli $NETWORK run $REWARD_DISTRIBUTION_ADDR \\"
echo "  calculate_participant_reward \\"
echo "  '{
    \"contribution\":1000000,
    \"total_contribution\":5000000,
    \"uptime\":9600,
    \"outages\":2
  }' \\"
echo "  --abi contracts/reward_distribution.abi.json"
echo ""

# ==========================================
# Part 8: Advanced Operations
# ==========================================
echo "Part 8: Advanced Operations"
echo "----------------------------------------"

echo "Withdraw participant stake:"
echo "tonos-cli $NETWORK call $PARTICIPANT_REGISTRY_ADDR \\"
echo "  withdrawParticipantStake \\"
echo "  '{\"amount\":3000000000}' \\"
echo "  --sign $PARTICIPANT_KEY \\"
echo "  --abi contracts/participant_registry.abi.json"
echo ""

echo "Unregister participant:"
echo "tonos-cli $NETWORK call $PARTICIPANT_REGISTRY_ADDR \\"
echo "  unregisterParticipant \\"
echo "  '{\"participant\":\"<PARTICIPANT_ADDRESS>\"}' \\"
echo "  --sign $PARTICIPANT_KEY \\"
echo "  --abi contracts/participant_registry.abi.json"
echo ""

echo "Deactivate pool:"
echo "tonos-cli $NETWORK call $POOL_OPERATOR_ADDR \\"
echo "  deactivatePool \\"
echo "  '{}' \\"
echo "  --sign $OPERATOR_KEY \\"
echo "  --abi contracts/pool_operator.abi.json"
echo ""

echo "Withdraw operator stake (when pool inactive):"
echo "tonos-cli $NETWORK call $POOL_OPERATOR_ADDR \\"
echo "  withdrawStake \\"
echo "  '{\"amount\":50000000000}' \\"
echo "  --sign $OPERATOR_KEY \\"
echo "  --abi contracts/pool_operator.abi.json"
echo ""

echo "=========================================="
echo "Examples complete!"
echo "=========================================="
echo ""
echo "Note: Replace placeholder addresses and adjust values as needed."
echo "For testnet deployment, get free TON from: https://t.me/testgiver_ton_bot"
echo ""
