import { Blockchain, SandboxContract, TreasuryContract } from '@ton-community/sandbox';
import { Cell, toNano, beginCell, Address } from '@ton/core';
import { compile } from '@ton-community/func-js';
import * as fs from 'fs';
import * as path from 'path';

describe('PoolOperator', () => {
    let blockchain: Blockchain;
    let poolOperator: SandboxContract<any>;
    let operator: SandboxContract<TreasuryContract>;
    let user: SandboxContract<TreasuryContract>;
    let code: Cell;

    const OP_INITIALIZE = 1;
    const OP_SET_COMMISSION = 2;
    const OP_ADD_STAKE = 3;
    const OP_ACTIVATE_POOL = 4;
    const OP_DEACTIVATE_POOL = 5;
    const OP_WITHDRAW_STAKE = 6;
    const OP_RECEIVE_REWARD = 7;
    const OP_SET_REGISTRY = 8;
    const OP_SET_DISTRIBUTION = 9;

    const ERROR_UNAUTHORIZED = 401;
    const ERROR_INVALID_COMMISSION = 402;
    const ERROR_INSUFFICIENT_STAKE = 403;
    const ERROR_POOL_INACTIVE = 404;
    const ERROR_INVALID_ADDRESS = 405;
    const ERROR_ALREADY_INITIALIZED = 406;

    beforeAll(async () => {
        // Compile contract
        const stdlibPath = path.join(__dirname, '../contracts/stdlib.fc');
        const contractPath = path.join(__dirname, '../contracts/pool_operator.fc');

        const stdlib = fs.readFileSync(stdlibPath, 'utf-8');
        const contractCode = fs.readFileSync(contractPath, 'utf-8');

        const result = await compile({
            targets: ['pool_operator.fc'],
            sources: {
                'stdlib.fc': stdlib,
                'pool_operator.fc': contractCode,
            },
        });

        if (result.status === 'error') {
            throw new Error('Compilation failed: ' + JSON.stringify(result));
        }

        code = Cell.fromBoc(Buffer.from(result.codeBoc, 'base64'))[0];
    });

    beforeEach(async () => {
        blockchain = await Blockchain.create();
        operator = await blockchain.treasury('operator');
        user = await blockchain.treasury('user');

        poolOperator = blockchain.openContract({
            code,
            data: new Cell(),
            address: Address.parse('EQD_' + '0'.repeat(46)),
        } as any);
    });

    describe('Initialization', () => {
        it('should initialize with valid commission and stake', async () => {
            const commission = 1000; // 10%
            const stake = toNano('100');

            const result = await poolOperator.sendInternal(operator.getSender(), {
                value: stake,
                body: beginCell()
                    .storeUint(OP_INITIALIZE, 32)
                    .storeUint(commission, 16)
                    .endCell(),
            });

            expect(result.transactions).toHaveTransaction({
                from: operator.address,
                to: poolOperator.address,
                success: true,
            });

            const poolStatus = await poolOperator.get('get_pool_status');
            expect(poolStatus).toBe(0); // Inactive initially

            const commissionRate = await poolOperator.get('get_commission_rate');
            expect(commissionRate).toBe(commission);

            const operatorStake = await poolOperator.get('get_operator_stake');
            expect(operatorStake).toBeGreaterThanOrEqual(stake);
        });

        it('should reject initialization with commission below 5%', async () => {
            const commission = 400; // 4%
            const stake = toNano('100');

            const result = await poolOperator.sendInternal(operator.getSender(), {
                value: stake,
                body: beginCell()
                    .storeUint(OP_INITIALIZE, 32)
                    .storeUint(commission, 16)
                    .endCell(),
            });

            expect(result.transactions).toHaveTransaction({
                from: operator.address,
                to: poolOperator.address,
                success: false,
                exitCode: ERROR_INVALID_COMMISSION,
            });
        });

        it('should reject initialization with commission above 15%', async () => {
            const commission = 1600; // 16%
            const stake = toNano('100');

            const result = await poolOperator.sendInternal(operator.getSender(), {
                value: stake,
                body: beginCell()
                    .storeUint(OP_INITIALIZE, 32)
                    .storeUint(commission, 16)
                    .endCell(),
            });

            expect(result.transactions).toHaveTransaction({
                from: operator.address,
                to: poolOperator.address,
                success: false,
                exitCode: ERROR_INVALID_COMMISSION,
            });
        });

        it('should reject initialization with insufficient stake', async () => {
            const commission = 1000; // 10%
            const stake = toNano('50'); // Less than 100 TON minimum

            const result = await poolOperator.sendInternal(operator.getSender(), {
                value: stake,
                body: beginCell()
                    .storeUint(OP_INITIALIZE, 32)
                    .storeUint(commission, 16)
                    .endCell(),
            });

            expect(result.transactions).toHaveTransaction({
                from: operator.address,
                to: poolOperator.address,
                success: false,
                exitCode: ERROR_INSUFFICIENT_STAKE,
            });
        });

        it('should reject double initialization', async () => {
            const commission = 1000;
            const stake = toNano('100');

            // First initialization
            await poolOperator.sendInternal(operator.getSender(), {
                value: stake,
                body: beginCell()
                    .storeUint(OP_INITIALIZE, 32)
                    .storeUint(commission, 16)
                    .endCell(),
            });

            // Second initialization attempt
            const result = await poolOperator.sendInternal(operator.getSender(), {
                value: stake,
                body: beginCell()
                    .storeUint(OP_INITIALIZE, 32)
                    .storeUint(commission, 16)
                    .endCell(),
            });

            expect(result.transactions).toHaveTransaction({
                from: operator.address,
                to: poolOperator.address,
                success: false,
                exitCode: ERROR_ALREADY_INITIALIZED,
            });
        });
    });

    describe('Commission Management', () => {
        beforeEach(async () => {
            // Initialize contract
            await poolOperator.sendInternal(operator.getSender(), {
                value: toNano('100'),
                body: beginCell()
                    .storeUint(OP_INITIALIZE, 32)
                    .storeUint(1000, 16)
                    .endCell(),
            });
        });

        it('should allow operator to update commission', async () => {
            const newCommission = 1200; // 12%

            const result = await poolOperator.sendInternal(operator.getSender(), {
                value: toNano('0.1'),
                body: beginCell()
                    .storeUint(OP_SET_COMMISSION, 32)
                    .storeUint(newCommission, 16)
                    .endCell(),
            });

            expect(result.transactions).toHaveTransaction({
                from: operator.address,
                to: poolOperator.address,
                success: true,
            });

            const commissionRate = await poolOperator.get('get_commission_rate');
            expect(commissionRate).toBe(newCommission);
        });

        it('should reject commission update from non-operator', async () => {
            const newCommission = 1200;

            const result = await poolOperator.sendInternal(user.getSender(), {
                value: toNano('0.1'),
                body: beginCell()
                    .storeUint(OP_SET_COMMISSION, 32)
                    .storeUint(newCommission, 16)
                    .endCell(),
            });

            expect(result.transactions).toHaveTransaction({
                from: user.address,
                to: poolOperator.address,
                success: false,
                exitCode: ERROR_UNAUTHORIZED,
            });
        });

        it('should reject invalid commission rates', async () => {
            const invalidCommission = 2000; // 20% - too high

            const result = await poolOperator.sendInternal(operator.getSender(), {
                value: toNano('0.1'),
                body: beginCell()
                    .storeUint(OP_SET_COMMISSION, 32)
                    .storeUint(invalidCommission, 16)
                    .endCell(),
            });

            expect(result.transactions).toHaveTransaction({
                from: operator.address,
                to: poolOperator.address,
                success: false,
                exitCode: ERROR_INVALID_COMMISSION,
            });
        });
    });

    describe('Stake Management', () => {
        beforeEach(async () => {
            await poolOperator.sendInternal(operator.getSender(), {
                value: toNano('100'),
                body: beginCell()
                    .storeUint(OP_INITIALIZE, 32)
                    .storeUint(1000, 16)
                    .endCell(),
            });
        });

        it('should allow operator to add stake', async () => {
            const additionalStake = toNano('50');

            const result = await poolOperator.sendInternal(operator.getSender(), {
                value: additionalStake,
                body: beginCell()
                    .storeUint(OP_ADD_STAKE, 32)
                    .endCell(),
            });

            expect(result.transactions).toHaveTransaction({
                from: operator.address,
                to: poolOperator.address,
                success: true,
            });

            const operatorStake = await poolOperator.get('get_operator_stake');
            expect(operatorStake).toBeGreaterThanOrEqual(toNano('150'));
        });

        it('should allow operator to withdraw stake when pool is inactive', async () => {
            const withdrawAmount = toNano('50');

            const result = await poolOperator.sendInternal(operator.getSender(), {
                value: toNano('0.1'),
                body: beginCell()
                    .storeUint(OP_WITHDRAW_STAKE, 32)
                    .storeCoins(withdrawAmount)
                    .endCell(),
            });

            expect(result.transactions).toHaveTransaction({
                from: operator.address,
                to: poolOperator.address,
                success: true,
            });

            expect(result.transactions).toHaveTransaction({
                from: poolOperator.address,
                to: operator.address,
                value: withdrawAmount,
            });
        });

        it('should reject withdrawal from non-operator', async () => {
            const withdrawAmount = toNano('50');

            const result = await poolOperator.sendInternal(user.getSender(), {
                value: toNano('0.1'),
                body: beginCell()
                    .storeUint(OP_WITHDRAW_STAKE, 32)
                    .storeCoins(withdrawAmount)
                    .endCell(),
            });

            expect(result.transactions).toHaveTransaction({
                from: user.address,
                to: poolOperator.address,
                success: false,
                exitCode: ERROR_UNAUTHORIZED,
            });
        });
    });

    describe('Pool Activation', () => {
        beforeEach(async () => {
            await poolOperator.sendInternal(operator.getSender(), {
                value: toNano('100'),
                body: beginCell()
                    .storeUint(OP_INITIALIZE, 32)
                    .storeUint(1000, 16)
                    .endCell(),
            });

            // Set registry and distribution addresses
            const dummyAddress = Address.parse('EQD_' + '1'.repeat(46));

            await poolOperator.sendInternal(operator.getSender(), {
                value: toNano('0.1'),
                body: beginCell()
                    .storeUint(OP_SET_REGISTRY, 32)
                    .storeAddress(dummyAddress)
                    .endCell(),
            });

            await poolOperator.sendInternal(operator.getSender(), {
                value: toNano('0.1'),
                body: beginCell()
                    .storeUint(OP_SET_DISTRIBUTION, 32)
                    .storeAddress(dummyAddress)
                    .endCell(),
            });
        });

        it('should allow operator to activate pool', async () => {
            const result = await poolOperator.sendInternal(operator.getSender(), {
                value: toNano('0.1'),
                body: beginCell()
                    .storeUint(OP_ACTIVATE_POOL, 32)
                    .endCell(),
            });

            expect(result.transactions).toHaveTransaction({
                from: operator.address,
                to: poolOperator.address,
                success: true,
            });

            const poolStatus = await poolOperator.get('get_pool_status');
            expect(poolStatus).toBe(1); // Active
        });

        it('should allow operator to deactivate pool', async () => {
            // First activate
            await poolOperator.sendInternal(operator.getSender(), {
                value: toNano('0.1'),
                body: beginCell()
                    .storeUint(OP_ACTIVATE_POOL, 32)
                    .endCell(),
            });

            // Then deactivate
            const result = await poolOperator.sendInternal(operator.getSender(), {
                value: toNano('0.1'),
                body: beginCell()
                    .storeUint(OP_DEACTIVATE_POOL, 32)
                    .endCell(),
            });

            expect(result.transactions).toHaveTransaction({
                from: operator.address,
                to: poolOperator.address,
                success: true,
            });

            const poolStatus = await poolOperator.get('get_pool_status');
            expect(poolStatus).toBe(0); // Inactive
        });

        it('should reject activation from non-operator', async () => {
            const result = await poolOperator.sendInternal(user.getSender(), {
                value: toNano('0.1'),
                body: beginCell()
                    .storeUint(OP_ACTIVATE_POOL, 32)
                    .endCell(),
            });

            expect(result.transactions).toHaveTransaction({
                from: user.address,
                to: poolOperator.address,
                success: false,
                exitCode: ERROR_UNAUTHORIZED,
            });
        });
    });

    describe('Get Methods', () => {
        beforeEach(async () => {
            await poolOperator.sendInternal(operator.getSender(), {
                value: toNano('100'),
                body: beginCell()
                    .storeUint(OP_INITIALIZE, 32)
                    .storeUint(1000, 16)
                    .endCell(),
            });
        });

        it('should return correct pool data', async () => {
            const poolData = await poolOperator.get('get_pool_data');
            expect(poolData).toBeDefined();
        });

        it('should return correct operator address', async () => {
            const operatorAddress = await poolOperator.get('get_operator_address');
            expect(operatorAddress).toBeDefined();
        });

        it('should return correct commission rate', async () => {
            const commissionRate = await poolOperator.get('get_commission_rate');
            expect(commissionRate).toBe(1000);
        });

        it('should return correct pool status', async () => {
            const poolStatus = await poolOperator.get('get_pool_status');
            expect(poolStatus).toBe(0);
        });
    });
});
