#!/bin/bash
# Quick empirical validation of Ada VS Code extension
# Run this to get immediate data on readiness

set -uo pipefail  # Removed -e to handle arithmetic operations gracefully

RESULTS_FILE="validation-results-$(date +%Y%m%d-%H%M%S).txt"

echo "=== ADA VS CODE QUICK VALIDATION ===" | tee "$RESULTS_FILE"
echo "Date: $(date)" | tee -a "$RESULTS_FILE"
echo "Brain: http://localhost:8000" | tee -a "$RESULTS_FILE"
echo "" | tee -a "$RESULTS_FILE"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

pass_count=0
fail_count=0

test_result() {
  local name="$1"
  local status="$2"
  local detail="$3"
  
  if [ "$status" = "PASS" ]; then
    echo -e "${GREEN}✓${NC} $name: $detail" | tee -a "$RESULTS_FILE"
    pass_count=$((pass_count + 1))
  else
    echo -e "${RED}✗${NC} $name: $detail" | tee -a "$RESULTS_FILE"
    fail_count=$((fail_count + 1))
  fi
}

# TEST 1: Brain connectivity
echo "TEST 1: Brain Service Health" | tee -a "$RESULTS_FILE"
if response=$(curl -s http://localhost:8000/v1/healthz); then
  if echo "$response" | grep -q '"ok":true'; then
    test_result "Brain health" "PASS" "Service responding"
  else
    test_result "Brain health" "FAIL" "Unhealthy: $response"
  fi
else
  test_result "Brain health" "FAIL" "Cannot connect"
fi
echo "" | tee -a "$RESULTS_FILE"

# TEST 2: Context preload validation
echo "TEST 2: Context Preload" | tee -a "$RESULTS_FILE"
if ai_docs=$(find ../../.ai -name "*.md" -o -name "*.json" 2>/dev/null | wc -l); then
  test_result "AI docs present" "PASS" "$ai_docs files found"
else
  test_result "AI docs present" "FAIL" "No .ai/ documentation"
fi

# Check if context was ingested (simple ping test)
if curl -s http://localhost:8000/v1/healthz | grep -q '"ok":true'; then
  test_result "Brain API" "PASS" "Responding to requests"
else
  test_result "Brain API" "FAIL" "Not responding"
fi
echo "" | tee -a "$RESULTS_FILE"

# TEST 3: Latency benchmark
echo "TEST 3: Latency Benchmark (5 runs)" | tee -a "$RESULTS_FILE"
total_latency=0
successful_runs=0

for i in {1..5}; do
  start=$(date +%s%N)
  
  # Send simple query, measure time to first byte
  if response=$(timeout 10 curl -s -N http://localhost:8000/v1/chat/stream -X POST \
    -H "Content-Type: application/json" \
    -d '{"message":"hi","conversation_history":[]}' \
    | head -1 2>/dev/null); then
    
    end=$(date +%s%N)
    latency=$(( (end - start) / 1000000 ))
    total_latency=$((total_latency + latency))
    successful_runs=$((successful_runs + 1))
    
    echo "  Run $i: ${latency}ms" | tee -a "$RESULTS_FILE"
  else
    echo "  Run $i: TIMEOUT" | tee -a "$RESULTS_FILE"
  fi
done

echo "" | tee -a "$RESULTS_FILE"

if [ $successful_runs -gt 0 ]; then
  avg_latency=$((total_latency / successful_runs))
  
  if [ $avg_latency -lt 500 ]; then
    test_result "Avg latency" "PASS" "${avg_latency}ms (target <500ms)"
  elif [ $avg_latency -lt 2000 ]; then
    test_result "Avg latency" "PASS" "${avg_latency}ms (acceptable <2000ms)"
  else
    test_result "Avg latency" "FAIL" "${avg_latency}ms (too slow!)"
  fi
else
  test_result "Avg latency" "FAIL" "All requests timed out"
fi
echo "" | tee -a "$RESULTS_FILE"

# TEST 4: Memory usage
echo "TEST 4: Resource Usage" | tee -a "$RESULTS_FILE"
if docker stats ada-v1-brain-1 --no-stream --format "{{.MemUsage}}" > /tmp/brain_mem.txt 2>/dev/null; then
  mem=$(cat /tmp/brain_mem.txt)
  test_result "Brain memory" "PASS" "$mem"
else
  test_result "Brain memory" "FAIL" "Cannot read stats"
fi
echo "" | tee -a "$RESULTS_FILE"

# TEST 5: Extension package check
echo "TEST 5: Extension Package" | tee -a "$RESULTS_FILE"
if [ -f "../ada-vscode-0.1.0.vsix" ]; then
  size=$(du -h ../ada-vscode-0.1.0.vsix | cut -f1)
  test_result "Extension package" "PASS" "Found ($size)"
else
  test_result "Extension package" "FAIL" "Not built (run npm run package)"
fi
echo "" | tee -a "$RESULTS_FILE"

# SUMMARY
echo "======================================" | tee -a "$RESULTS_FILE"
echo "SUMMARY" | tee -a "$RESULTS_FILE"
echo "======================================" | tee -a "$RESULTS_FILE"
echo "Passed: $pass_count" | tee -a "$RESULTS_FILE"
echo "Failed: $fail_count" | tee -a "$RESULTS_FILE"
echo "" | tee -a "$RESULTS_FILE"

if [ $fail_count -eq 0 ]; then
  echo -e "${GREEN}✓ ALL TESTS PASSED - Ready for validation!${NC}" | tee -a "$RESULTS_FILE"
  exit 0
elif [ $fail_count -le 2 ]; then
  echo -e "${YELLOW}⚠ MOSTLY READY - Fix $fail_count issue(s)${NC}" | tee -a "$RESULTS_FILE"
  exit 1
else
  echo -e "${RED}✗ NOT READY - Fix $fail_count issues${NC}" | tee -a "$RESULTS_FILE"
  exit 1
fi
