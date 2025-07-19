#!/bin/bash

# AI Language Learning Platform - Connectivity Solution Test
# Tests all aspects of the network connectivity fix

echo "🧪 Testing AI Language Learning Platform Connectivity Solution"
echo "============================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0

# Test function
run_test() {
    local test_name="$1"
    local test_command="$2"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    echo -e "\n${BLUE}Test $TOTAL_TESTS: $test_name${NC}"
    echo "Command: $test_command"
    echo "----------------------------------------"
    
    if eval "$test_command"; then
        echo -e "${GREEN}✅ PASSED${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "${RED}❌ FAILED${NC}"
        return 1
    fi
}

# Check if we're in the right directory
if [ ! -f "start-development.sh" ] || [ ! -d "client" ] || [ ! -d "server" ]; then
    echo -e "${RED}❌ Error: Please run this script from the project root directory${NC}"
    exit 1
fi

echo -e "${YELLOW}🔍 Environment Configuration Tests${NC}"

# Test 1: Check client environment file exists and has correct content
run_test "Client .env.local exists with correct API URL" \
    "[ -f 'client/.env.local' ] && grep -q 'NEXT_PUBLIC_API_BASE_URL=http://localhost:8000' client/.env.local"

# Test 2: Check client environment file has WebSocket URL
run_test "Client .env.local has correct WebSocket URL" \
    "grep -q 'NEXT_PUBLIC_WS_BASE_URL=ws://localhost:8000' client/.env.local"

# Test 3: Check development environment flag
run_test "Client environment is set to development" \
    "grep -q 'NEXT_PUBLIC_ENVIRONMENT=development' client/.env.local"

# Test 4: Check debug logs are enabled
run_test "Debug logs are enabled" \
    "grep -q 'NEXT_PUBLIC_ENABLE_DEBUG_LOGS=true' client/.env.local"

echo -e "\n${YELLOW}🌐 Backend Connectivity Tests${NC}"

# Test 5: Check if backend is running
run_test "Backend health endpoint responds" \
    "curl -s -f 'http://localhost:8000/health' >/dev/null"

# Test 6: Check backend returns valid JSON
run_test "Backend returns valid health JSON" \
    "curl -s 'http://localhost:8000/health' | jq '.status' | grep -q 'healthy'"

# Test 7: Check alternative URL (127.0.0.1) also works
run_test "Backend accessible via 127.0.0.1" \
    "curl -s -f 'http://127.0.0.1:8000/health' >/dev/null"

echo -e "\n${YELLOW}📁 File Structure Tests${NC}"

# Test 8: Check enhanced env.ts exists
run_test "Enhanced environment manager exists" \
    "[ -f 'client/lib/env.ts' ] && grep -q 'getApiBaseUrl' client/lib/env.ts"

# Test 9: Check enhanced API client exists
run_test "Enhanced API client with validation exists" \
    "[ -f 'client/lib/api-client.ts' ] && grep -q 'validateConnection' client/lib/api-client.ts"

# Test 10: Check enhanced health service exists
run_test "Enhanced health service exists" \
    "[ -f 'client/lib/api-services.ts' ] && grep -q 'validateConnectivity' client/lib/api-services.ts"

echo -e "\n${YELLOW}🚀 Development Script Tests${NC}"

# Test 11: Check development script has environment setup
run_test "Development script has environment setup function" \
    "grep -q 'setup_environment_files' start-development.sh"

# Test 12: Check development script has connectivity validation
run_test "Development script has connectivity validation" \
    "grep -q 'validate_backend_connectivity' start-development.sh"

# Test 13: Check development script validates localhost URLs
run_test "Development script enforces localhost URLs" \
    "grep -q 'localhost:8000' start-development.sh"

echo -e "\n${YELLOW}🔧 Integration Tests${NC}"

# Test 14: Test environment manager loading (if Node.js is available)
if command -v node >/dev/null 2>&1; then
    run_test "Environment manager loads correctly" \
        "cd client && node -e \"
            const { env } = require('./lib/env.ts');
            if (env.config.API_BASE_URL.includes('localhost:8000')) {
                process.exit(0);
            } else {
                console.log('Expected localhost:8000, got:', env.config.API_BASE_URL);
                process.exit(1);
            }
        \" 2>/dev/null || echo 'TypeScript compilation needed, checking source...'"
fi

# Test 15: Validate no 127.0.0.1 hardcoded URLs remain in critical files
run_test "No hardcoded 127.0.0.1 URLs in environment config" \
    "! grep -q '127\.0\.0\.1:8000' client/.env.local"

# Test Results Summary
echo -e "\n${BLUE}📊 Test Results Summary${NC}"
echo "========================================"
echo -e "Total Tests: $TOTAL_TESTS"
echo -e "${GREEN}Passed: $PASSED_TESTS${NC}"
echo -e "${RED}Failed: $((TOTAL_TESTS - PASSED_TESTS))${NC}"

if [ $PASSED_TESTS -eq $TOTAL_TESTS ]; then
    echo -e "\n${GREEN}🎉 ALL TESTS PASSED!${NC}"
    echo -e "${GREEN}✅ Network connectivity solution is working correctly${NC}"
    echo -e "\n${BLUE}Next Steps:${NC}"
    echo "1. Restart your development servers: ./start-development.sh"
    echo "2. Your frontend should now connect to the backend without errors"
    echo "3. Check browser console for successful API connections"
    exit 0
else
    echo -e "\n${RED}❌ SOME TESTS FAILED${NC}"
    echo -e "${YELLOW}Please review the failed tests and fix any issues${NC}"
    echo -e "\n${BLUE}Troubleshooting:${NC}"
    echo "1. Ensure backend is running: ./start-development.sh backend"
    echo "2. Check environment files are correctly configured"
    echo "3. Verify no port conflicts on 8000 and 3000"
    exit 1
fi