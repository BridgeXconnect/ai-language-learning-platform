const nextJest = require('next/jest')

const createJestConfig = nextJest({
  // Provide the path to your Next.js app to load next.config.js and .env files
  dir: './client',
})

// Add any custom config to be passed to Jest
const customJestConfig = {
  // Add more setup options before each test is run
  setupFilesAfterEnv: ['<rootDir>/client/jest.setup.js'],
  
  // Test environment
  testEnvironment: 'jest-environment-jsdom',
  
  // Module paths
  moduleNameMapping: {
    '^@/(.*)$': '<rootDir>/client/$1',
    '^@/components/(.*)$': '<rootDir>/client/components/$1',
    '^@/lib/(.*)$': '<rootDir>/client/lib/$1',
    '^@/hooks/(.*)$': '<rootDir>/client/hooks/$1',
    '^@/contexts/(.*)$': '<rootDir>/client/contexts/$1',
    '^@/app/(.*)$': '<rootDir>/client/app/$1',
  },
  
  // Test patterns
  testMatch: [
    '<rootDir>/client/**/__tests__/**/*.(js|jsx|ts|tsx)',
    '<rootDir>/client/**/*.(test|spec).(js|jsx|ts|tsx)',
  ],
  
  // Coverage configuration
  collectCoverageFrom: [
    'client/**/*.{js,jsx,ts,tsx}',
    '!client/**/*.d.ts',
    '!client/node_modules/**',
    '!client/.next/**',
    '!client/out/**',
    '!client/coverage/**',
    '!client/tailwind.config.js',
    '!client/next.config.js',
    '!client/postcss.config.js',
    '!client/jest.config.js',
    '!client/jest.setup.js',
  ],
  
  // Coverage thresholds
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
  
  // Coverage reporters
  coverageReporters: ['text', 'lcov', 'html'],
  
  // Transform configuration
  transform: {
    '^.+\\.(js|jsx|ts|tsx)$': ['babel-jest', { presets: ['next/babel'] }],
  },
  
  // Module file extensions
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json', 'node'],
  
  // Ignore patterns
  testPathIgnorePatterns: [
    '<rootDir>/node_modules/',
    '<rootDir>/client/.next/',
    '<rootDir>/client/out/',
  ],
  
  // Transform ignore patterns
  transformIgnorePatterns: [
    '/node_modules/',
    '^.+\\.module\\.(css|sass|scss)$',
  ],
  
  // Verbose output
  verbose: true,
  
  // Bail on first failure in CI
  bail: process.env.CI ? 1 : 0,
  
  // Clear mocks between tests
  clearMocks: true,
  
  // Restore mocks after each test
  restoreMocks: true,
  
  // Maximum worker processes
  maxWorkers: process.env.CI ? 1 : '50%',
  
  // Test timeout
  testTimeout: 10000,
  
  // Setup files
  setupFiles: ['<rootDir>/client/jest.polyfills.js'],
  
  // Global setup
  globalSetup: '<rootDir>/client/jest.global-setup.js',
  
  // Global teardown
  globalTeardown: '<rootDir>/client/jest.global-teardown.js',
}

// createJestConfig is exported this way to ensure that next/jest can load the Next.js config which is async
module.exports = createJestConfig(customJestConfig)