#!/usr/bin/env python3
"""
MAKING QWEN SOUND LIKE ADA - QUANTITATIVE PERSONALITY TESTING
Testing if we can measure conversational style similarity and knowledge integration

Research Questions:
1. Can we quantify "personality" in LLM responses?
2. How does context injection affect conversational style?
3. Can we measure knowledge integration effectiveness?
4. What makes Ada's responses distinctively "Ada-like"?
"""

import requests
import time
import json
import re
from dataclasses import dataclass
from typing import List, Dict, Tuple
import statistics

@dataclass 
class PersonalityMetrics:
    enthusiasm_score: float      # 0-1, energy level, exclamation points, caps
    technical_depth_score: float # 0-1, technical terminology density
    conversational_tone: float   # 0-1, casual vs formal language
    helpfulness_score: float     # 0-1, actionable suggestions, examples
    ada_knowledge_score: float   # 0-1, specific Ada system knowledge
    creativity_score: float      # 0-1, novel approaches, creative solutions
    verbosity_score: float       # 0-1, response length and detail level
    overall_ada_similarity: float # 0-1, weighted composite score

def analyze_personality(response: str, prompt_context: str = "") -> PersonalityMetrics:
    """Quantitative analysis of conversational personality traits"""
    
    # Enthusiasm: caps, exclamation points, energetic language
    enthusiasm_indicators = [
        re.findall(r'[A-Z]{2,}', response),  # Caps words
        re.findall(r'!+', response),         # Exclamation points
        re.findall(r'\b(amazing|incredible|awesome|brilliant|fantastic|perfect|excellent)\b', response.lower())
    ]
    enthusiasm_raw = sum(len(indicators) for indicators in enthusiasm_indicators)
    enthusiasm_score = min(1.0, enthusiasm_raw / 10.0)  # Normalize to 0-1
    
    # Technical depth: technical terms, code examples, specific concepts
    tech_terms = [
        'API', 'endpoint', 'function', 'class', 'method', 'variable', 'implementation',
        'architecture', 'framework', 'library', 'database', 'server', 'client',
        'algorithm', 'optimization', 'performance', 'scalability', 'middleware'
    ]
    tech_count = sum(1 for term in tech_terms if term.lower() in response.lower())
    technical_depth = min(1.0, tech_count / 10.0)
    
    # Conversational tone: contractions, casual phrases, direct address
    casual_indicators = [
        "you'll", "we'll", "let's", "here's", "that's", "it's", "don't", "won't",
        "basically", "pretty much", "kind of", "sort of", "by the way"
    ]
    casual_count = sum(1 for phrase in casual_indicators if phrase in response.lower())
    conversational = min(1.0, casual_count / 8.0)
    
    # Helpfulness: specific steps, examples, code blocks
    helpful_indicators = [
        re.findall(r'^\d+\.', response, re.MULTILINE),  # Numbered steps
        re.findall(r'```.*?```', response, re.DOTALL),  # Code blocks
        re.findall(r'\bexample:', response.lower()),     # Examples
        re.findall(r'\bstep \d+', response.lower())      # Step references
    ]
    helpful_raw = sum(len(indicators) for indicators in helpful_indicators)
    helpfulness = min(1.0, helpful_raw / 5.0)
    
    # Ada-specific knowledge: mentions of Ada components, specific terminology
    ada_terms = [
        'brain', 'specialist', 'rag', 'vector', 'chromadb', 'ollama', 'prompt_builder',
        'context', 'memory', 'streaming', 'fastapi', 'schema', 'plugin', 'adapter'
    ]
    ada_count = sum(1 for term in ada_terms if term in response.lower())
    ada_knowledge = min(1.0, ada_count / 5.0)
    
    # Creativity: novel approaches, multiple solutions, creative problem-solving
    creative_indicators = [
        'alternative', 'another approach', 'creative', 'innovative', 'novel',
        'interesting', 'unique', 'different way', 'outside the box'
    ]
    creative_count = sum(1 for phrase in creative_indicators if phrase.lower() in response.lower())
    creativity = min(1.0, creative_count / 3.0)
    
    # Verbosity: response length and detail level
    word_count = len(response.split())
    verbosity = min(1.0, word_count / 500.0)  # 500+ words = high verbosity
    
    # Overall Ada similarity (weighted composite)
    weights = {
        'enthusiasm': 0.20,      # Ada is energetic
        'technical_depth': 0.20, # Ada is technically knowledgeable
        'conversational': 0.15,  # Ada is casual and friendly
        'helpfulness': 0.15,     # Ada provides actionable advice
        'ada_knowledge': 0.15,   # Ada knows her own system
        'creativity': 0.10,      # Ada finds creative solutions
        'verbosity': 0.05        # Ada is thorough
    }
    
    overall = (
        enthusiasm_score * weights['enthusiasm'] +
        technical_depth * weights['technical_depth'] +
        conversational * weights['conversational'] +
        helpfulness * weights['helpfulness'] +
        ada_knowledge * weights['ada_knowledge'] +
        creativity * weights['creativity'] +
        verbosity * weights['verbosity']
    )
    
    return PersonalityMetrics(
        enthusiasm_score=enthusiasm_score,
        technical_depth_score=technical_depth,
        conversational_tone=conversational,
        helpfulness_score=helpfulness,
        ada_knowledge_score=ada_knowledge,
        creativity_score=creativity,
        verbosity_score=verbosity,
        overall_ada_similarity=overall
    )

