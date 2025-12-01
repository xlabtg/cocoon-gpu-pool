const { compileFunc } = require('@ton-community/func-js');
const fs = require('fs');
const path = require('path');

async function compileContract(contractName) {
    console.log(`Compiling ${contractName}...`);

    const stdlibPath = path.join(__dirname, '../contracts/stdlib.fc');
    const contractPath = path.join(__dirname, `../contracts/${contractName}.fc`);

    const stdlib = fs.readFileSync(stdlibPath, 'utf-8');
    const contractCode = fs.readFileSync(contractPath, 'utf-8');

    const result = await compileFunc({
        targets: [`${contractName}.fc`],
        sources: {
            'stdlib.fc': stdlib,
            [`${contractName}.fc`]: contractCode,
        },
    });

    if (result.status === 'error') {
        console.error(`Compilation failed for ${contractName}:`, result.message);
        process.exit(1);
    }

    const outputDir = path.join(__dirname, '../build');
    if (!fs.existsSync(outputDir)) {
        fs.mkdirSync(outputDir, { recursive: true });
    }

    const outputPath = path.join(outputDir, `${contractName}.cell`);
    fs.writeFileSync(outputPath, result.codeBoc, 'base64');

    console.log(`✓ ${contractName} compiled successfully`);
    console.log(`  Output: ${outputPath}`);

    return result.codeBoc;
}

async function main() {
    console.log('Starting compilation of all contracts...\n');

    try {
        await compileContract('pool_operator');
        await compileContract('participant_registry');
        await compileContract('reward_distribution');

        console.log('\n✓ All contracts compiled successfully!');
    } catch (error) {
        console.error('\n✗ Compilation failed:', error);
        process.exit(1);
    }
}

if (require.main === module) {
    main();
}

module.exports = { compileContract };
