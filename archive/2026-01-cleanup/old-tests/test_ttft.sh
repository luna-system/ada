#!/bin/bash
# Test TTFT timing instrumentation

echo "Testing TTFT with query: 'what modules are in this project?'"
echo "---"

curl -X POST http://localhost:8000/v1/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "message": "what modules are in this project?",
    "conversation_id": "ttft-test",
    "stream": true
  }' \
  2>&1 | head -n 5

echo ""
echo "---"
echo "Check docker logs for timing breakdown:"
echo "  docker compose logs brain --tail=50 | grep 'Request.*ms'"
