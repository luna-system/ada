/** @type {import('ts-jest').JestConfigWithTsJest} */
module.exports = {
    preset: 'ts-jest',
    testEnvironment: 'node',
    roots: ['<rootDir>/src'],
    testMatch: ['**/__tests__/**/*.test.ts'],
    moduleFileExtensions: ['ts', 'js'],
    // Silence ts-jest hybrid module warning
    transform: {
        '^.+\\.ts$': ['ts-jest', {
            diagnostics: {
                ignoreCodes: [151002]
            }
        }]
    },
    collectCoverageFrom: [
        'src/handlers/**/*.ts',
        'src/formatters/**/*.ts',
        'src/types/**/*.ts',
        '!src/**/*.test.ts',
    ],
    coverageThreshold: {
        // Focus on our testable modules - 100% coverage!
        'src/handlers/': {
            branches: 100,
            functions: 100,
            lines: 100,
            statements: 100
        },
        'src/formatters/': {
            branches: 100,
            functions: 100,
            lines: 100,
            statements: 100
        }
    },
    // Don't try to import vscode - mock it
    moduleNameMapper: {
        '^vscode$': '<rootDir>/src/__mocks__/vscode.ts'
    },
    // Faster in watch mode
    watchPathIgnorePatterns: ['<rootDir>/node_modules/', '<rootDir>/out/']
};
