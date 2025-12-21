#!/usr/bin/env bash
# Test script for validating Nix setup and Ada flake
# Run this after setting up Nix to verify everything works

set -e  # Exit on error

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🧪 Ada Nix Setup Validator"
echo "=========================="
echo ""

# Test 1: Check Nix is installed
echo -n "1. Checking Nix installation... "
if command -v nix &> /dev/null; then
    echo -e "${GREEN}✓${NC}"
    nix --version
else
    echo -e "${RED}✗${NC}"
    echo "   Nix not found. Install from https://nixos.org/download"
    exit 1
fi
echo ""

# Test 2: Check flakes are enabled
echo -n "2. Checking flakes enabled... "
if nix flake --version &> /dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    echo "   Enable flakes:"
    echo "   mkdir -p ~/.config/nix"
    echo "   echo 'experimental-features = nix-command flakes' >> ~/.config/nix/nix.conf"
    exit 1
fi
echo ""

# Test 3: Check user in nix-users group
echo -n "3. Checking nix-users group... "
if groups | grep -q nix-users; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${YELLOW}⚠${NC}"
    echo "   You're not in nix-users group. This might cause permission issues."
    echo "   Fix with: sudo usermod -aG nix-users $USER"
    echo "   Then log out and back in."
fi
echo ""

# Test 4: Check nix-daemon is running
echo -n "4. Checking nix-daemon... "
if systemctl is-active --quiet nix-daemon 2>/dev/null; then
    echo -e "${GREEN}✓${NC}"
elif pgrep -x nix-daemon > /dev/null; then
    echo -e "${GREEN}✓${NC} (running but not via systemd)"
else
    echo -e "${YELLOW}⚠${NC}"
    echo "   Daemon not running. Start with:"
    echo "   sudo systemctl enable --now nix-daemon"
fi
echo ""

# Test 5: Validate flake.nix syntax
echo -n "5. Validating flake.nix... "
if [ -f "flake.nix" ]; then
    if nix flake check --no-build 2>/dev/null; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗${NC}"
        echo "   Flake validation failed. Run: nix flake check"
        exit 1
    fi
else
    echo -e "${RED}✗${NC}"
    echo "   flake.nix not found. Are you in the Ada directory?"
    exit 1
fi
echo ""

# Test 6: Show flake outputs
echo "6. Flake outputs:"
nix flake show 2>/dev/null || echo "   (Unable to show outputs)"
echo ""

# Test 7: Try to enter dev shell (dry run)
echo -n "7. Testing nix develop (dry run)... "
if nix develop --dry-run &> /dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    echo "   Dev shell dry run failed. Try: nix flake update"
    exit 1
fi
echo ""

# Test 8: Check Python availability in flake
echo "8. Checking Python in dev shell..."
if nix develop --command python --version 2>/dev/null; then
    echo -e "   ${GREEN}✓${NC} Python available"
else
    echo -e "   ${YELLOW}⚠${NC} Could not verify Python (might need to enter shell manually)"
fi
echo ""

# Test 9: Check all required tools
echo "9. Checking dev shell tools..."
for tool in python ollama ada git curl jq; do
    if nix develop --command which $tool &> /dev/null; then
        echo -e "   ${GREEN}✓${NC} $tool"
    else
        echo -e "   ${YELLOW}⚠${NC} $tool (might not be in PATH)"
    fi
done
echo ""

# Test 10: Locale check
echo -n "10. Checking locale configuration... "
if locale | grep -q "LC_ALL=C.UTF-8\|LANG=.*UTF-8"; then
    echo -e "${GREEN}✓${NC}"
elif nix develop --command bash -c 'echo $LC_ALL' | grep -q "C.UTF-8"; then
    echo -e "${GREEN}✓${NC} (set by flake)"
else
    echo -e "${YELLOW}⚠${NC}"
    echo "    Locale might cause issues. Flake sets LC_ALL=C.UTF-8 automatically."
fi
echo ""

echo "=============================="
echo -e "${GREEN}✓ Basic validation passed!${NC}"
echo ""
echo "Next steps:"
echo "  1. Enter dev shell:  nix develop"
echo "  2. Start Ollama:     ollama serve &"
echo "  3. Pull model:       ollama pull qwen2.5-coder:7b"
echo "  4. Setup Ada:        ada setup"
echo "  5. Run Ada:          ada run"
echo ""
echo "For automatic activation, use direnv:"
echo "  direnv allow"
echo ""
echo "Need help? See docs/zero_to_ada.rst"
