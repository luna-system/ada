#!/usr/bin/env python3
"""
Quick demo script showing the wiki specialist in action!

This demonstrates how Ada can look up information from wikis
to answer questions about fandoms, shows, characters, and more.
"""

from brain.specialists.wiki_specialist import WikiSpecialist, WIKI_CONFIGS

def main():
    wiki = WikiSpecialist()
    
    print("🌟 Wiki Specialist Demo 🌟\n")
    print(f"Available wikis: {', '.join(WIKI_CONFIGS.keys())}\n")
    print("=" * 60)
    
    # Test 1: Wikipedia lookup
    print("\n📚 Example 1: Wikipedia - Python Programming Language")
    print("-" * 60)
    result = wiki.process({
        'wiki': 'wikipedia',
        'page': 'Python (programming language)'
    })
    if result.success:
        print(result.context_text[:300] + "...")
    else:
        print(f"Error: {result.error}")
    
    # Test 2: BFDI wiki lookup
    print("\n\n🎬 Example 2: BFDI Wiki - Battle for Dream Island")
    print("-" * 60)
    result = wiki.process({
        'wiki': 'bfdi',
        'page': 'Battle for Dream Island'
    })
    if result.success:
        print(result.context_text[:300] + "...")
    else:
        print(f"Error: {result.error}")
    
    # Test 3: Character lookup
    print("\n\n🎭 Example 3: BFDI Wiki - Character (Four)")
    print("-" * 60)
    result = wiki.process({
        'wiki': 'bfdi',
        'page': 'Four'
    })
    if result.success:
        print(result.context_text[:300] + "...")
    else:
        print(f"Error: {result.error}")
    
    # Test 4: Search suggestions
    print("\n\n🔍 Example 4: Typo with search suggestions")
    print("-" * 60)
    result = wiki.process({
        'wiki': 'bfdi',
        'page': 'Battl for Drem Islnd'  # Intentional typos
    })
    print(result.context_text)
    if 'suggestions' in result.metadata:
        print(f"\nSuggestions: {', '.join(result.metadata['suggestions'])}")
    
    print("\n" + "=" * 60)
    print("\n💡 How Ada uses this:")
    print("   User: 'Tell me about Four from BFDI'")
    print("   Ada internally calls: wiki_lookup(wiki='bfdi', page='Four')")
    print("   Then responds with the wiki information!")
    print("\n✨ Perfect for helping with fandom questions! ✨\n")

if __name__ == "__main__":
    main()
