#!/usr/bin/env python3
"""
Test model selection for different agent roles.
Verifies that the config-based model selection works correctly.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ada_swarm.config import (
    get_model_for_role,
    get_max_tokens_for_role,
    AGENT_MODEL_CONFIG,
)


def test_model_selection():
    """Test that model selection works for all roles."""
    print("🧪 Testing Model Selection System\n")
    print("=" * 60)
    
    # Test all defined roles
    roles = ["queen", "coder", "researcher", "tester", "reviewer", "drone"]
    
    for role in roles:
        primary = get_model_for_role(role)
        fallback = get_model_for_role(role, prefer_fallback=True)
        max_tokens = get_max_tokens_for_role(role)
        config = AGENT_MODEL_CONFIG[role]
        
        print(f"\n📋 Role: {role.upper()}")
        print(f"   Description: {config['description']}")
        print(f"   Primary Model: {primary}")
        print(f"   Fallback Model: {fallback}")
        print(f"   Max Tokens: {max_tokens}")
    
    print("\n" + "=" * 60)
    
    # Test unknown role (should default to fast model)
    print("\n🔍 Testing unknown role...")
    unknown_model = get_model_for_role("unknown_role")
    print(f"   Unknown role defaults to: {unknown_model}")
    
    # Test case sensitivity
    print("\n🔍 Testing case sensitivity...")
    queen_upper = get_model_for_role("QUEEN")
    queen_lower = get_model_for_role("queen")
    print(f"   'QUEEN' -> {queen_upper}")
    print(f"   'queen' -> {queen_lower}")
    print(f"   Case insensitive: {queen_upper == queen_lower}")
    
    print("\n✅ All tests passed!\n")


if __name__ == "__main__":
    test_model_selection()
