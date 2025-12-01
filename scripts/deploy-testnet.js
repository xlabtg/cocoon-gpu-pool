const { compileContract } = require('./compile');
const { Address, toNano, beginCell } = require('@ton/core');

/**
 * Deployment script for TON testnet
 *
 * Prerequisites:
 * 1. Install TON CLI: https://github.com/ton-blockchain/ton/releases
 * 2. Create wallet on testnet
 * 3. Get testnet coins from faucet: https://t.me/testgiver_ton_bot
 * 4. Set environment variables:
 *    - OPERATOR_ADDRESS: Your wallet address
 *    - OPERATOR_KEY: Path to your wallet key file
 */

const config = {
    network: 'testnet',
    operatorAddress: process.env.OPERATOR_ADDRESS || 'EQD_...',
    initialCommission: 1000, // 10%
    initialStake: toNano('100'),
};

async function deployPoolOperator() {
    console.log('\n=== Deploying PoolOperator ===');

    const codeBoc = await compileContract('pool_operator');

    // Create initial data cell (empty for initialization)
    const dataCell = new Cell();

    // Create initialization message
    const initMessage = beginCell()
        .storeUint(1, 32) // OP_INITIALIZE
        .storeUint(config.initialCommission, 16)
        .endCell();

    console.log('Contract compiled and ready for deployment');
    console.log('');
    console.log('To deploy using tonos-cli:');
    console.log('');
    console.log(`tonos-cli deploy \\`);
    console.log(`  --abi pool_operator.abi.json \\`);
    console.log(`  --sign ${process.env.OPERATOR_KEY || 'operator.keys.json'} \\`);
    console.log(`  --wc 0 \\`);
    console.log(`  pool_operator.tvc \\`);
    console.log(`  '{"commission":${config.initialCommission}}' \\`);
    console.log(`  --value ${config.initialStake}`);
    console.log('');

    return {
        code: codeBoc,
        data: dataCell,
        initMessage,
    };
}

async function deployParticipantRegistry(poolOperatorAddress) {
    console.log('\n=== Deploying ParticipantRegistry ===');

    const codeBoc = await compileContract('participant_registry');

    const dataCell = new Cell();

    const initMessage = beginCell()
        .storeUint(1, 32) // OP_INITIALIZE
        .endCell();

    console.log('Contract compiled and ready for deployment');
    console.log('');
    console.log('To deploy using tonos-cli:');
    console.log('');
    console.log(`tonos-cli deploy \\`);
    console.log(`  --abi participant_registry.abi.json \\`);
    console.log(`  --sign ${process.env.OPERATOR_KEY || 'operator.keys.json'} \\`);
    console.log(`  --wc 0 \\`);
    console.log(`  participant_registry.tvc \\`);
    console.log(`  '{}' \\`);
    console.log(`  --value 1000000000`);
    console.log('');

    return {
        code: codeBoc,
        data: dataCell,
        initMessage,
    };
}

async function deployRewardDistribution(poolOperatorAddress, registryAddress) {
    console.log('\n=== Deploying RewardDistribution ===');

    const codeBoc = await compileContract('reward_distribution');

    const dataCell = new Cell();

    const initMessage = beginCell()
        .storeUint(1, 32) // OP_INITIALIZE
        .storeAddress(Address.parse(registryAddress))
        .endCell();

    console.log('Contract compiled and ready for deployment');
    console.log('');
    console.log('To deploy using tonos-cli:');
    console.log('');
    console.log(`tonos-cli deploy \\`);
    console.log(`  --abi reward_distribution.abi.json \\`);
    console.log(`  --sign ${process.env.OPERATOR_KEY || 'operator.keys.json'} \\`);
    console.log(`  --wc 0 \\`);
    console.log(`  reward_distribution.tvc \\`);
    console.log(`  '{"registry":"${registryAddress}"}' \\`);
    console.log(`  --value 1000000000`);
    console.log('');

    return {
        code: codeBoc,
        data: dataCell,
        initMessage,
    };
}

async function linkContracts(poolOperatorAddr, registryAddr, distributionAddr) {
    console.log('\n=== Linking Contracts ===');
    console.log('');
    console.log('Set registry address in PoolOperator:');
    console.log(`tonos-cli call ${poolOperatorAddr} setRegistry '{"registry":"${registryAddr}"}' --sign operator.keys.json`);
    console.log('');
    console.log('Set distribution address in PoolOperator:');
    console.log(`tonos-cli call ${poolOperatorAddr} setDistribution '{"distribution":"${distributionAddr}"}' --sign operator.keys.json`);
    console.log('');
}

async function activatePool(poolOperatorAddr) {
    console.log('\n=== Activating Pool ===');
    console.log('');
    console.log('Activate the pool:');
    console.log(`tonos-cli call ${poolOperatorAddr} activatePool '{}' --sign operator.keys.json`);
    console.log('');
}

async function main() {
    console.log('========================================');
    console.log('TON Testnet Deployment Guide');
    console.log('========================================');
    console.log('');
    console.log('Network:', config.network);
    console.log('Operator:', config.operatorAddress);
    console.log('Initial Commission:', `${config.initialCommission / 100}%`);
    console.log('Initial Stake:', config.initialStake, 'nanotons');
    console.log('');

    try {
        // Step 1: Deploy PoolOperator
        const poolOperator = await deployPoolOperator();

        // Placeholder addresses for demonstration
        const poolOperatorAddr = 'EQD_POOL_OPERATOR_ADDRESS_HERE';
        const registryAddr = 'EQD_REGISTRY_ADDRESS_HERE';
        const distributionAddr = 'EQD_DISTRIBUTION_ADDRESS_HERE';

        // Step 2: Deploy ParticipantRegistry
        await deployParticipantRegistry(poolOperatorAddr);

        // Step 3: Deploy RewardDistribution
        await deployRewardDistribution(poolOperatorAddr, registryAddr);

        // Step 4: Link contracts
        await linkContracts(poolOperatorAddr, registryAddr, distributionAddr);

        // Step 5: Activate pool
        await activatePool(poolOperatorAddr);

        console.log('========================================');
        console.log('Deployment preparation complete!');
        console.log('========================================');
        console.log('');
        console.log('Next steps:');
        console.log('1. Deploy each contract using the tonos-cli commands above');
        console.log('2. Update the placeholder addresses with actual deployed addresses');
        console.log('3. Link the contracts together using the provided commands');
        console.log('4. Activate the pool');
        console.log('5. Test with testnet participants');
        console.log('');

    } catch (error) {
        console.error('Deployment preparation failed:', error);
        process.exit(1);
    }
}

if (require.main === module) {
    main();
}

module.exports = {
    deployPoolOperator,
    deployParticipantRegistry,
    deployRewardDistribution,
};