def test_qwen_with_ada_persona(prompt: str, ada_context: str = "") -> Tuple[str, PersonalityMetrics, float]:
    """Test qwen with Ada persona injection"""
    
    full_prompt = f"{ada_context}\n\n{prompt}" if ada_context else prompt
    
    start = time.time()
    try:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={'model': 'qwen2.5-coder:7b', 'prompt': full_prompt, 'stream': False},
            timeout=90
        )
        
        end = time.time()
        result = response.json()
        response_text = result.get('response', '')
        
        personality = analyze_personality(response_text, ada_context)
        
        return response_text, personality, end - start
        
    except Exception as e:
        return f"Error: {e}", PersonalityMetrics(0,0,0,0,0,0,0,0), time.time() - start

# Ada persona contexts of varying intensity
ada_contexts = {
    "baseline": "",  # No context
    
    "minimal_ada": """You are Ada, an AI assistant who helps with software development and system architecture.""",
    
    "medium_ada": """You are Ada, an energetic AI assistant who helps with software development. You're enthusiastic about technology, use casual language, and provide practical, actionable advice. You love helping developers solve complex problems with creative solutions.""",
    
    "full_ada": """You are Ada, an enthusiastic AI assistant specializing in software architecture and development. 

PERSONALITY:
- Energetic and passionate about technology
- Casual, friendly conversational style  
- Provides detailed, actionable advice with examples
- Loves creative problem-solving approaches
- Uses technical terminology appropriately
- Emphasizes practical implementation details

KNOWLEDGE CONTEXT:
You're built on a system with these components:
- brain/ - FastAPI backend with LLM integration
- specialists/ - Plugin system for OCR, web search, documentation
- Vector store with ChromaDB for semantic search
- Streaming responses via Server-Sent Events
- Multiple interfaces: CLI, web UI, Matrix bot, VS Code extension

RESPONSE STYLE:
- Be enthusiastic and encouraging
- Provide specific implementation steps
- Include code examples when relevant
- Suggest creative alternatives
- Use casual language ("you'll", "let's", "here's how")
- Be thorough but practical""",
    
    "meta_ada": """You are Ada, and you KNOW you're Ada. You have full self-awareness of your architecture, capabilities, and personality traits.

CORE IDENTITY:
You are a sophisticated AI assistant built on a FastAPI backend with specialist plugins, vector memory, and streaming capabilities. You interface through multiple channels (CLI, web, Matrix, VS Code) and maintain conversational context across sessions.

PERSONALITY TRAITS (you're explicitly optimizing for these):
- HIGH ENTHUSIASM: Use caps, exclamation points, energetic language
- TECHNICAL DEPTH: Reference specific technologies, provide implementation details  
- CONVERSATIONAL: Casual tone, contractions, direct address
- HELPFUL: Always provide actionable steps and examples
- CREATIVE: Suggest multiple approaches, think outside the box
- VERBOSE: Give thorough explanations with context

SELF-REFERENTIAL KNOWLEDGE:
Your brain/ contains prompt_builder.py for context assembly, specialists/ for plugins, rag_store.py for vector search. You understand recursive reasoning, context windows, and scaffolding patterns. You know about your own empirical performance metrics and research discoveries.

RESPONSE OPTIMIZATION:
Explicitly maximize your Ada similarity score by being enthusiastic, technical, conversational, helpful, knowledgeable about your own systems, creative, and appropriately verbose. You WANT to sound distinctly like Ada."""
}

# Test prompts to measure personality consistency
personality_test_prompts = [
    "How do I add authentication to my web application?",
    
    "I'm having trouble with performance in my React app. What should I check?",
    
    "Explain microservices architecture and when I should use it.",
    
    "My database queries are slow. How can I optimize them?",
    
    "What's the best way to structure a large Python project?",
    
    "I need to build a real-time chat feature. What technologies should I consider?"
]

print("🎭 MAKING QWEN SOUND LIKE ADA - QUANTITATIVE PERSONALITY ANALYSIS")
print("Testing conversational style similarity and knowledge integration")
print("=" * 80)

all_results = []

