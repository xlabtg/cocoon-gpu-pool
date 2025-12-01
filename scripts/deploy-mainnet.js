const { compileContract } = require('./compile');

/**
 * Deployment script for TON mainnet
 *
 * ⚠️ WARNING: This script is for mainnet deployment
 *
 * Prerequisites:
 * 1. Complete security audit of all contracts
 * 2. Extensive testnet testing
 * 3. Mainnet wallet with sufficient TON
 * 4. Operator stake ready (minimum 100 TON + gas fees)
 *
 * Environment variables required:
 * - OPERATOR_ADDRESS: Mainnet wallet address
 * - OPERATOR_KEY: Path to mainnet wallet key file (keep secure!)
 * - INITIAL_COMMISSION: Commission rate in basis points (500-1500)
 * - OPERATOR_STAKE: Initial stake amount in TON
 */

const config = {
    network: 'mainnet',
    operatorAddress: process.env.OPERATOR_ADDRESS,
    initialCommission: parseInt(process.env.INITIAL_COMMISSION || '1000'),
    operatorStake: process.env.OPERATOR_STAKE || '100',
};

function validateConfig() {
    const errors = [];

    if (!config.operatorAddress) {
        errors.push('OPERATOR_ADDRESS not set');
    }

    if (!process.env.OPERATOR_KEY) {
        errors.push('OPERATOR_KEY not set');
    }

    if (config.initialCommission < 500 || config.initialCommission > 1500) {
        errors.push('INITIAL_COMMISSION must be between 500 and 1500 (5%-15%)');
    }

    const stake = parseFloat(config.operatorStake);
    if (isNaN(stake) || stake < 100) {
        errors.push('OPERATOR_STAKE must be at least 100 TON');
    }

    if (errors.length > 0) {
        console.error('Configuration errors:');
        errors.forEach(err => console.error(`  - ${err}`));
        process.exit(1);
    }
}

async function performSecurityChecks() {
    console.log('\n=== Security Checklist ===');
    console.log('');
    console.log('Before deploying to mainnet, verify:');
    console.log('');
    console.log('[ ] 1. All contracts have been audited by a reputable security firm');
    console.log('[ ] 2. Audit report has been reviewed and all issues resolved');
    console.log('[ ] 3. Extensive testnet testing has been completed');
    console.log('[ ] 4. All test cases pass with 100% coverage');
    console.log('[ ] 5. Economic parameters have been validated');
    console.log('[ ] 6. Operator wallet is secured with hardware wallet or multisig');
    console.log('[ ] 7. Operator stake funds are available and confirmed');
    console.log('[ ] 8. Emergency pause/recovery procedures are documented');
    console.log('[ ] 9. Monitoring and alerting systems are in place');
    console.log('[ ] 10. Team has reviewed and approved deployment');
    console.log('');
    console.log('⚠️  MAINNET DEPLOYMENT IS IRREVERSIBLE');
    console.log('⚠️  ENSURE ALL CHECKS ARE COMPLETED');
    console.log('');

    // In production, this would require interactive confirmation
    const confirmed = process.env.CONFIRM_MAINNET_DEPLOY === 'yes-i-am-sure';

    if (!confirmed) {
        console.log('Deployment aborted.');
        console.log('Set CONFIRM_MAINNET_DEPLOY=yes-i-am-sure to proceed.');
        process.exit(0);
    }
}

async function main() {
    console.log('========================================');
    console.log('TON MAINNET Deployment');
    console.log('========================================');
    console.log('');

    validateConfig();
    await performSecurityChecks();

    console.log('Configuration:');
    console.log('  Network:', config.network);
    console.log('  Operator:', config.operatorAddress);
    console.log('  Commission:', `${config.initialCommission / 100}%`);
    console.log('  Stake:', config.operatorStake, 'TON');
    console.log('');

    try {
        // Compile all contracts
        console.log('Compiling contracts for mainnet...');
        await compileContract('pool_operator');
        await compileContract('participant_registry');
        await compileContract('reward_distribution');

        console.log('\n✓ All contracts compiled successfully');
        console.log('');
        console.log('=== Mainnet Deployment Steps ===');
        console.log('');
        console.log('1. Deploy PoolOperator:');
        console.log(`   tonos-cli deploy --network mainnet \\`);
        console.log(`     --abi pool_operator.abi.json \\`);
        console.log(`     --sign ${process.env.OPERATOR_KEY} \\`);
        console.log(`     --wc 0 \\`);
        console.log(`     build/pool_operator.cell \\`);
        console.log(`     '{"commission":${config.initialCommission}}' \\`);
        console.log(`     --value ${parseFloat(config.operatorStake) * 1e9}`);
        console.log('');
        console.log('2. Deploy ParticipantRegistry:');
        console.log(`   tonos-cli deploy --network mainnet \\`);
        console.log(`     --abi participant_registry.abi.json \\`);
        console.log(`     --sign ${process.env.OPERATOR_KEY} \\`);
        console.log(`     --wc 0 \\`);
        console.log(`     build/participant_registry.cell \\`);
        console.log(`     '{}' \\`);
        console.log(`     --value 1000000000`);
        console.log('');
        console.log('3. Deploy RewardDistribution:');
        console.log(`   tonos-cli deploy --network mainnet \\`);
        console.log(`     --abi reward_distribution.abi.json \\`);
        console.log(`     --sign ${process.env.OPERATOR_KEY} \\`);
        console.log(`     --wc 0 \\`);
        console.log(`     build/reward_distribution.cell \\`);
        console.log(`     '{"registry":"<REGISTRY_ADDRESS>"}' \\`);
        console.log(`     --value 1000000000`);
        console.log('');
        console.log('4. Link contracts (replace addresses):');
        console.log(`   tonos-cli call <POOL_OPERATOR_ADDR> setRegistry \\`);
        console.log(`     '{"registry":"<REGISTRY_ADDR>"}' \\`);
        console.log(`     --sign ${process.env.OPERATOR_KEY} --network mainnet`);
        console.log('');
        console.log(`   tonos-cli call <POOL_OPERATOR_ADDR> setDistribution \\`);
        console.log(`     '{"distribution":"<DISTRIBUTION_ADDR>"}' \\`);
        console.log(`     --sign ${process.env.OPERATOR_KEY} --network mainnet`);
        console.log('');
        console.log('5. Activate pool:');
        console.log(`   tonos-cli call <POOL_OPERATOR_ADDR> activatePool \\`);
        console.log(`     '{}' \\`);
        console.log(`     --sign ${process.env.OPERATOR_KEY} --network mainnet`);
        console.log('');
        console.log('========================================');
        console.log('⚠️  VERIFY EACH STEP BEFORE PROCEEDING');
        console.log('========================================');
        console.log('');

    } catch (error) {
        console.error('Mainnet deployment preparation failed:', error);
        process.exit(1);
    }
}

if (require.main === module) {
    main();
}
