# Testing Guide

## Overview

This directory contains comprehensive unit tests for the Cocoon GPU Pool smart contracts.

## Test Structure

- `PoolOperator.spec.ts` - Tests for the PoolOperator contract
- `ParticipantRegistry.spec.ts` - Tests for the ParticipantRegistry contract
- `RewardDistribution.spec.ts` - Tests for the RewardDistribution contract
- `Integration.spec.ts` - Integration tests for all contracts working together

## Running Tests

```bash
# Install dependencies
npm install

# Run all tests
npm test

# Run tests with coverage
npm run test:coverage

# Run specific test file
npm test -- PoolOperator.spec.ts
```

## Test Coverage

The test suite aims for 100% code coverage across all contracts, including:

- All operation codes and functions
- All error conditions and validations
- All get methods
- All state transitions
- Edge cases and boundary conditions

## Testing Framework

We use the following tools:

- **Jest**: Test runner and assertion library
- **@ton-community/sandbox**: TON blockchain emulator for testing
- **@ton-community/func-js**: FunC compiler for contract compilation
- **@ton/core**: Core TON libraries for working with cells and addresses

## Test Data

Tests use the following conventions:

- Operator stake: 100 TON minimum
- Participant stake: 10 TON minimum
- Commission rates: 5-15% (500-1500 basis points)
- Uptime precision: 100.00% = 10000
- GPU performance scores: 0-1000000

## Writing New Tests

When adding new tests:

1. Follow the existing test structure
2. Use descriptive test names
3. Test both success and failure cases
4. Include edge cases
5. Maintain 100% coverage requirement