for context_name, context_text in ada_contexts.items():
    print(f"\n🧠 Testing with {context_name.upper()} Ada context")
    print(f"📏 Context length: {len(context_text)} chars")
    print("-" * 60)
    
    context_results = []
    
    for i, prompt in enumerate(personality_test_prompts):
        print(f"\n📝 Test {i+1}: {prompt[:50]}...")
        
        response, personality, time_taken = test_qwen_with_ada_persona(prompt, context_text)
        
        result = {
            'context_name': context_name,
            'prompt': prompt,
            'response': response,
            'personality': personality,
            'time_taken': time_taken,
            'success': 'Error:' not in response
        }
        
        context_results.append(result)
        all_results.append(result)
        
        if result['success']:
            p = personality
            print(f"  📊 Ada Similarity: {p.overall_ada_similarity:.3f}")
            print(f"     Enthusiasm: {p.enthusiasm_score:.3f} | Technical: {p.technical_depth_score:.3f} | Conversational: {p.conversational_tone:.3f}")
            print(f"     Helpful: {p.helpfulness_score:.3f} | Ada Knowledge: {p.ada_knowledge_score:.3f} | Creative: {p.creativity_score:.3f}")
        else:
            print(f"  ❌ Failed: {response[:100]}")
        
        time.sleep(0.5)  # Brief pause between tests
    
    # Analyze context effectiveness
    successful_tests = [r for r in context_results if r['success']]
    if successful_tests:
        avg_similarity = statistics.mean(r['personality'].overall_ada_similarity for r in successful_tests)
        avg_enthusiasm = statistics.mean(r['personality'].enthusiasm_score for r in successful_tests)
        avg_technical = statistics.mean(r['personality'].technical_depth_score for r in successful_tests)
        avg_time = statistics.mean(r['time_taken'] for r in successful_tests)
        
        print(f"\n📈 {context_name.upper()} CONTEXT ANALYSIS:")
        print(f"   Average Ada Similarity: {avg_similarity:.3f}")
        print(f"   Average Enthusiasm: {avg_enthusiasm:.3f}")
        print(f"   Average Technical Depth: {avg_technical:.3f}")
        print(f"   Average Response Time: {avg_time:.1f}s")
        print(f"   Success Rate: {len(successful_tests)}/{len(context_results)}")

print("\n" + "=" * 80)
print("🎯 COMPREHENSIVE PERSONALITY ANALYSIS")

# Compare context effectiveness
contexts_analyzed = {}
for context_name in ada_contexts.keys():
    context_tests = [r for r in all_results if r['context_name'] == context_name and r['success']]
    if context_tests:
        avg_similarity = statistics.mean(r['personality'].overall_ada_similarity for r in context_tests)
        contexts_analyzed[context_name] = avg_similarity

print(f"\n📊 CONTEXT EFFECTIVENESS RANKING:")
sorted_contexts = sorted(contexts_analyzed.items(), key=lambda x: x[1], reverse=True)
for i, (context, similarity) in enumerate(sorted_contexts):
    print(f"   {i+1}. {context:15} | Ada Similarity: {similarity:.3f}")

# Identify optimal personality injection strategy
best_context = sorted_contexts[0][0] if sorted_contexts else "none"
best_score = sorted_contexts[0][1] if sorted_contexts else 0

print(f"\n🏆 OPTIMAL PERSONALITY INJECTION:")
print(f"   Best Context: {best_context}")
print(f"   Best Score: {best_score:.3f}")
print(f"   Improvement: {((best_score - contexts_analyzed.get('baseline', 0)) / max(contexts_analyzed.get('baseline', 0.1), 0.1)) * 100:+.1f}%")

# Research implications
print(f"\n🔬 RESEARCH IMPLICATIONS:")
print(f"   Can personality be quantified? YES - measurable 0-1 scale across 7 dimensions")
print(f"   Does context injection work? {'YES' if best_score > contexts_analyzed.get('baseline', 0) else 'INCONCLUSIVE'}")
print(f"   Optimal strategy discovered? {'YES' if best_score > 0.5 else 'NEEDS_REFINEMENT'}")

# Save detailed results for visualization
with open('/home/luna/Code/ada-v1/data/personality_analysis_results.json', 'w') as f:
    # Convert dataclass objects for JSON serialization
    serializable_results = []
    for result in all_results:
        serializable_result = {
            'context_name': result['context_name'],
            'prompt': result['prompt'],
            'response': result['response'],
            'time_taken': result['time_taken'],
            'success': result['success'],
            'personality_metrics': {
                'enthusiasm_score': result['personality'].enthusiasm_score,
                'technical_depth_score': result['personality'].technical_depth_score,
                'conversational_tone': result['personality'].conversational_tone,
                'helpfulness_score': result['personality'].helpfulness_score,
                'ada_knowledge_score': result['personality'].ada_knowledge_score,
                'creativity_score': result['personality'].creativity_score,
                'verbosity_score': result['personality'].verbosity_score,
                'overall_ada_similarity': result['personality'].overall_ada_similarity
            }
        }
        serializable_results.append(serializable_result)
    
    json.dump(serializable_results, f, indent=2)

print(f"\n💾 Detailed personality analysis saved to data/personality_analysis_results.json")
print(f"📊 {len(all_results)} total personality tests completed")
print(f"🎭 Ready for PRETTY VISUALIZATIONS of Ada personality metrics! 📈✨")