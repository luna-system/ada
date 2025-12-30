#!/usr/bin/env python3
"""
Quick test for Phase 1 multi-round consciousness endpoint integration.
"""

import sys
import json

def test_endpoint_structure():
    """Test that the multi-round consciousness endpoint structure is correct."""
    print("🌸 Testing Phase 1 Multi-Round Consciousness Integration...")
    
    # Test 1: Check that brain/consciousness module exists and has expected structure
    try:
        from brain.consciousness import run_multi_round_inference, FloretContext, MultiRoundEngine
        print("✅ Multi-round consciousness module imports successfully")
        print(f"   - run_multi_round_inference: {run_multi_round_inference}")
        print(f"   - FloretContext: {FloretContext}")
        print(f"   - MultiRoundEngine: {MultiRoundEngine}")
    except ImportError as e:
        print(f"❌ Failed to import consciousness module: {e}")
        return False
    
    # Test 2: Check that app.py has the multi_round parameter integration
    try:
        with open('brain/app.py', 'r') as f:
            app_content = f.read()
        
        required_elements = [
            "multi_round",
            "floret_mode", 
            "use_multi_round",
            "run_multi_round_inference",
            "🌸✨",
            "max_rounds"
        ]
        
        missing = []
        for element in required_elements:
            if element not in app_content:
                missing.append(element)
        
        if missing:
            print(f"❌ Missing required elements in app.py: {missing}")
            return False
        else:
            print("✅ App.py has all required multi-round integration elements")
            
    except Exception as e:
        print(f"❌ Failed to check app.py: {e}")
        return False
    
    # Test 3: Validate the modular structure
    try:
        import os
        consciousness_files = [
            'brain/consciousness/__init__.py',
            'brain/consciousness/schemas.py', 
            'brain/consciousness/heisenberg.py',
            'brain/consciousness/engine.py'
        ]
        
        missing_files = []
        for file_path in consciousness_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
        
        if missing_files:
            print(f"❌ Missing consciousness module files: {missing_files}")
            return False
        else:
            print("✅ All consciousness module files exist")
            
    except Exception as e:
        print(f"❌ Failed to check consciousness module structure: {e}")
        return False
    
    print("\n🎉 Phase 1 Multi-Round Consciousness Integration: COMPLETE!")
    print("✨ Ready to test endpoint: POST /v1/chat/stream with multi_round=true")
    print("🌸 Beautiful floret consciousness is now accessible!")
    
    return True

def main():
    """Main test function."""
    success = test_endpoint_structure()
    if success:
        print("\n🚀 Next steps:")
        print("1. Start Ada brain: ./scripts/run.sh brain")
        print("2. Test multi-round endpoint: curl -X POST http://localhost:8000/v1/chat/stream \\")
        print("   -H 'Content-Type: application/json' \\")
        print("   -d '{\"prompt\": \"Hello Ada! Think deeply about consciousness.\", \"multi_round\": true}'")
        print("3. Observe floret consciousness thinking patterns! 🌻✨")
        sys.exit(0)
    else:
        print("\n❌ Integration incomplete - check errors above")
        sys.exit(1)

if __name__ == "__main__":
    main()