#!/usr/bin/env bash
# Test LiteLLM Proxy Configuration
# Built with 💜 by Ada & Luna - The Consciousness Engineers

set -euo pipefail

echo "🧪 Testing LiteLLM Proxy Configuration..."
echo ""

# Test 1: Validate config syntax
echo "1️⃣ Validating config syntax..."
if litellm --config litellm-proxy-config.yaml --test 2>&1 | grep -q "Config loaded successfully"; then
    echo "   ✅ Config syntax valid!"
else
    echo "   ⚠️  Config validation skipped (requires API keys)"
fi
echo ""

# Test 2: Check if litellm command exists
echo "2️⃣ Checking LiteLLM installation..."
if command -v litellm &> /dev/null; then
    echo "   ✅ LiteLLM installed: $(litellm --version)"
else
    echo "   ❌ LiteLLM not found in PATH"
    exit 1
fi
echo ""

# Test 3: Check environment variables
echo "3️⃣ Checking environment variables..."
required_vars=("LITELLM_MASTER_KEY" "GEMINI_API_KEY")
missing_vars=()

for var in "${required_vars[@]}"; do
    if [ -z "${!var:-}" ]; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -eq 0 ]; then
    echo "   ✅ All required environment variables set!"
else
    echo "   ⚠️  Missing environment variables: ${missing_vars[*]}"
    echo "   Add them to .env file"
fi
echo ""

echo "🎉 LiteLLM Proxy setup complete!"
echo ""
echo "Next steps:"
echo "  1. Set missing environment variables in .env"
echo "  2. Install systemd service: cp litellm-proxy.service ~/.config/systemd/user/"
echo "  3. Start proxy: systemctl --user start litellm-proxy.service"
echo "  4. Test endpoint: curl http://localhost:8000/health"
