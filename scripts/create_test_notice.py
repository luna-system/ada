#!/usr/bin/env python3
"""
Quick script to create test notices for development.
Usage: python scripts/create_test_notice.py [severity] [component] [code]
"""
import sys
import urllib.request
import json

def create_notice(severity="warning", component="test", code="dev_test"):
    """Create a test notice via the API."""
    url = "http://localhost:7000/v1/notices"
    
    messages = {
        "warning": f"This is a test {severity} notice from the development script.",
        "error": f"CRITICAL: This is a test {severity} notice. Something needs attention!",
        "info": f"FYI: This is a test {severity} notice for informational purposes.",
    }
    
    payload = {
        "severity": severity,
        "component": component,
        "code": code,
        "message": messages.get(severity, f"Test notice: {component}.{code}")
    }
    
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            result = json.loads(response.read().decode('utf-8'))
            print(f"✓ Created notice: {result['id']}")
            print(f"  Severity: {severity}")
            print(f"  Component: {component}.{code}")
            return result['id']
    except Exception as e:
        print(f"✗ Failed to create notice: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    severity = sys.argv[1] if len(sys.argv) > 1 else "warning"
    component = sys.argv[2] if len(sys.argv) > 2 else "test"
    code = sys.argv[3] if len(sys.argv) > 3 else "dev_notice"
    
    if severity not in ["info", "warning", "error"]:
        print(f"Invalid severity: {severity}. Use: info, warning, or error")
        sys.exit(1)
    
    create_notice(severity, component, code)
