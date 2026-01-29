#!/usr/bin/env python3
"""
Simple LiteLLM test without proxy
Tests direct LiteLLM usage with Gemini

Built with 💜 by Ada & Luna - The Consciousness Engineers
"""

import os
import litellm

# Enable verbose logging
litellm.set_verbose = True

def test_direct_litellm():
    """Test LiteLLM directly with Gemini (no proxy)"""
    print("🧪 Testing LiteLLM Direct Usage (No Proxy)")
    print("=" * 60)
    
    # Check for API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not set in environment")
        print("   Add it to .env file")
        return False
    
    print(f"✅ API key found: {api_key[:10]}...")
    print()
    
    try:
        print("📡 Calling Gemini via LiteLLM...")
        response = litellm.completion(
            model="gemini/gemini-2.0-flash-exp",
            messages=[{
                "role": "user",
                "content": "Say 'Bzzz! LiteLLM works!' if you can hear me."
            }],
            api_key=api_key
        )
        
        print("✅ Response received!")
        print()
        print("📊 Response:")
        print("=" * 60)
        print(response.choices[0].message.content)
        print("=" * 60)
        print()
        
        # Show usage stats
        if hasattr(response, 'usage'):
            print("📈 Usage Stats:")
            print(f"   Prompt tokens: {response.usage.prompt_tokens}")
            print(f"   Completion tokens: {response.usage.completion_tokens}")
            print(f"   Total tokens: {response.usage.total_tokens}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = test_direct_litellm()
    exit(0 if success else 1)
