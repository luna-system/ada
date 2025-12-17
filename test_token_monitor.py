#!/usr/bin/env python
"""Quick test of token monitoring integration."""
import sys
sys.path.insert(0, '/home/luna/Code/ada-v1')

# Mock the dependencies we don't need
import unittest.mock as mock
sys.modules['chromadb'] = mock.MagicMock()

from brain.config import config
print(f"✅ Config loaded")
print(f"  TOKEN_MONITORING_ENABLED: {config.TOKEN_MONITORING_ENABLED}")
print(f"  LLM_MAX_CONTEXT: {config.LLM_MAX_CONTEXT}")
print(f"  TOKEN_WARNING_THRESHOLD: {config.TOKEN_WARNING_THRESHOLD}")

from brain.token_monitor import TokenBudgetMonitor
print(f"✅ TokenBudgetMonitor imported")

# Test basic functionality
monitor = TokenBudgetMonitor(max_tokens=1000, warning_threshold=0.8)
monitor.track("test_section", "Hello world " * 50)  # ~150 words
breakdown = monitor.get_breakdown()

print(f"✅ Monitor works")
print(f"  Tracked tokens: {breakdown.total_tokens}")
print(f"  Usage: {breakdown.percentage_used:.1f}%")
print(f"  Warning: {breakdown.is_warning}")

print("\n🌱 Token monitoring integration ready!")
