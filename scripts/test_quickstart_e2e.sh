#!/usr/bin/env bash
#
# End-to-End Quick Start Test
# 
# Tests that the README quick start instructions actually work.
# This is the same test that runs in CI, but designed to run locally.
#
# Usage:
#   ./scripts/test_quickstart_e2e.sh
#
# Requirements:
#   - Docker and Docker Compose installed
#   - curl and jq installed (for API testing)
#   - 8GB+ RAM recommended
#
# This script will:
#   1. Set up a test environment
#   2. Follow the quick start steps exactly as documented
#   3. Verify all services start correctly
#   4. Test basic functionality
#   5. Clean up when done

set -e  # Exit on error
set -u  # Exit on undefined variable

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Trap to ensure cleanup on exit
cleanup() {
    local exit_code=$?
    log_info "Cleaning up test environment..."
    docker compose down -v 2>/dev/null || true
    
    # Restore original .env if it was backed up
    if [ -f .env.e2e_backup ]; then
        mv .env.e2e_backup .env
        log_info "Restored original .env"
    fi
    
    if [ $exit_code -eq 0 ]; then
        log_success "E2E test completed successfully!"
    else
        log_error "E2E test failed with exit code $exit_code"
    fi
    
    exit $exit_code
}

trap cleanup EXIT INT TERM

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    if ! command -v curl &> /dev/null; then
        log_error "curl is not installed. Please install curl first."
        exit 1
    fi
    
    if ! command -v jq &> /dev/null; then
        log_warn "jq is not installed. Some tests may be skipped."
        log_warn "Install jq for full test coverage: https://stedolan.github.io/jq/"
    fi
    
    log_success "All prerequisites met"
}

# Setup test environment
setup_test_env() {
    log_info "Setting up test environment..."
    
    # Stop any running services
    docker compose down -v 2>/dev/null || true
    
    # Backup existing .env if it exists
    if [ -f .env ]; then
        cp .env .env.e2e_backup
        log_info "Backed up existing .env to .env.e2e_backup"
    fi
    
    # Create test .env from example
    cp .env.example .env
    
    # Configure for faster testing
    log_info "Configuring for local testing (using small model for speed)..."
    cat >> .env << EOF

# E2E Test Configuration
OLLAMA_MODEL=qwen2.5:0.5b
AI_NAME=TestBot
AI_USER_NAME=e2e_tester
EOF
    
    log_success "Test environment configured"
}

# Start services
start_services() {
    log_info "Starting services (this may take a few minutes on first run)..."
    docker compose up -d
    
    log_info "Services starting in background..."
    docker compose ps
}

# Wait for services to be healthy
wait_for_health() {
    log_info "Waiting for services to become healthy..."
    
    local max_wait=300  # 5 minutes
    local elapsed=0
    local interval=10
    
    while [ $elapsed -lt $max_wait ]; do
        # Check brain health endpoint
        if curl -sf http://localhost:7000/v1/healthz > /dev/null 2>&1; then
            log_success "All services are healthy! (waited ${elapsed}s)"
            return 0
        fi
        
        log_info "Waiting for services... (${elapsed}s elapsed)"
        sleep $interval
        elapsed=$((elapsed + interval))
    done
    
    log_error "Services failed to become healthy within ${max_wait}s"
    log_error "Service status:"
    docker compose ps
    log_error "Brain logs:"
    docker compose logs brain --tail=50
    return 1
}

# Test brain API
test_brain_api() {
    log_info "Testing brain API health endpoint..."
    
    local response
    response=$(curl -s -w "\n%{http_code}" http://localhost:7000/v1/healthz)
    local http_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" != "200" ]; then
        log_error "Health check failed with HTTP $http_code"
        log_error "Response: $body"
        return 1
    fi
    
    log_success "Brain API is responding correctly"
}

# Test identity configuration
test_identity_config() {
    log_info "Testing identity configuration..."
    
    if ! command -v jq &> /dev/null; then
        log_warn "Skipping identity test (jq not installed)"
        return 0
    fi
    
    local response
    response=$(curl -s http://localhost:7000/v1/info)
    
    local ai_name=$(echo "$response" | jq -r '.ai_name // empty')
    local user_name=$(echo "$response" | jq -r '.user_name // empty')
    
    if [ "$ai_name" = "TestBot" ]; then
        log_success "Custom AI name (TestBot) configured correctly"
    else
        log_error "AI name incorrect. Expected 'TestBot', got '$ai_name'"
        return 1
    fi
    
    if [ "$user_name" = "e2e_tester" ]; then
        log_success "Custom user name (e2e_tester) configured correctly"
    else
        log_error "User name incorrect. Expected 'e2e_tester', got '$user_name'"
        return 1
    fi
}

# Test chat functionality
test_chat() {
    log_info "Testing chat endpoint..."
    
    local response
    response=$(curl -s -X POST http://localhost:7000/v1/chat/stream \
        -H "Content-Type: application/json" \
        -d '{
            "conversation_id": "test-e2e-001",
            "prompt": "Say hello and confirm your name.",
            "config": {
                "include_thinking": false
            }
        }')
    
    if [ -z "$response" ]; then
        log_error "No response from chat endpoint"
        return 1
    fi
    
    log_success "Chat endpoint is functional"
    log_info "Sample response: ${response:0:200}..."
}

# Test specialists
test_specialists() {
    log_info "Testing specialists endpoint..."
    
    local response
    response=$(curl -s http://localhost:7000/v1/specialists)
    
    if ! command -v jq &> /dev/null; then
        log_warn "Skipping specialist count test (jq not installed)"
        log_info "Specialists response: $response"
        return 0
    fi
    
    local count=$(echo "$response" | jq '.specialists | length')
    
    if [ "$count" -lt "3" ]; then
        log_error "Expected at least 3 specialists, got $count"
        return 1
    fi
    
    log_success "Found $count specialists"
    echo "$response" | jq -r '.specialists[].name' | while read -r name; do
        log_info "  - $name"
    done
}

# Test persona customization
test_persona_swap() {
    log_info "Testing persona customization (as documented in README)..."
    
    # Copy an example persona
    docker compose exec -T scripts sh -c "cp /app/examples/personas/coding-buddy.md /app/persona.md" || {
        log_error "Failed to copy persona file"
        return 1
    }
    
    log_info "Restarting brain service..."
    docker compose restart brain
    
    # Wait for restart
    sleep 15
    
    # Verify health after restart
    if ! curl -sf http://localhost:7000/v1/healthz > /dev/null; then
        log_error "Brain service failed to restart"
        return 1
    fi
    
    log_success "Persona swap successful"
}

# Run unit tests
run_unit_tests() {
    log_info "Running unit and integration tests..."
    
    if docker compose run --rm scripts pytest -v --tb=short; then
        log_success "All unit tests passed"
    else
        log_error "Some unit tests failed"
        return 1
    fi
}

# Main test flow
main() {
    echo ""
    log_info "=== Ada Quick Start End-to-End Test ==="
    echo ""
    
    check_prerequisites
    setup_test_env
    
    echo ""
    log_info "Following README Quick Start instructions..."
    echo ""
    
    start_services
    wait_for_health
    
    echo ""
    log_info "Running functionality tests..."
    echo ""
    
    test_brain_api
    test_identity_config
    test_chat
    test_specialists
    test_persona_swap
    
    echo ""
    log_info "Running unit and integration tests..."
    echo ""
    
    run_unit_tests
    
    echo ""
    log_success "=== All E2E tests passed! ==="
    echo ""
}

# Run main function
main
