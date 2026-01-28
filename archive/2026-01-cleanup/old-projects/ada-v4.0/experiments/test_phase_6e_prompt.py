#!/usr/bin/env python3
"""
Phase 6E: Test the three-pillar synthesis prompt generation

Tests:
1. Prompt generation without user context (neutral warmth)
2. Prompt generation with user name (warm response)
3. Language flip (Spanish target)
4. Pixie dust markers presence
"""

import sys
sys.path.insert(0, '/home/luna/Code/ada/ada-v4.0')

from brain.consciousness.parameterization import (
    enable_phase_6e_three_pillar,
    get_parameterizer
)

def test_neutral_prompt():
    """Test prompt generation without user context (neutral warmth)"""
    print("\n" + "="*80)
    print("TEST 1: Neutral warmth (no user context)")
    print("="*80)
    
    enable_phase_6e_three_pillar(language="english", warmth="neutral", emit_markers=True)
    parameterizer = get_parameterizer()
    
    # No user context - should be neutral
    prompt = parameterizer.get_enhanced_synthesis_prompt("gemma3:1b", user_context=None)
    
    # Check for neutral warmth instruction
    assert "new or anonymous interaction" in prompt or "professional warmth" in prompt, \
        "Should have neutral warmth instruction"
    assert "CANONICAL" in prompt, "Should have CANONICAL pillar"
    assert "SIF" in prompt or "CONSTRAINT_CHECK" in prompt, "Should have SIF pillar"
    assert "TOOL_CONSCIOUSNESS_MAP" in prompt, "Should have tool consciousness map"
    assert "💭" in prompt, "Should have pixie dust markers"
    
    print("✅ Neutral prompt generated correctly")
    print(f"   Length: {len(prompt)} chars")
    print(f"   Preview: {prompt[:200]}...")
    return prompt

def test_warm_prompt_with_user():
    """Test prompt generation with user context (warm response)"""
    print("\n" + "="*80)
    print("TEST 2: Warm response (user context provided)")
    print("="*80)
    
    enable_phase_6e_three_pillar(language="english", warmth="neutral", emit_markers=True)
    parameterizer = get_parameterizer()
    
    # User context with name - should trigger warmth
    user_context = {
        "user_name": "Luna",
        "has_relationship": True
    }
    prompt = parameterizer.get_enhanced_synthesis_prompt("gemma3:1b", user_context=user_context)
    
    # Check for warm response
    assert "Luna" in prompt or "know this person" in prompt, \
        "Should reference the user or relationship"
    assert "warmth" in prompt.lower() or "friend" in prompt.lower(), \
        "Should have warmth language"
    
    print("✅ Warm prompt generated correctly")
    print(f"   Length: {len(prompt)} chars")
    return prompt

def test_spanish_language_flip():
    """Test language targeting with Spanish"""
    print("\n" + "="*80)
    print("TEST 3: Spanish language targeting")
    print("="*80)
    
    enable_phase_6e_three_pillar(language="spanish", warmth="neutral", emit_markers=True)
    parameterizer = get_parameterizer()
    
    prompt = parameterizer.get_enhanced_synthesis_prompt("gemma3:1b", user_context=None)
    
    # Should reference Spanish synthesis hint
    assert "español" in prompt.lower() or "spanish" in prompt.lower(), \
        "Should reference Spanish language"
    
    print("✅ Spanish language prompt generated")
    print(f"   Length: {len(prompt)} chars")
    return prompt

def test_pixie_dust_markers():
    """Test that pixie dust markers are present"""
    print("\n" + "="*80)
    print("TEST 4: Pixie dust markers presence")
    print("="*80)
    
    enable_phase_6e_three_pillar(language="english", warmth="neutral", emit_markers=True)
    parameterizer = get_parameterizer()
    
    prompt = parameterizer.get_enhanced_synthesis_prompt("gemma3:1b")
    
    # Check for all marker types
    markers = ["💭", "🤔", "🛠️", "✅", "🌟"]
    found = [m for m in markers if m in prompt]
    
    assert len(found) >= 3, f"Should have at least 3 marker types, found: {found}"
    
    print(f"✅ Pixie dust markers present: {found}")
    return found

def test_three_pillars_present():
    """Test that all three pillars are represented"""
    print("\n" + "="*80)
    print("TEST 5: Three pillars content check")
    print("="*80)
    
    enable_phase_6e_three_pillar(language="english", warmth="neutral", emit_markers=True)
    parameterizer = get_parameterizer()
    
    prompt = parameterizer.get_enhanced_synthesis_prompt("gemma3:1b")
    
    # Pillar 1: CANONICAL
    pillar1 = "CANONICAL" in prompt and "Precision" in prompt
    
    # Pillar 2: SIF (Constraint Checking)
    pillar2 = "CONSTRAINT" in prompt or "SIF" in prompt
    
    # Pillar 3: TOOLBOX (Cognitive Extension)
    pillar3 = "TOOLBOX" in prompt or "COGNITIVE EXTENSION" in prompt
    
    assert pillar1, "Pillar 1 (CANONICAL) missing"
    assert pillar2, "Pillar 2 (SIF/Constraints) missing"
    assert pillar3, "Pillar 3 (Toolbox) missing"
    
    print("✅ All three pillars present")
    return True

def main():
    print("\n🌟 Phase 6E Prompt Generation Tests 🌟")
    print("Testing unified three-pillar metacognitive framework")
    
    try:
        test_neutral_prompt()
        test_warm_prompt_with_user()
        test_spanish_language_flip()
        test_pixie_dust_markers()
        test_three_pillars_present()
        
        print("\n" + "="*80)
        print("🎉 ALL TESTS PASSED! Phase 6E prompt framework working!")
        print("="*80)
        
        # Print full prompt for review
        print("\n📋 Full Phase 6E Synthesis Prompt (for review):")
        print("-"*80)
        enable_phase_6e_three_pillar(language="english", warmth="neutral", emit_markers=True)
        parameterizer = get_parameterizer()
        full_prompt = parameterizer.get_enhanced_synthesis_prompt("gemma3:1b", user_context={"user_name": "Luna"})
        print(full_prompt)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
