#!/usr/bin/env python3
"""
CONTEXT WINDOW STRESS TEST
Testing the context window hypothesis and reasoning compression strategies

Hypothesis: Context window size directly impacts performance patterns
Test: Progressive context compression and reasoning scaffolding
"""

import requests
import time
import json
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class ContextTest:
    name: str
    context_chars: int
    estimated_tokens: int  # rough estimate: chars/4
    compression_strategy: str
    content: str

def create_progressive_contexts() -> List[ContextTest]:
    """Create contexts of increasing complexity to test window limits"""
    
    # Base context - minimal
    base = """
# Ada System Context
Core: brain/app.py (API), brain/llm.py (Ollama), brain/prompt_builder.py (context), brain/specialists/ (plugins)
"""
    
    # Medium context - structured
    medium = """
# Ada System Architecture
## Core Services
- brain/app.py: FastAPI endpoints, streaming chat
- brain/llm.py: Ollama client, token monitoring
- brain/prompt_builder.py: RAG assembly, specialist coordination
- brain/rag_store.py: ChromaDB vector search
- brain/specialists/: Plugin system (OCR, web search, docs)

## Data Flow
Request → app.py → prompt_builder → rag_store + specialists → llm.py → response
"""
    
    # Large context - comprehensive
    large = medium + """

## Detailed Components
### API Layer (brain/app.py)
- POST /v1/chat/stream: Main chat endpoint with Server-Sent Events
- GET /v1/specialists: List available specialist plugins
- GET /v1/schema: Pydantic model schemas
- GET /v1/info: System configuration and capabilities

### LLM Interface (brain/llm.py)  
- generate_stream(): Streaming text generation via Ollama
- count_tokens(): Token usage monitoring
- extract_thinking(): Parse reasoning from responses

### Context Engine (brain/prompt_builder.py)
- build_prompt(): Assemble RAG context + specialists + memories
- Specialist activation based on context and request type
- Memory injection from vector store semantic search

### Plugin Architecture (brain/specialists/)
- BaseSpecialist protocol: should_activate() + process()
- OCRSpecialist: Image text extraction via Tesseract
- WebSearchSpecialist: External web queries for fresh information
- DocsSpecialist: Search Ada's own documentation
- Bidirectional specialist calls: LLM can request specialist activation mid-response
"""
    
    # MASSIVE context - full documentation dump
    massive = large + """

### Database Layer (brain/rag_store.py)
- ChromaDB integration for vector storage
- Memory collections: personas, FAQs, memories, conversation_turns
- Semantic search with embedding-based retrieval
- Health checking and connection management

### Configuration Management (brain/config.py)
- Pydantic Settings for environment-based configuration
- LLM_BASE_URL: Ollama endpoint (default: localhost:11434)
- LLM_MODEL: Model name (default: qwen2.5-coder:7b)
- CHROMA_HOST/PORT: Vector database connection
- DATA_DIR: Persistent storage location

### Interface Adapters
- ada-client/: Shared HTTP client library for brain API
- frontend/: Web UI with EventSource streaming client
- matrix-bridge/: Matrix bot with per-room context management
- ada-mcp/: Model Context Protocol server for IDE integration

### Advanced Features
- Memory decay with temperature modulation
- Context habituation for repeated pattern detection  
- Prediction error weighting for novelty/surprise
- Attention spotlight for recency + relevance prioritization
- Multi-timescale caching: personas (24hr), memories (5min)
- Biomimetic memory system with neuromorphic processing
- Specialist bidirectional communication via XML tags
""" * 3  # Triple it to make it HUGE

    return [
        ContextTest("MINIMAL", len(base), len(base)//4, "Essential only", base),
        ContextTest("STRUCTURED", len(medium), len(medium)//4, "Hierarchical", medium), 
        ContextTest("COMPREHENSIVE", len(large), len(large)//4, "Full detail", large),
        ContextTest("MASSIVE", len(massive), len(massive)//4, "Documentation dump", massive)
    ]

def test_context_window_limits(model: str, contexts: List[ContextTest]) -> Dict:
    """Test model performance across different context sizes"""
    
    test_prompt = "Walk me through adding a new specialist plugin that can analyze code complexity and suggest optimizations."
    
    results = {
        "model": model,
        "context_window_claimed": {
            "qwen2.5-coder:7b": 32768,
            "deepseek-r1:latest": 8192
        }.get(model, "unknown"),
        "tests": []
    }
    
    for context in contexts:
        print(f"\n🧪 Testing {model} with {context.name} context")
        print(f"   📏 {context.context_chars:,} chars (~{context.estimated_tokens:,} tokens)")
        
        full_prompt = f"{context.content}\n\nUser request: {test_prompt}"
        
        start = time.time()
        try:
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={'model': model, 'prompt': full_prompt, 'stream': False},
                timeout=180
            )
            
            end = time.time()
            result = response.json()
            response_text = result.get('response', '')
            tokens = len(response_text.split())
            time_taken = end - start
            
            test_result = {
                "context_name": context.name,
                "context_chars": context.context_chars,
                "estimated_tokens": context.estimated_tokens,
                "success": True,
                "response_tokens": tokens,
                "time_taken": time_taken,
                "tokens_per_second": tokens / time_taken if time_taken > 0 else 0,
                "response_preview": response_text[:100] + "..." if response_text else "",
                "context_window_exceeded": context.estimated_tokens > results["context_window_claimed"]
            }
            
            print(f"   ✅ {tokens:,} tokens in {time_taken:.1f}s ({tokens/time_taken:.1f} t/s)")
            if test_result["context_window_exceeded"]:
                print(f"   ⚠️  Context exceeds claimed window by {context.estimated_tokens - results['context_window_claimed']:,} tokens")
            
        except Exception as e:
            test_result = {
                "context_name": context.name,
                "context_chars": context.context_chars,
                "estimated_tokens": context.estimated_tokens,
                "success": False,
                "error": str(e)[:200],
                "time_taken": time.time() - start,
                "context_window_exceeded": context.estimated_tokens > results["context_window_claimed"]
            }
            print(f"   ❌ FAILED: {str(e)[:50]}...")
        
        results["tests"].append(test_result)
        
        # Stop if we hit failures
        if not test_result["success"]:
            print(f"   🚨 Stopping tests for {model} at context limit")
            break
            
        time.sleep(0.5)
    
    return results

def test_reasoning_scaffolding():
    """Test progressive reasoning scaffolding approach"""
    print("\n" + "="*60)
    print("🧠 REASONING SCAFFOLDING TEST")
    print("="*60)
    
    # Simple scaffolded approach
    simple_request = "How do I add a new specialist plugin?"
    
    # Complex scaffolded approach - break it down
    scaffolded_prompt = """
Step 1: Understand the specialist system
Step 2: Create the plugin file  
Step 3: Implement the protocol
Step 4: Register the plugin
Step 5: Test the integration

Now, for each step, explain how to add a new specialist plugin that can analyze code complexity.
"""
    
    models = ['qwen2.5-coder:7b', 'deepseek-r1:latest']
    
    for model in models:
        print(f"\n🧠 Testing scaffolding with {model}")
        
        # Test simple vs scaffolded
        for prompt, name in [(simple_request, "SIMPLE"), (scaffolded_prompt, "SCAFFOLDED")]:
            start = time.time()
            try:
                response = requests.post(
                    'http://localhost:11434/api/generate',
                    json={'model': model, 'prompt': prompt, 'stream': False},
                    timeout=60
                )
                result = response.json()
                response_text = result.get('response', '')
                tokens = len(response_text.split())
                time_taken = time.time() - start
                
                print(f"   📊 {name}: {tokens:,} tokens in {time_taken:.1f}s")
                
            except Exception as e:
                print(f"   ❌ {name}: Failed - {str(e)[:50]}")

print("🔬 CONTEXT WINDOW STRESS TEST")
print("Testing context window hypothesis and reasoning scaffolding")

contexts = create_progressive_contexts()

models = ['qwen2.5-coder:7b', 'deepseek-r1:latest']
all_results = []

for model in models:
    print(f"\n{'='*60}")
    print(f"🧠 TESTING {model}")
    print(f"{'='*60}")
    
    result = test_context_window_limits(model, contexts)
    all_results.append(result)

# Test reasoning scaffolding
test_reasoning_scaffolding()

# Analysis
print(f"\n{'='*60}")
print("📊 CONTEXT WINDOW ANALYSIS")
print(f"{'='*60}")

for result in all_results:
    successful_tests = [t for t in result["tests"] if t["success"]]
    if successful_tests:
        max_context = max(t["context_chars"] for t in successful_tests)
        max_tokens = max(t["estimated_tokens"] for t in successful_tests)
        
        print(f"\n{result['model']}:")
        print(f"   Claimed context window: {result['context_window_claimed']:,} tokens")
        print(f"   Actual max handled:     {max_tokens:,} tokens ({max_context:,} chars)")
        print(f"   Exceeded claimed by:    {max_tokens - result['context_window_claimed']:,} tokens")
        
        # Performance degradation analysis
        speeds = [t["tokens_per_second"] for t in successful_tests if "tokens_per_second" in t]
        if len(speeds) > 1:
            print(f"   Speed range: {min(speeds):.1f} - {max(speeds):.1f} t/s")
            print(f"   Speed degradation: {((max(speeds) - min(speeds)) / max(speeds) * 100):.1f}%")

# Save results
with open('/home/luna/Code/ada-v1/data/context_window_analysis.json', 'w') as f:
    json.dump(all_results, f, indent=2)

print(f"\n💾 Results saved to data/context_window_analysis.json")

# GitHub Copilot Support Contact
print(f"\n📞 GITHUB COPILOT SUPPORT:")
print("   Individual: GitHub Support (support.github.com)")
print("   Business: GitHub Enterprise support")
print("   Community: GitHub Community Forum") 
print("   Docs: docs.github.com/copilot")
print("   No direct API rate/quality metrics published")