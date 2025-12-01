# Smart Contract Specifications

## Overview

This document provides detailed specifications for the three core smart contracts that enable GPU resource pooling on the Cocoon network: PoolOperator, RewardDistribution, and ParticipantRegistry.

## Table of Contents

1. [PoolOperator Contract](#pooloperator-contract)
2. [RewardDistribution Contract](#rewarddistribution-contract)
3. [ParticipantRegistry Contract](#participantregistry-contract)
4. [Contract Interactions](#contract-interactions)
5. [Security Model](#security-model)
6. [Upgrade Strategy](#upgrade-strategy)

## PoolOperator Contract

### Purpose

The PoolOperator contract serves as the central governance and registration point for a GPU resource pool. It acts as the interface between the pool and the Cocoon network, managing pool-wide configuration and participant access control.

### State Variables

```func
;; Core State
global slice pool_owner_address;      ;; Pool operator's wallet
global int pool_id;                   ;; Unique pool identifier
global slice cocoon_root_address;     ;; Reference to Cocoon root contract
global int pool_state;                ;; 0=Active, 1=Paused, 2=Closed

;; Contract References
global slice participant_registry_address;
global slice reward_distribution_address;

;; Pool Configuration
global int pool_fee_bps;              ;; Pool operator fee (basis points, max 10000)
global int min_participant_stake;     ;; Minimum stake in nanoTON
global int max_participants;          ;; Maximum pool size
global int registration_open;         ;; 0=Closed, 1=Open

;; Pool Metadata
global cell pool_metadata;            ;; Name, description, URL
global int total_pooled_stake;        ;; Sum of all participant stakes
global int active_participant_count;
global int total_tasks_completed;
global int total_tokens_processed;

;; Versioning and Upgrades
global int contract_version;
global cell params;                   ;; Packed parameters for future extensibility
```

### Data Structures

#### pool_metadata Cell Structure
```func
{
  pool_name: string           ;; Max 64 chars
  pool_description: string    ;; Max 256 chars
  pool_website: string        ;; URL
  operator_contact: string    ;; Email or telegram
  created_at: int
  updated_at: int
}
```

#### params Cell Structure
```func
{
  min_uptime_percentage: int        ;; Minimum uptime for eligibility (0-100)
  heartbeat_timeout_sec: int        ;; Seconds before worker considered offline
  slash_percentage: int             ;; Penalty for violations (0-10000 bps)
  withdrawal_delay_sec: int         ;; Timelock for stake withdrawal
  upgrade_timelock_sec: int         ;; Delay for parameter changes
  emergency_shutdown_enabled: int   ;; 0=No, 1=Yes
}
```

### Operations

#### Administrative Operations

```func
;; op::pool_init
;; Initialize pool with configuration
;; Sender: pool_owner_address
recv_internal(msg_value, in_msg_body) {
  int op = in_msg_body~load_uint(32);
  int query_id = in_msg_body~load_uint(64);

  if (op == op::pool_init) {
    slice cocoon_root = in_msg_body~load_msg_addr();
    slice participant_registry = in_msg_body~load_msg_addr();
    slice reward_distribution = in_msg_body~load_msg_addr();
    int pool_fee = in_msg_body~load_uint(16);
    int min_stake = in_msg_body~load_coins();
    cell metadata = in_msg_body~load_ref();

    throw_unless(error::already_initialized, pool_state == -1);
    throw_unless(error::invalid_fee, pool_fee <= 10000);
    throw_unless(error::unauthorized, equal_slices(sender, pool_owner_address));

    cocoon_root_address = cocoon_root;
    participant_registry_address = participant_registry;
    reward_distribution_address = reward_distribution;
    pool_fee_bps = pool_fee;
    min_participant_stake = min_stake;
    pool_metadata = metadata;
    pool_state = 0; ;; Active

    save_data();
    forward_excesses(sender, query_id);
  }
}
```

```func
;; op::pool_update_params
;; Update pool parameters (fee, minimum stake, etc.)
;; Sender: pool_owner_address
;; Includes timelock for security
if (op == op::pool_update_params) {
  int new_pool_fee = in_msg_body~load_uint(16);
  int new_min_stake = in_msg_body~load_coins();
  int new_max_participants = in_msg_body~load_uint(32);

  throw_unless(error::unauthorized, equal_slices(sender, pool_owner_address));
  throw_unless(error::invalid_fee, new_pool_fee <= 10000);
  throw_unless(error::pool_not_active, pool_state == 0);

  ;; TODO: Implement timelock for parameter changes
  ;; For now, apply immediately
  pool_fee_bps = new_pool_fee;
  min_participant_stake = new_min_stake;
  max_participants = new_max_participants;

  save_data();
  emit_event(event::params_updated, query_id);
  forward_excesses(sender, query_id);
}
```

```func
;; op::pool_pause
;; Pause pool operations (emergency)
;; Sender: pool_owner_address
if (op == op::pool_pause) {
  throw_unless(error::unauthorized, equal_slices(sender, pool_owner_address));
  throw_unless(error::already_paused, pool_state == 0);

  pool_state = 1; ;; Paused

  ;; Notify participant registry to stop accepting new contributions
  send_message(participant_registry_address, op::pause_contributions, query_id);

  save_data();
  emit_event(event::pool_paused, query_id);
  forward_excesses(sender, query_id);
}
```

```func
;; op::pool_resume
;; Resume pool operations after pause
;; Sender: pool_owner_address
if (op == op::pool_resume) {
  throw_unless(error::unauthorized, equal_slices(sender, pool_owner_address));
  throw_unless(error::not_paused, pool_state == 1);

  pool_state = 0; ;; Active

  send_message(participant_registry_address, op::resume_contributions, query_id);

  save_data();
  emit_event(event::pool_resumed, query_id);
  forward_excesses(sender, query_id);
}
```

#### Participant Management

```func
;; op::pool_register_participant
;; Register new participant in the pool
;; Sender: participant address
;; Value: Must include minimum stake + gas
if (op == op::pool_register_participant) {
  slice participant_address = sender;
  cell gpu_specification = in_msg_body~load_ref();
  int stake_amount = in_msg_body~load_coins();

  throw_unless(error::pool_not_active, pool_state == 0);
  throw_unless(error::registration_closed, registration_open == 1);
  throw_unless(error::insufficient_stake, stake_amount >= min_participant_stake);
  throw_unless(error::pool_full, active_participant_count < max_participants);
  throw_unless(error::low_msg_value, msg_value >= stake_amount + COMMISSION_ESTIMATE);

  ;; Forward registration to ParticipantRegistry
  builder msg = begin_cell()
    .store_uint(op::registry_add_participant, 32)
    .store_uint(query_id, 64)
    .store_slice(participant_address)
    .store_ref(gpu_specification)
    .store_coins(stake_amount);

  send_raw_message(create_msg(participant_registry_address, stake_amount + 1, msg),
                   SEND_MODE_PAY_FEES_SEPARATELY);

  active_participant_count += 1;
  total_pooled_stake += stake_amount;

  save_data();
  emit_event(event::participant_registered, query_id, participant_address);
  forward_excesses(sender, query_id);
}
```

```func
;; op::pool_remove_participant
;; Remove participant from pool (owner-initiated or participant-initiated)
;; Sender: pool_owner_address OR participant themselves
if (op == op::pool_remove_participant) {
  slice participant_address = in_msg_body~load_msg_addr();
  int force_remove = in_msg_body~load_uint(1);

  int is_owner = equal_slices(sender, pool_owner_address);
  int is_self = equal_slices(sender, participant_address);

  throw_unless(error::unauthorized, is_owner | is_self);
  throw_if(error::cannot_force_remove, force_remove & ~ is_owner);

  ;; Forward removal to ParticipantRegistry
  ;; Registry will handle stake return after withdrawal delay
  send_message(participant_registry_address, op::registry_remove_participant,
               query_id, participant_address);

  active_participant_count -= 1;
  ;; total_pooled_stake updated when registry confirms

  save_data();
  emit_event(event::participant_removed, query_id, participant_address);
  forward_excesses(sender, query_id);
}
```

#### Reporting and Statistics

```func
;; op::pool_update_statistics
;; Update pool-wide statistics (called by backend)
;; Sender: pool_owner_address or authorized reporter
if (op == op::pool_update_statistics) {
  int tasks_completed = in_msg_body~load_uint(64);
  int tokens_processed = in_msg_body~load_uint(64);

  throw_unless(error::unauthorized, equal_slices(sender, pool_owner_address));

  total_tasks_completed += tasks_completed;
  total_tokens_processed += tokens_processed;

  save_data();
  forward_excesses(sender, query_id);
}
```

#### Fee Management

```func
;; op::pool_withdraw_fees
;; Withdraw accumulated operator fees
;; Sender: pool_owner_address
if (op == op::pool_withdraw_fees) {
  throw_unless(error::unauthorized, equal_slices(sender, pool_owner_address));

  ;; Query accumulated fees from RewardDistribution contract
  ;; RewardDistribution will send fees back
  send_message(reward_distribution_address, op::distribution_withdraw_operator_fees,
               query_id, pool_owner_address);

  forward_excesses(sender, query_id);
}
```

### Get Methods

```func
;; Get pool configuration and status
(int, slice, slice, int, int, int, int, int) get_pool_info() method_id {
  return (
    pool_id,
    pool_owner_address,
    cocoon_root_address,
    pool_state,
    pool_fee_bps,
    min_participant_stake,
    active_participant_count,
    total_pooled_stake
  );
}

;; Get pool statistics
(int, int, int) get_pool_statistics() method_id {
  return (
    total_tasks_completed,
    total_tokens_processed,
    contract_version
  );
}

;; Get contract addresses
(slice, slice) get_contract_references() method_id {
  return (
    participant_registry_address,
    reward_distribution_address
  );
}

;; Check if participant can register
int can_register_participant() method_id {
  return (pool_state == 0) &
         (registration_open == 1) &
         (active_participant_count < max_participants);
}
```

## RewardDistribution Contract

### Purpose

The RewardDistribution contract automates the collection and distribution of TON rewards earned by the pool. It receives payments from the Cocoon network, calculates proportional distributions based on participant contributions, and executes payouts.

### State Variables

```func
;; Core State
global slice pool_operator_address;
global slice participant_registry_address;
global int current_epoch;
global int epoch_duration_sec;          ;; Default: 604800 (7 days)

;; Reward Tracking
global int total_rewards_received;
global int total_rewards_distributed;
global int total_operator_fees_collected;
global int pending_operator_fees;

;; Epoch Management
global cell epoch_data;                 ;; Dict: epoch_id -> EpochInfo
global cell distribution_queue;         ;; Queue of pending distributions
global int last_distribution_timestamp;

;; Configuration
global int pool_fee_bps;                ;; Synced from PoolOperator
global int auto_distribute_enabled;     ;; 0=Manual, 1=Auto
global int min_distribution_amount;     ;; Minimum to trigger distribution

;; State
global cell params;
```

### Data Structures

#### EpochInfo Structure
```func
{
  epoch_id: int
  start_timestamp: int
  end_timestamp: int
  total_rewards: int
  operator_fee: int
  participant_rewards: int
  distribution_status: int           ;; 0=Pending, 1=InProgress, 2=Completed
  participants_paid: int
  total_participants: int
  distribution_merkle_root: int      ;; For verification
}
```

#### DistributionRecord Structure
```func
{
  participant_address: slice
  epoch_id: int
  contribution_score: int
  reward_amount: int
  distributed: int                   ;; 0=Pending, 1=Completed
  distribution_timestamp: int
}
```

### Operations

#### Reward Reception

```func
;; op::distribution_receive_payment
;; Receive rewards from Cocoon network or external sources
;; Sender: Any (but typically Cocoon proxy or pool gateway)
if (op == op::distribution_receive_payment) {
  int payment_amount = msg_value - COMMISSION_ESTIMATE;

  throw_unless(error::payment_too_small, payment_amount > 0);

  ;; Add to current epoch rewards
  total_rewards_received += payment_amount;

  ;; Update current epoch
  (slice epoch_info_slice, int found) = epoch_data.udict_get?(64, current_epoch);
  throw_unless(error::epoch_not_found, found);

  EpochInfo epoch = unpack_epoch_info(epoch_info_slice);
  epoch.total_rewards += payment_amount;

  epoch_data~udict_set(64, current_epoch, pack_epoch_info(epoch));

  ;; Check if auto-distribution threshold reached
  if (auto_distribute_enabled & (epoch.total_rewards >= min_distribution_amount)) {
    ;; Trigger distribution calculation
    calculate_distribution(current_epoch);
  }

  save_data();
  emit_event(event::payment_received, payment_amount, sender);
  forward_excesses(sender, query_id);
}
```

```func
;; Plain TON transfers (no op code)
if (op == 0) {
  ;; Treat as reward payment
  int payment_amount = msg_value - COMMISSION_ESTIMATE;

  if (payment_amount > 0) {
    total_rewards_received += payment_amount;

    ;; Add to current epoch
    ;; (implementation similar to above)
  }

  save_data();
  return ();
}
```

#### Epoch Management

```func
;; op::distribution_finalize_epoch
;; Close current epoch and start new one
;; Sender: pool_operator_address or automated trigger
if (op == op::distribution_finalize_epoch) {
  throw_unless(error::unauthorized, equal_slices(sender, pool_operator_address));

  ;; Check if current epoch duration passed
  int current_time = now();
  (slice epoch_slice, int found) = epoch_data.udict_get?(64, current_epoch);
  throw_unless(error::epoch_not_found, found);

  EpochInfo epoch = unpack_epoch_info(epoch_slice);
  throw_unless(error::epoch_not_expired, current_time >= epoch.end_timestamp);

  ;; Finalize current epoch
  epoch.distribution_status = 0; ;; Mark as pending distribution
  epoch_data~udict_set(64, current_epoch, pack_epoch_info(epoch));

  ;; Create new epoch
  current_epoch += 1;
  EpochInfo new_epoch = {
    epoch_id: current_epoch,
    start_timestamp: current_time,
    end_timestamp: current_time + epoch_duration_sec,
    total_rewards: 0,
    operator_fee: 0,
    participant_rewards: 0,
    distribution_status: -1,  ;; Active
    participants_paid: 0,
    total_participants: 0,
    distribution_merkle_root: 0
  };
  epoch_data~udict_set(64, current_epoch, pack_epoch_info(new_epoch));

  save_data();
  emit_event(event::epoch_finalized, epoch.epoch_id, epoch.total_rewards);
  forward_excesses(sender, query_id);
}
```

#### Distribution Calculation

```func
;; op::distribution_calculate
;; Calculate reward distribution for an epoch
;; Sender: pool_operator_address
if (op == op::distribution_calculate) {
  int epoch_id = in_msg_body~load_uint(64);

  throw_unless(error::unauthorized, equal_slices(sender, pool_operator_address));

  ;; Get epoch info
  (slice epoch_slice, int found) = epoch_data.udict_get?(64, epoch_id);
  throw_unless(error::epoch_not_found, found);

  EpochInfo epoch = unpack_epoch_info(epoch_slice);
  throw_unless(error::already_calculated, epoch.distribution_status == 0);

  ;; Calculate operator fee
  int operator_fee = (epoch.total_rewards * pool_fee_bps) / 10000;
  int participant_pool = epoch.total_rewards - operator_fee;

  ;; Query participant contributions from registry
  ;; This requires off-chain calculation and submission of distribution list
  ;; Or on-chain iteration (gas expensive for large pools)

  epoch.operator_fee = operator_fee;
  epoch.participant_rewards = participant_pool;
  epoch.distribution_status = 1; ;; In progress

  pending_operator_fees += operator_fee;

  epoch_data~udict_set(64, epoch_id, pack_epoch_info(epoch));

  save_data();
  emit_event(event::distribution_calculated, epoch_id, participant_pool);
  forward_excesses(sender, query_id);
}
```

#### Distribution Execution

```func
;; op::distribution_execute_batch
;; Execute reward distribution for a batch of participants
;; Sender: pool_operator_address
;; Note: Uses batch processing to avoid gas limits
if (op == op::distribution_execute_batch) {
  int epoch_id = in_msg_body~load_uint(64);
  cell distribution_list = in_msg_body~load_ref();  ;; List of (address, amount) pairs

  throw_unless(error::unauthorized, equal_slices(sender, pool_operator_address));

  ;; Get epoch info
  (slice epoch_slice, int found) = epoch_data.udict_get?(64, epoch_id);
  throw_unless(error::epoch_not_found, found);

  EpochInfo epoch = unpack_epoch_info(epoch_slice);
  throw_unless(error::invalid_state, epoch.distribution_status == 1);

  ;; Parse distribution list
  slice list_slice = distribution_list.begin_parse();
  int count = list_slice~load_uint(16);
  int total_amount = 0;

  repeat (count) {
    slice participant = list_slice~load_msg_addr();
    int amount = list_slice~load_coins();

    ;; Send reward to participant
    builder msg = begin_cell()
      .store_uint(op::payout, 32)
      .store_uint(query_id, 64)
      .store_uint(epoch_id, 64);

    send_raw_message(create_msg(participant, amount, msg),
                     SEND_MODE_PAY_FEES_SEPARATELY);

    total_amount += amount;
    epoch.participants_paid += 1;

    emit_event(event::reward_paid, participant, amount);
  }

  total_rewards_distributed += total_amount;

  ;; Check if all participants paid
  if (epoch.participants_paid >= epoch.total_participants) {
    epoch.distribution_status = 2; ;; Completed
    emit_event(event::epoch_distributed, epoch_id, total_amount);
  }

  epoch_data~udict_set(64, epoch_id, pack_epoch_info(epoch));

  save_data();
  forward_excesses(sender, query_id);
}
```

```func
;; op::distribution_claim_rewards
;; Participant claims their unclaimed rewards
;; Sender: participant address
if (op == op::distribution_claim_rewards) {
  slice participant = sender;

  ;; Query unclaimed rewards for participant
  ;; This requires maintaining a separate dict of participant -> unclaimed amounts
  ;; Or iterating through epochs (expensive)

  ;; For efficiency, use off-chain indexing and on-chain verification
  int epoch_id = in_msg_body~load_uint(64);
  int claimed_amount = in_msg_body~load_coins();
  cell merkle_proof = in_msg_body~load_ref();

  ;; Verify merkle proof
  (slice epoch_slice, int found) = epoch_data.udict_get?(64, epoch_id);
  throw_unless(error::epoch_not_found, found);

  EpochInfo epoch = unpack_epoch_info(epoch_slice);
  int merkle_root = epoch.distribution_merkle_root;

  throw_unless(error::invalid_proof,
               verify_merkle_proof(merkle_proof, merkle_root, participant, claimed_amount));

  ;; Send reward
  builder msg = begin_cell()
    .store_uint(op::payout, 32)
    .store_uint(query_id, 64)
    .store_uint(epoch_id, 64);

  send_raw_message(create_msg(participant, claimed_amount, msg),
                   SEND_MODE_CARRY_ALL_BALANCE);

  total_rewards_distributed += claimed_amount;

  save_data();
  emit_event(event::reward_claimed, participant, claimed_amount);
}
```

#### Operator Fee Withdrawal

```func
;; op::distribution_withdraw_operator_fees
;; Withdraw accumulated operator fees
;; Sender: pool_operator_address
if (op == op::distribution_withdraw_operator_fees) {
  slice recipient = in_msg_body~load_msg_addr();

  throw_unless(error::unauthorized, equal_slices(sender, pool_operator_address));
  throw_unless(error::no_fees_available, pending_operator_fees > 0);

  int withdraw_amount = pending_operator_fees;
  pending_operator_fees = 0;
  total_operator_fees_collected += withdraw_amount;

  ;; Send fees to operator
  builder msg = begin_cell()
    .store_uint(op::payout, 32)
    .store_uint(query_id, 64);

  send_raw_message(create_msg(recipient, withdraw_amount, msg),
                   SEND_MODE_PAY_FEES_SEPARATELY);

  save_data();
  emit_event(event::operator_fees_withdrawn, withdraw_amount);
  forward_excesses(sender, query_id);
}
```

### Get Methods

```func
;; Get current epoch information
(int, int, int, int, int) get_current_epoch_info() method_id {
  (slice epoch_slice, int found) = epoch_data.udict_get?(64, current_epoch);
  throw_unless(error::epoch_not_found, found);

  EpochInfo epoch = unpack_epoch_info(epoch_slice);
  return (
    epoch.epoch_id,
    epoch.start_timestamp,
    epoch.end_timestamp,
    epoch.total_rewards,
    epoch.distribution_status
  );
}

;; Get distribution statistics
(int, int, int, int) get_distribution_stats() method_id {
  return (
    total_rewards_received,
    total_rewards_distributed,
    total_operator_fees_collected,
    pending_operator_fees
  );
}

;; Get epoch data
(int, int, int, int, int, int) get_epoch_data(int epoch_id) method_id {
  (slice epoch_slice, int found) = epoch_data.udict_get?(64, epoch_id);
  throw_unless(error::epoch_not_found, found);

  EpochInfo epoch = unpack_epoch_info(epoch_slice);
  return (
    epoch.total_rewards,
    epoch.operator_fee,
    epoch.participant_rewards,
    epoch.distribution_status,
    epoch.participants_paid,
    epoch.total_participants
  );
}
```

## ParticipantRegistry Contract

### Purpose

The ParticipantRegistry contract maintains a comprehensive record of all pool participants, their hardware specifications, stake amounts, contribution metrics, and reputation scores. It serves as the source of truth for reward distribution calculations.

### State Variables

```func
;; Core State
global slice pool_operator_address;
global cell participants;              ;; Dict: participant_address -> ParticipantInfo
global int participant_count;
global int total_stake;

;; Contribution Tracking
global cell contribution_data;         ;; Dict: (participant_address, epoch) -> ContributionInfo
global int current_epoch;

;; Configuration
global int min_stake_amount;
global int withdrawal_delay_sec;       ;; Timelock for withdrawals (default: 7 days)
global int min_uptime_percentage;      ;; Minimum uptime for rewards eligibility
global int slash_percentage_bps;       ;; Penalty amount for violations

;; State
global int registry_paused;            ;; 0=Active, 1=Paused
global cell params;
```

### Data Structures

#### ParticipantInfo Structure
```func
{
  owner_address: slice
  worker_contract_address: slice    ;; Cocoon worker contract
  gpu_specification_hash: int       ;; Hash of GPU spec JSON
  gpu_count: int

  stake_amount: int
  join_timestamp: int
  status: int                       ;; 0=Active, 1=Inactive, 2=Suspended, 3=Withdrawing

  total_contribution_score: int     ;; Cumulative weighted contribution
  total_uptime_seconds: int
  total_tasks_completed: int
  total_tokens_processed: int

  reputation_score: int             ;; 0-1000, affects reward weight
  last_heartbeat_timestamp: int
  withdrawal_request_timestamp: int  ;; For timelock
  pending_withdrawal_amount: int
}
```

#### ContributionInfo Structure
```func
{
  participant_address: slice
  epoch_id: int

  tasks_completed: int
  tokens_processed: int
  uptime_seconds: int
  uptime_percentage: int            ;; Calculated against epoch duration

  contribution_score: int           ;; Weighted metric for this epoch
  quality_score: int                ;; Based on error rates, latency

  rewards_eligible: int             ;; 0=No, 1=Yes (based on min uptime)
  slashed_amount: int               ;; Any penalties applied

  last_updated_timestamp: int
}
```

### Operations

#### Participant Registration

```func
;; op::registry_add_participant
;; Add new participant to registry
;; Sender: PoolOperator contract
if (op == op::registry_add_participant) {
  throw_unless(error::unauthorized, equal_slices(sender, pool_operator_address));
  throw_unless(error::paused, registry_paused == 0);

  slice participant_address = in_msg_body~load_msg_addr();
  cell gpu_spec = in_msg_body~load_ref();
  int stake_amount = in_msg_body~load_coins();

  ;; Check if participant already exists
  (slice existing, int found) = participants.udict_get?(256, hash_slice(participant_address));
  throw_if(error::already_registered, found);

  throw_unless(error::insufficient_stake, stake_amount >= min_stake_amount);

  ;; Parse GPU specification
  slice gpu_slice = gpu_spec.begin_parse();
  int gpu_model_hash = gpu_slice~load_uint(256);
  int gpu_count = gpu_slice~load_uint(8);
  gpu_slice.end_parse();

  ;; Create participant info
  ParticipantInfo info = {
    owner_address: participant_address,
    worker_contract_address: null_addr(),  ;; Set later when worker deploys
    gpu_specification_hash: gpu_model_hash,
    gpu_count: gpu_count,
    stake_amount: stake_amount,
    join_timestamp: now(),
    status: 0,  ;; Active
    total_contribution_score: 0,
    total_uptime_seconds: 0,
    total_tasks_completed: 0,
    total_tokens_processed: 0,
    reputation_score: 500,  ;; Start at 50% (neutral)
    last_heartbeat_timestamp: now(),
    withdrawal_request_timestamp: 0,
    pending_withdrawal_amount: 0
  };

  participants~udict_set(256, hash_slice(participant_address), pack_participant_info(info));
  participant_count += 1;
  total_stake += stake_amount;

  save_data();
  emit_event(event::participant_added, participant_address, stake_amount);
  forward_excesses(sender, query_id);
}
```

```func
;; op::registry_update_worker_address
;; Update worker contract address for participant
;; Sender: participant or pool_operator
if (op == op::registry_update_worker_address) {
  slice participant_address = in_msg_body~load_msg_addr();
  slice worker_address = in_msg_body~load_msg_addr();

  int is_operator = equal_slices(sender, pool_operator_address);
  int is_self = equal_slices(sender, participant_address);
  throw_unless(error::unauthorized, is_operator | is_self);

  ;; Get participant info
  (slice info_slice, int found) = participants.udict_get?(256, hash_slice(participant_address));
  throw_unless(error::not_found, found);

  ParticipantInfo info = unpack_participant_info(info_slice);
  info.worker_contract_address = worker_address;

  participants~udict_set(256, hash_slice(participant_address), pack_participant_info(info));

  save_data();
  emit_event(event::worker_address_updated, participant_address);
  forward_excesses(sender, query_id);
}
```

#### Contribution Tracking

```func
;; op::registry_update_contribution
;; Update participant contribution metrics
;; Sender: pool_operator_address (from backend tracker)
if (op == op::registry_update_contribution) {
  throw_unless(error::unauthorized, equal_slices(sender, pool_operator_address));

  slice participant_address = in_msg_body~load_msg_addr();
  int epoch_id = in_msg_body~load_uint(64);
  int tasks_completed = in_msg_body~load_uint(64);
  int tokens_processed = in_msg_body~load_uint(64);
  int uptime_seconds = in_msg_body~load_uint(32);
  int quality_score = in_msg_body~load_uint(16);  ;; 0-1000

  ;; Get participant info
  (slice info_slice, int found) = participants.udict_get?(256, hash_slice(participant_address));
  throw_unless(error::not_found, found);

  ParticipantInfo info = unpack_participant_info(info_slice);

  ;; Update totals
  info.total_tasks_completed += tasks_completed;
  info.total_tokens_processed += tokens_processed;
  info.total_uptime_seconds += uptime_seconds;
  info.last_heartbeat_timestamp = now();

  ;; Get or create contribution record for this epoch
  int contrib_key = (hash_slice(participant_address) << 64) | epoch_id;
  (slice contrib_slice, int contrib_found) = contribution_data.udict_get?(320, contrib_key);

  ContributionInfo contrib;
  if (contrib_found) {
    contrib = unpack_contribution_info(contrib_slice);
  } else {
    contrib = {
      participant_address: participant_address,
      epoch_id: epoch_id,
      tasks_completed: 0,
      tokens_processed: 0,
      uptime_seconds: 0,
      uptime_percentage: 0,
      contribution_score: 0,
      quality_score: 0,
      rewards_eligible: 0,
      slashed_amount: 0,
      last_updated_timestamp: now()
    };
  }

  ;; Update contribution info
  contrib.tasks_completed += tasks_completed;
  contrib.tokens_processed += tokens_processed;
  contrib.uptime_seconds += uptime_seconds;
  contrib.quality_score = quality_score;  ;; Latest value
  contrib.last_updated_timestamp = now();

  ;; Calculate contribution score (weighted metric)
  contrib.contribution_score = calculate_contribution_score(
    contrib.tokens_processed,
    contrib.uptime_seconds,
    contrib.tasks_completed,
    quality_score,
    info.reputation_score
  );

  info.total_contribution_score += contrib.contribution_score;

  ;; Save updated data
  contribution_data~udict_set(320, contrib_key, pack_contribution_info(contrib));
  participants~udict_set(256, hash_slice(participant_address), pack_participant_info(info));

  save_data();
  forward_excesses(sender, query_id);
}
```

```func
;; Helper: Calculate contribution score
int calculate_contribution_score(int tokens, int uptime, int tasks, int quality, int reputation) inline {
  ;; Weights
  int w_tokens = 5000;      ;; 50%
  int w_uptime = 2000;      ;; 20%
  int w_tasks = 2000;       ;; 20%
  int w_quality = 1000;     ;; 10%

  ;; Normalize and weight
  ;; (This is simplified; real implementation would normalize based on pool-wide metrics)
  int score = (
    (tokens * w_tokens / 1000000) +
    (uptime * w_uptime / 86400) +
    (tasks * w_tasks / 100) +
    (quality * w_quality / 1000)
  );

  ;; Apply reputation multiplier
  score = (score * reputation) / 1000;

  return score;
}
```

#### Stake Management

```func
;; op::registry_increase_stake
;; Participant increases their stake
;; Sender: participant address
if (op == op::registry_increase_stake) {
  slice participant_address = sender;
  int additional_stake = msg_value - COMMISSION_ESTIMATE;

  throw_unless(error::insufficient_value, additional_stake > 0);

  ;; Get participant info
  (slice info_slice, int found) = participants.udict_get?(256, hash_slice(participant_address));
  throw_unless(error::not_found, found);

  ParticipantInfo info = unpack_participant_info(info_slice);
  info.stake_amount += additional_stake;

  participants~udict_set(256, hash_slice(participant_address), pack_participant_info(info));
  total_stake += additional_stake;

  save_data();
  emit_event(event::stake_increased, participant_address, additional_stake);
  forward_excesses(sender, query_id);
}
```

```func
;; op::registry_request_withdrawal
;; Request to withdraw stake (initiates timelock)
;; Sender: participant address
if (op == op::registry_request_withdrawal) {
  slice participant_address = sender;
  int withdrawal_amount = in_msg_body~load_coins();

  ;; Get participant info
  (slice info_slice, int found) = participants.udict_get?(256, hash_slice(participant_address));
  throw_unless(error::not_found, found);

  ParticipantInfo info = unpack_participant_info(info_slice);
  throw_unless(error::insufficient_stake, withdrawal_amount <= info.stake_amount);
  throw_unless(error::withdrawal_pending, info.pending_withdrawal_amount == 0);

  ;; Initiate timelock
  info.status = 3;  ;; Withdrawing
  info.withdrawal_request_timestamp = now();
  info.pending_withdrawal_amount = withdrawal_amount;

  ;; If full withdrawal, mark as inactive
  if (withdrawal_amount == info.stake_amount) {
    info.status = 1;  ;; Inactive
  }

  participants~udict_set(256, hash_slice(participant_address), pack_participant_info(info));

  save_data();
  emit_event(event::withdrawal_requested, participant_address, withdrawal_amount);
  forward_excesses(sender, query_id);
}
```

```func
;; op::registry_complete_withdrawal
;; Complete withdrawal after timelock expires
;; Sender: participant address
if (op == op::registry_complete_withdrawal) {
  slice participant_address = sender;

  ;; Get participant info
  (slice info_slice, int found) = participants.udict_get?(256, hash_slice(participant_address));
  throw_unless(error::not_found, found);

  ParticipantInfo info = unpack_participant_info(info_slice);
  throw_unless(error::no_pending_withdrawal, info.pending_withdrawal_amount > 0);

  ;; Check timelock
  int current_time = now();
  int unlock_time = info.withdrawal_request_timestamp + withdrawal_delay_sec;
  throw_unless(error::timelock_active, current_time >= unlock_time);

  int withdrawal_amount = info.pending_withdrawal_amount;

  ;; Update state
  info.stake_amount -= withdrawal_amount;
  info.pending_withdrawal_amount = 0;
  info.withdrawal_request_timestamp = 0;

  if (info.stake_amount < min_stake_amount) {
    ;; Full withdrawal, remove participant
    participants~udict_delete?(256, hash_slice(participant_address));
    participant_count -= 1;
  } else {
    ;; Partial withdrawal, restore active status
    info.status = 0;  ;; Active
    participants~udict_set(256, hash_slice(participant_address), pack_participant_info(info));
  }

  total_stake -= withdrawal_amount;

  ;; Send funds to participant
  builder msg = begin_cell()
    .store_uint(op::payout, 32)
    .store_uint(query_id, 64);

  send_raw_message(create_msg(participant_address, withdrawal_amount, msg),
                   SEND_MODE_PAY_FEES_SEPARATELY);

  save_data();
  emit_event(event::withdrawal_completed, participant_address, withdrawal_amount);
}
```

#### Reputation and Slashing

```func
;; op::registry_update_reputation
;; Update participant reputation score
;; Sender: pool_operator_address
if (op == op::registry_update_reputation) {
  throw_unless(error::unauthorized, equal_slices(sender, pool_operator_address));

  slice participant_address = in_msg_body~load_msg_addr();
  int new_reputation = in_msg_body~load_uint(16);  ;; 0-1000

  throw_unless(error::invalid_reputation, (new_reputation >= 0) & (new_reputation <= 1000));

  ;; Get participant info
  (slice info_slice, int found) = participants.udict_get?(256, hash_slice(participant_address));
  throw_unless(error::not_found, found);

  ParticipantInfo info = unpack_participant_info(info_slice);
  int old_reputation = info.reputation_score;
  info.reputation_score = new_reputation;

  participants~udict_set(256, hash_slice(participant_address), pack_participant_info(info));

  save_data();
  emit_event(event::reputation_updated, participant_address, new_reputation);
  forward_excesses(sender, query_id);
}
```

```func
;; op::registry_slash_participant
;; Penalize participant for violations
;; Sender: pool_operator_address
if (op == op::registry_slash_participant) {
  throw_unless(error::unauthorized, equal_slices(sender, pool_operator_address));

  slice participant_address = in_msg_body~load_msg_addr();
  int slash_amount = in_msg_body~load_coins();
  int reason_code = in_msg_body~load_uint(16);

  ;; Get participant info
  (slice info_slice, int found) = participants.udict_get?(256, hash_slice(participant_address));
  throw_unless(error::not_found, found);

  ParticipantInfo info = unpack_participant_info(info_slice);

  ;; Calculate slash amount if not specified
  if (slash_amount == 0) {
    slash_amount = (info.stake_amount * slash_percentage_bps) / 10000;
  }

  throw_unless(error::excessive_slash, slash_amount <= info.stake_amount);

  ;; Apply slash
  info.stake_amount -= slash_amount;
  total_stake -= slash_amount;

  ;; Lower reputation
  info.reputation_score = max(0, info.reputation_score - 100);

  ;; If stake below minimum, suspend participant
  if (info.stake_amount < min_stake_amount) {
    info.status = 2;  ;; Suspended
  }

  participants~udict_set(256, hash_slice(participant_address), pack_participant_info(info));

  save_data();
  emit_event(event::participant_slashed, participant_address, slash_amount, reason_code);
  forward_excesses(sender, query_id);
}
```

### Get Methods

```func
;; Get participant information
(slice, int, int, int, int, int, int, int, int) get_participant_info(slice address) method_id {
  (slice info_slice, int found) = participants.udict_get?(256, hash_slice(address));
  throw_unless(error::not_found, found);

  ParticipantInfo info = unpack_participant_info(info_slice);
  return (
    info.worker_contract_address,
    info.stake_amount,
    info.status,
    info.total_contribution_score,
    info.total_tasks_completed,
    info.total_tokens_processed,
    info.total_uptime_seconds,
    info.reputation_score,
    info.last_heartbeat_timestamp
  );
}

;; Get contribution info for epoch
(int, int, int, int, int, int) get_contribution_info(slice address, int epoch_id) method_id {
  int contrib_key = (hash_slice(address) << 64) | epoch_id;
  (slice contrib_slice, int found) = contribution_data.udict_get?(320, contrib_key);
  throw_unless(error::not_found, found);

  ContributionInfo contrib = unpack_contribution_info(contrib_slice);
  return (
    contrib.tasks_completed,
    contrib.tokens_processed,
    contrib.uptime_seconds,
    contrib.contribution_score,
    contrib.quality_score,
    contrib.rewards_eligible
  );
}

;; Get registry statistics
(int, int) get_registry_stats() method_id {
  return (
    participant_count,
    total_stake
  );
}

;; Check if participant exists and is active
int is_participant_active(slice address) method_id {
  (slice info_slice, int found) = participants.udict_get?(256, hash_slice(address));
  if (~ found) {
    return 0;
  }

  ParticipantInfo info = unpack_participant_info(info_slice);
  return (info.status == 0) & (info.stake_amount >= min_stake_amount);
}
```

## Contract Interactions

### Registration Flow

```
Participant → PoolOperator.pool_register_participant(gpu_spec, stake)
                     ↓
      PoolOperator → ParticipantRegistry.registry_add_participant()
                     ↓
      ParticipantRegistry stores participant info
                     ↓
      Emit event → Backend deploys worker
                     ↓
      Backend → ParticipantRegistry.registry_update_worker_address()
```

### Contribution Tracking Flow

```
Worker completes task → Backend Contribution Tracker
                              ↓
      Aggregates metrics (hourly/daily)
                              ↓
      Backend → ParticipantRegistry.registry_update_contribution()
                              ↓
      Updates contribution_data for current epoch
```

### Reward Distribution Flow

```
Epoch ends → Backend → RewardDistribution.distribution_finalize_epoch()
                              ↓
      Backend → RewardDistribution.distribution_calculate()
                              ↓
      Queries ParticipantRegistry for contribution scores
                              ↓
      Off-chain calculation of reward shares
                              ↓
      Backend → RewardDistribution.distribution_execute_batch()
                              ↓
      Transfers TON to participants
```

## Security Model

### Access Control

1. **PoolOperator Contract**
   - Owner-only operations: Parameter updates, participant removal, fee withdrawal
   - Participant operations: Self-registration, self-removal
   - Public read: Get methods for transparency

2. **RewardDistribution Contract**
   - Operator-only: Epoch management, distribution execution, fee withdrawal
   - Public: Receive payments, claim rewards
   - Automated: Distribution triggers (if enabled)

3. **ParticipantRegistry Contract**
   - Operator-only: Contribution updates, reputation management, slashing
   - Participant operations: Stake management, worker address updates
   - Pool contract: Add/remove participants

### Economic Security

1. **Minimum Stake Requirement**
   - Prevents spam registrations
   - Ensures skin-in-the-game for participants
   - Default: 100 TON minimum

2. **Timelock Mechanisms**
   - Withdrawal delay: 7 days
   - Parameter change delay: 3 days
   - Prevents rapid exploitation

3. **Slashing Conditions**
   - Extended downtime (>24h without heartbeat)
   - Invalid attestation
   - Malicious behavior (operator discretion)
   - Default slash: 10% of stake

### Smart Contract Security

1. **Reentrancy Protection**
   - All state changes before external calls
   - Use of `raw_reserve` for balance management

2. **Integer Overflow Prevention**
   - FunC v0.4.0+ has built-in overflow checks
   - Explicit bounds checking on critical values

3. **Gas Limit Management**
   - Batch operations for large datasets
   - Off-chain computation with on-chain verification (Merkle proofs)

4. **Upgrade Safety**
   - Proxy pattern for upgradeability
   - Data migration procedures
   - Emergency pause capability

## Upgrade Strategy

### Proxy Pattern

All three contracts implement an upgradeable proxy pattern:

```func
;; Storage layout
;; [0] implementation_code: cell
;; [1] contract_data: cell

() upgrade_implementation(cell new_code) impure {
  throw_unless(error::unauthorized, equal_slices(sender, owner));

  ;; Verify new code hash is whitelisted (optional)
  ;; Update implementation
  set_code(new_code);

  emit_event(event::implementation_upgraded, slice_hash(new_code.begin_parse()));
}
```

### Data Migration

For major data structure changes:

1. Deploy new implementation alongside old
2. Gradually migrate data in batches
3. Verify integrity
4. Switch over when complete
5. Keep old implementation for rollback

### Version Compatibility

Contracts store a `contract_version` field:
- Backward compatible changes: Increment minor version
- Breaking changes: Increment major version
- Backend must check version compatibility before operations

## Testing Requirements

### Unit Tests

1. PoolOperator:
   - Participant registration/removal
   - Parameter updates
   - Emergency pause/resume
   - Fee calculations

2. RewardDistribution:
   - Payment reception
   - Epoch management
   - Distribution calculations
   - Merkle proof verification

3. ParticipantRegistry:
   - Contribution tracking
   - Stake management
   - Slashing logic
   - Reputation updates

### Integration Tests

1. End-to-end registration flow
2. Complete reward distribution cycle
3. Withdrawal with timelock
4. Emergency scenarios

### Security Audits

Before mainnet deployment:
1. External security audit (recommended: CertiK, Trail of Bits)
2. Formal verification of critical functions
3. Bug bounty program
4. Testnet deployment with real usage

## Deployment Checklist

- [ ] Unit tests passing (100% coverage)
- [ ] Integration tests passing
- [ ] Security audit completed and issues resolved
- [ ] Testnet deployment successful
- [ ] Documentation complete
- [ ] Backend integration verified
- [ ] Emergency procedures documented
- [ ] Monitoring and alerting configured
- [ ] Multi-signature wallet setup for owner operations
- [ ] Upgrade procedures tested
