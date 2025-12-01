# Migration Plan: Centralized to Decentralized Management

## Overview

This document outlines the strategy for migrating the GPU Resource Pool from centralized operator control to decentralized governance through a DAO (Decentralized Autonomous Organization) model.

## Table of Contents

1. [Migration Philosophy](#migration-philosophy)
2. [Migration Phases](#migration-phases)
3. [Governance Model](#governance-model)
4. [Technical Implementation](#technical-implementation)
5. [Timeline and Milestones](#timeline-and-milestones)
6. [Risk Mitigation](#risk-mitigation)

## Migration Philosophy

### Core Principles

1. **Gradual Transition**: Phased approach to minimize disruption
2. **Proven Operation**: Demonstrate centralized model works before decentralizing
3. **Community Building**: Establish engaged participant base first
4. **Safety First**: Maintain ability to pause/revert if issues arise
5. **Transparency**: All decisions and processes publicly documented

### Why Gradual Migration?

**Centralized Start (Phase 0-1):**
- Faster iteration and bug fixes
- Clearer accountability
- Simpler decision-making
- Easier to attract early participants (known operator)

**Decentralized Goal (Phase 3-4):**
- Censorship resistance
- Community ownership
- Distributed decision-making
- Long-term sustainability

## Migration Phases

### Phase 0: Centralized Launch (Months 1-3)

**Governance:**
- Single operator controls all decisions
- Operator owns PoolOperator contract
- Direct parameter updates

**Characteristics:**
- Quick response to issues
- Centralized fee management
- Operator-driven participant onboarding
- Manual intervention allowed

**Success Criteria:**
- Pool operational for 3 months
- 10+ active participants
- 99%+ uptime
- No critical security incidents
- Positive participant feedback

**Metrics:**
```
- Uptime: >99%
- Participants: 10-25
- Revenue: >500 TON/month
- Participant satisfaction: >80%
```

### Phase 1: Multi-Signature Governance (Months 4-9)

**Governance:**
- Transition to multi-sig wallet for critical operations
- 3-of-5 or 5-of-7 multi-sig
- Signers: Operator + trusted participants

**Implementation:**

```typescript
// Deploy Gnosis Safe or TON multi-sig
const multiSig = await deploySafeMultisig({
  owners: [
    operatorAddress,
    topParticipant1Address,
    topParticipant2Address,
    communityRepresentative1,
    communityRepresentative2
  ],
  threshold: 3, // 3 signatures required
});

// Transfer PoolOperator ownership to multi-sig
await poolOperator.sendChangeOwner(multiSig.address);
```

**Multi-Sig Operations:**
- Parameter changes (fees, minimum stake)
- Contract upgrades
- Emergency pause/resume
- Operator fee withdrawals

**Standard Operations (still centralized):**
- Contribution tracking
- Distribution execution
- Infrastructure management

**Success Criteria:**
- Multi-sig operational for 6 months
- No missed critical decisions
- All signers actively participating
- 25+ participants
- Established operating procedures

**Metrics:**
```
- Participants: 25-50
- Multi-sig decisions: 10+ successful
- Decision latency: <48 hours
- Community engagement: >60%
```

### Phase 2: DAO Formation (Months 10-18)

**Governance:**
- Launch governance token (GP-TON or similar)
- Token distribution to participants
- Voting mechanism implementation
- DAO treasury establishment

#### 2.1 Governance Token Design

**GP-TON (GPU Pool TON) Token:**

```func
// Governance token properties
- Type: Jetton (TON standard token)
- Total Supply: 100,000,000 GP-TON
- Non-inflationary (fixed supply)
- Transferable (with optional lock periods)
- Votable (1 token = 1 vote)
```

**Token Distribution:**

| Allocation | Percentage | Amount | Vesting |
|------------|------------|--------|---------|
| Early Participants | 30% | 30M | 6 month cliff, 18 month vest |
| Future Participants | 25% | 25M | Distributed over time based on contribution |
| Pool Operator | 15% | 15M | 12 month cliff, 24 month vest |
| DAO Treasury | 20% | 20M | Controlled by governance |
| Community Incentives | 10% | 10M | For growth initiatives |

**Token Earning Mechanism:**

Participants earn GP-TON based on contribution:

```python
# Monthly GP-TON rewards per participant
gp_ton_earned = (
    participant_contribution_score /
    total_contribution_score
) × monthly_gp_ton_allocation

# Example: If 100,000 GP-TON distributed monthly
# Alice with 5% contribution score earns:
# = 0.05 × 100,000 = 5,000 GP-TON
```

**Voting Power:**
```
voting_power = gp_ton_balance + staked_ton_balance × multiplier
multiplier = 10 (1 TON staked = 10 GP-TON voting power)
```

#### 2.2 DAO Structure

**Governance Contracts:**

```
┌──────────────────────────────────────┐
│         DAO Governor Contract         │
│  - Proposal creation & voting         │
│  - Execution of approved proposals    │
│  - Timelock for safety               │
└──────────────────────────────────────┘
              │
              ├──────────────────────────┐
              │                          │
┌─────────────▼────────────┐  ┌─────────▼──────────┐
│   GP-TON Token Contract   │  │  DAO Treasury      │
│  - Voting weight source   │  │  - Community funds │
└──────────────────────────┘  └────────────────────┘
```

**Governance Smart Contract:**

```func
// GovernanceContract.fc
global cell proposals;              // Dict: proposal_id -> ProposalInfo
global int proposal_count;
global slice dao_treasury;
global slice gp_ton_contract;
global int quorum_percentage;       // e.g., 10% of total supply
global int approval_threshold;      // e.g., 66% of votes
global int voting_period_sec;       // e.g., 7 days
global int timelock_period_sec;     // e.g., 2 days
global int proposal_deposit;        // e.g., 1000 GP-TON

// Proposal structure
{
  proposal_id: int
  proposer: slice
  title: string
  description: string
  actions: cell                     // List of contract calls to execute
  start_timestamp: int
  end_timestamp: int
  votes_for: int
  votes_against: int
  votes_abstain: int
  status: int                       // Pending, Active, Passed, Failed, Executed
  execution_timestamp: int
}

// Operations
op::proposal_create
op::proposal_vote
op::proposal_execute
op::proposal_cancel
```

**Proposal Types:**

1. **Parameter Change Proposals**
   - Fee adjustments
   - Minimum stake changes
   - Epoch duration modifications

2. **Budget Proposals**
   - Marketing spend
   - Infrastructure upgrades
   - Developer grants

3. **Governance Change Proposals**
   - Voting threshold adjustments
   - Quorum changes
   - New governance features

4. **Emergency Proposals**
   - Security incident response
   - Contract pauses
   - Rapid parameter changes (reduced timelock)

#### 2.3 Voting Mechanism

**Proposal Lifecycle:**

```
1. Creation (requires deposit)
     ↓
2. Community Discussion (3 days)
     ↓
3. Voting Period (7 days)
     ↓
4. Timelock (2 days if passed)
     ↓
5. Execution (if passed) or Cancellation (if failed)
```

**Voting Options:**
- **For**: Support proposal
- **Against**: Oppose proposal
- **Abstain**: Count toward quorum but neutral

**Quorum Requirement:**
```
total_votes = votes_for + votes_against + votes_abstain
quorum_met = total_votes >= (total_gp_ton_supply × quorum_percentage)
```

**Approval Requirement:**
```
approval = votes_for / (votes_for + votes_against) >= approval_threshold
```

**Example:**
```
Total GP-TON supply: 100,000,000
Quorum: 10% = 10,000,000 GP-TON must vote
Approval threshold: 66%

Proposal results:
- Votes For: 7,000,000
- Votes Against: 2,000,000
- Votes Abstain: 1,500,000
- Total Votes: 10,500,000

Quorum check: 10,500,000 >= 10,000,000 ✓
Approval check: 7,000,000 / (7,000,000 + 2,000,000) = 77.8% >= 66% ✓

Result: PASSED
```

#### 2.4 DAO Treasury

**Treasury Funding:**
- Portion of operator fees (start at 20%, increase to 50% over time)
- Grants and donations
- Investment returns

**Treasury Usage (approved by governance):**
- Infrastructure costs
- Developer incentives
- Marketing and growth
- Security audits
- Community events

**Initial Treasury Allocation:**
```
- Infrastructure reserve: 40%
- Development fund: 30%
- Marketing & growth: 20%
- Emergency fund: 10%
```

### Phase 3: Progressive Decentralization (Months 19-30)

**Governance:**
- DAO controls all major decisions
- Operator becomes service provider (voted on)
- Community proposals actively used

**Decentralization Checklist:**

- [ ] PoolOperator ownership transferred to DAO Governor contract
- [ ] Parameter changes require governance vote
- [ ] Budget allocation decided by DAO
- [ ] Operator compensation voted on quarterly
- [ ] Emergency multisig still exists (6-of-9 including operator)
- [ ] Community-elected representatives for day-to-day operations

**Operator Role Evolution:**

**Phase 2 (Centralized):**
- Owner of contracts
- Sole decision maker
- Direct fee recipient

**Phase 3 (Service Provider):**
- Service agreement with DAO
- Quarterly performance reviews
- Compensation voted on by governance
- Can be replaced by DAO vote

**Service Agreement Example:**

```yaml
operator_agreement:
  role: Infrastructure Operations
  responsibilities:
    - Maintain backend services (99%+ uptime)
    - Monitor worker health
    - Process contribution updates
    - Execute reward distributions
    - 24/7 on-call support

  compensation:
    base_fee: 50 TON/month
    performance_bonus:
      - uptime >99.9%: +20 TON
      - error_rate <0.1%: +10 TON
      - participant_satisfaction >90%: +20 TON

  kpis:
    - uptime_percentage: >99%
    - avg_response_time: <500ms
    - incident_resolution_time: <2h
    - participant_onboarding_time: <24h

  term: 3 months
  renewal: Requires DAO vote
```

**Success Criteria:**
- DAO successfully passes 10+ proposals
- Community-driven improvements implemented
- Operator operates under service agreement
- No centralization concerns raised

### Phase 4: Full Decentralization (Months 30+)

**Governance:**
- Fully on-chain governance
- No single point of failure
- Multiple service providers (operators)
- Global community participation

**Characteristics:**

1. **Contract Ownership:**
   - DAO Governor contract owns all pool contracts
   - No individual or entity has admin keys
   - All changes via governance

2. **Operations:**
   - Multiple competing service providers
   - DAO votes on providers quarterly
   - Redundant infrastructure

3. **Decision Making:**
   - All major decisions on-chain
   - Transparent voting
   - Delegated voting for inactive holders

4. **Economic Model:**
   - DAO treasury funds all operations
   - Service providers paid from treasury
   - Fee structure governed by community

**Multi-Provider Model:**

```
┌─────────────────────────────────────┐
│          DAO Governance             │
└─────────────────────────────────────┘
              │
    ┌─────────┴─────────┬─────────────┐
    │                   │             │
┌───▼────┐        ┌────▼────┐   ┌───▼────┐
│Provider│        │Provider │   │Provider│
│   A    │        │   B     │   │   C    │
│Backend │        │Backend  │   │Backend │
└────────┘        └─────────┘   └────────┘
```

- Each provider operates independent infrastructure
- DAO routes work based on performance/cost
- Providers compete for DAO contracts
- No single provider critical (redundancy)

## Governance Model

### Voting Parameters

**Recommended Settings (adjustable by governance):**

```yaml
governance_parameters:
  # Voting
  quorum_percentage: 10%             # Of total GP-TON supply
  approval_threshold: 66%            # Of votes cast (For vs Against)
  voting_period: 7 days
  timelock_period: 2 days
  proposal_deposit: 1000 GP-TON     # Refunded if passed

  # Emergency proposals
  emergency_quorum: 5%
  emergency_approval: 80%
  emergency_timelock: 6 hours

  # Delegation
  delegation_enabled: true
  max_delegation_depth: 2            # Prevent long delegation chains
```

### Proposal Categories and Thresholds

| Category | Quorum | Approval | Timelock |
|----------|--------|----------|----------|
| Standard | 10% | 66% | 2 days |
| Economic (fees) | 15% | 70% | 3 days |
| Governance Changes | 20% | 75% | 5 days |
| Emergency | 5% | 80% | 6 hours |
| Contract Upgrades | 25% | 80% | 7 days |

### Delegation System

Participants can delegate voting power:

```typescript
// Delegate voting power
await gpTonContract.sendDelegate({
  delegateTo: expertParticipantAddress,
  amount: 1000 // GP-TON to delegate
});

// Revoke delegation
await gpTonContract.sendUndelegate({
  amount: 500 // Partial undelegate
});
```

**Benefits:**
- Inactive holders can participate via delegation
- Expert participants gain influence
- Increases effective participation rate

**Safeguards:**
- Delegator can override delegate's vote
- Delegation can be revoked anytime
- Delegates must disclose conflicts of interest

## Technical Implementation

### Smart Contract Upgrades

**Upgrade Process:**

1. **Proposal Creation:**
   ```typescript
   await daoGovernor.createProposal({
     title: "Upgrade PoolOperator to v2.0",
     description: "Adds participant tier system",
     actions: [
       {
         target: poolOperatorAddress,
         method: "op::pool_upgrade",
         params: {
           new_code: newPoolOperatorCode,
           new_data: migrationData
         },
         value: toNano("0.1")
       }
     ],
     deposit: toNano("1000") // 1000 GP-TON
   });
   ```

2. **Community Review:**
   - Code published on GitHub
   - Security audit shared
   - Community discussion period

3. **Voting:**
   - 7-day voting period
   - Quorum and approval checked

4. **Timelock:**
   - 7-day timelock for contract upgrades
   - Allows final review and potential cancellation

5. **Execution:**
   - Automated execution after timelock
   - Or manual execution by anyone

### Data Migration

For contract upgrades requiring data migration:

```func
// Migration function in new contract
() migrate_from_v1(cell old_data) impure {
  slice ds = old_data.begin_parse();

  // Parse old format
  slice owner = ds~load_msg_addr();
  int pool_id = ds~load_uint(32);
  cell participants_old = ds~load_ref();

  // Transform to new format
  cell participants_new = migrate_participants(participants_old);

  // Add new fields with defaults
  int tier_system_enabled = 0;
  cell tier_config = pack_default_tier_config();

  // Save in new format
  save_data_v2(owner, pool_id, participants_new, tier_system_enabled, tier_config);
}
```

### Governance Contract Interface

```typescript
interface DAOGovernorContract {
  // Proposal management
  createProposal(params: ProposalParams): Promise<number>;
  vote(proposalId: number, vote: VoteType): Promise<void>;
  executeProposal(proposalId: number): Promise<void>;
  cancelProposal(proposalId: number): Promise<void>;

  // Delegation
  delegate(to: Address, amount: bigint): Promise<void>;
  undelegate(amount: bigint): Promise<void>;

  // Queries
  getProposal(proposalId: number): Promise<Proposal>;
  getVotingPower(address: Address): Promise<bigint>;
  getQuorum(): Promise<bigint>;
}
```

## Timeline and Milestones

### Detailed Timeline

**Month 1-3: Phase 0 (Centralized)**
- Week 1-2: Deploy contracts
- Week 3-4: Onboard first participants
- Week 5-12: Operate, iterate, improve

**Month 4-6: Phase 1 Preparation**
- Month 4: Select multi-sig participants
- Month 5: Deploy multi-sig, test
- Month 6: Transfer ownership to multi-sig

**Month 7-9: Phase 1 (Multi-Sig)**
- Operate under multi-sig
- Establish decision-making procedures
- Document governance processes

**Month 10-12: Phase 2 Preparation**
- Month 10: Design governance token
- Month 11: Develop DAO contracts
- Month 12: Audit DAO contracts

**Month 13-15: Phase 2 Launch**
- Month 13: Deploy DAO contracts
- Month 14: Distribute GP-TON tokens
- Month 15: First governance votes

**Month 16-18: Phase 2 Maturation**
- Active governance participation
- DAO treasury established
- Multiple proposals passed

**Month 19-24: Phase 3 (Progressive)**
- Month 19: Transfer ownership to DAO
- Month 20-21: Operator service agreement
- Month 22-24: Community-led initiatives

**Month 25-30: Phase 3 Maturation**
- Establish multiple service providers
- Decentralized infrastructure
- Global community

**Month 30+: Phase 4 (Full Decentralization)**
- No single point of control
- Mature governance process
- Sustainable long-term operation

### Key Milestones

| Milestone | Target Date | Success Metric |
|-----------|-------------|----------------|
| Launch | Month 1 | 10 participants |
| Stability | Month 3 | 99% uptime |
| Multi-sig | Month 6 | 3 successful votes |
| Token Launch | Month 13 | 100% distribution |
| First DAO Vote | Month 15 | Quorum met |
| DAO Ownership | Month 19 | Transfer complete |
| Multi-Provider | Month 25 | 2+ operators |
| Full Decentralization | Month 30 | No central control |

## Risk Mitigation

### Phase 0-1 Risks

**Risk: Operator Abuse**
- Mitigation: Multi-sig early (Month 6)
- Mitigation: Transparent operations
- Mitigation: Community oversight

**Risk: Technical Failures**
- Mitigation: Extensive testing
- Mitigation: Emergency pause capability
- Mitigation: Rollback procedures

### Phase 2-3 Risks

**Risk: Low Governance Participation**
- Mitigation: Incentivize voting (small GP-TON rewards)
- Mitigation: Delegation system
- Mitigation: Community engagement efforts

**Risk: Governance Attacks (vote buying, etc.)**
- Mitigation: High quorum thresholds
- Mitigation: Timelocks for review
- Mitigation: Community monitoring
- Mitigation: Reputation systems

**Risk: DAO Treasury Mismanagement**
- Mitigation: Spending limits per proposal
- Mitigation: Multi-sig backup for emergency
- Mitigation: Quarterly budget reviews

### Phase 4 Risks

**Risk: Stagnation (no decisions made)**
- Mitigation: Default parameters that work
- Mitigation: Emergency fallback governance
- Mitigation: Incentive alignment

**Risk: Plutocracy (whale control)**
- Mitigation: Quadratic voting (future)
- Mitigation: Reputation-weighted voting
- Mitigation: Delegation caps

### Emergency Procedures

**If governance becomes deadlocked:**
1. Emergency multi-sig can pause operations
2. 48-hour community discussion
3. Emergency proposal with reduced timelock
4. If still deadlocked, revert to Phase 2 temporarily

**If security incident occurs:**
1. Anyone can trigger emergency pause
2. Multi-sig (6-of-9) required to resume
3. DAO vote required for permanent changes

**If DAO contract bug found:**
1. Immediate pause via multi-sig
2. Security audit of bug
3. Fix deployed under emergency procedures
4. Community vote on permanent fix

## Conclusion

This migration plan provides a clear path from centralized operation to full decentralization. The gradual approach allows the community to mature alongside the technology, ensuring a stable and sustainable transition.

**Success depends on:**
- Building strong community
- Proving operational excellence
- Transparent communication
- Patient, methodical execution

**End State:**
- Community-owned and operated
- No single point of failure
- Sustainable economics
- Global participation

The migration is not a one-time event but an ongoing journey toward progressive decentralization, with the flexibility to adjust based on real-world experience and community feedback.
