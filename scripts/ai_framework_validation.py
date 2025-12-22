#!/usr/bin/env python3
"""
.AI/ FRAMEWORK EMPIRICAL VALIDATION
Testing whether structured documentation improves LLM performance

Experimental Design:
- Control: Raw documentation/context
- Experimental: .ai/ structured documentation  
- Metrics: Speed, accuracy, context utilization
"""

import requests
import time
import json
from dataclasses import dataclass
from typing import List, Dict, Tuple

@dataclass
class TestResult:
    model: str
    test_type: str  # "control" or "experimental" 
    context_type: str
    prompt_chars: int
    response_tokens: int
    time_taken: float
    success: bool
    response_preview: str

def test_model_with_context(model: str, prompt: str, context: str, test_type: str) -> TestResult:
    full_prompt = f"{context}\n\n{prompt}"
    
    start = time.time()
    try:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={'model': model, 'prompt': full_prompt, 'stream': False},
            timeout=120
        )
        
        end = time.time()
        result = response.json()
        response_text = result.get('response', '')
        tokens = len(response_text.split())
        
        return TestResult(
            model=model,
            test_type=test_type,
            context_type=context[:20] + "..." if len(context) > 20 else context,
            prompt_chars=len(full_prompt),
            response_tokens=tokens,
            time_taken=end-start,
            success=True,
            response_preview=response_text[:100] + "..." if response_text else ""
        )
        
    except Exception as e:
        return TestResult(
            model=model,
            test_type=test_type,
            context_type="error",
            prompt_chars=len(full_prompt),
            response_tokens=0,
            time_taken=time.time() - start,
            success=False,
            response_preview=str(e)[:100]
        )

# CONTROL GROUP: Raw context dump
raw_context = """
You have access to the following components and capabilities:

brain/app.py - FastAPI application with REST endpoints for chat streaming, specialist listing, health checks
brain/llm.py - LLM client wrapper for Ollama with streaming generation and token counting  
brain/prompt_builder.py - Assembles prompts with RAG context, specialists, memories, conversation history
brain/rag_store.py - Vector database interface for semantic search over memories using ChromaDB
brain/specialists/ - Plugin system for OCR, web search, documentation lookup, bidirectional LLM calls
brain/schemas.py - Pydantic models for API contracts and data validation
brain/config.py - Environment configuration using Pydantic Settings
frontend/ - Web UI with EventSource streaming client for chat interface
matrix-bridge/ - Matrix bot integration with room context management
ada-client/ - Shared HTTP client library for Ada brain API
ada-mcp/ - Model Context Protocol server for IDE integration

The system uses ChromaDB for vector storage, Ollama for LLM inference, and supports multiple interfaces including CLI, web UI, Matrix bot, and MCP tools.
"""

# EXPERIMENTAL GROUP: .ai/ structured context
ai_context = """
# Ada System Context (.ai/ Documentation)

## Core Architecture
**Entry Point**: brain/app.py - FastAPI application coordinating all subsystems
**LLM Interface**: brain/llm.py - Ollama client with streaming + token monitoring
**Context Assembly**: brain/prompt_builder.py - RAG context + specialists + memories
**Vector Store**: brain/rag_store.py - ChromaDB semantic search interface
**Data Models**: brain/schemas.py - Pydantic contracts (auto-exposed via /v1/schema)
**Configuration**: brain/config.py - Environment-based settings

## Plugin System  
**Location**: brain/specialists/
**Protocol**: BaseSpecialist interface with should_activate() + process() methods
**Capabilities**: OCR, web search, documentation lookup, bidirectional LLM calls
**Auto-discovery**: Runtime registration via __init__.py

## Interfaces (Adapter Pattern)
- **CLI**: ada-client/ - Terminal REPL and one-shot queries
- **Web**: frontend/ - EventSource streaming browser client  
- **Matrix**: matrix-bridge/ - Bot with per-room context management
- **MCP**: ada-mcp/ - Model Context Protocol for IDE integration

## Data Flow
Request → brain/app.py → prompt_builder → rag_store + specialists → llm.py → streaming response
Memory: response → rag_store.py → ChromaDB vector storage

## Key Dependencies
- Vector DB: ChromaDB for semantic search
- LLM: Ollama for inference
- API: FastAPI for REST endpoints
"""

# Test prompts  
test_prompts = [
    "How do I add a new specialist plugin to the system?",
    "Explain the data flow when a user sends a chat message through the web interface.",
    "What would I need to modify to add rate limiting to the API?",
    "How does the system handle memory storage and retrieval?"
]

models = ['qwen2.5-coder:7b', 'deepseek-r1:latest']

print("🧪 .AI/ FRAMEWORK EMPIRICAL VALIDATION")
print("Testing structured vs unstructured documentation impact on LLM performance")
print("=" * 80)

results = []

for model in models:
    print(f"\n🧠 Testing {model}")
    print("-" * 50)
    
    for i, prompt in enumerate(test_prompts):
        print(f"\n📝 Test {i+1}: {prompt[:50]}...")
        
        # Control group: Raw context
        print("  🔄 Control (raw docs)...")
        control_result = test_model_with_context(model, prompt, raw_context, "control")
        results.append(control_result)
        
        # Experimental group: .ai/ structured
        print("  🔄 Experimental (.ai/ docs)...")  
        experimental_result = test_model_with_context(model, prompt, ai_context, "experimental")
        results.append(experimental_result)
        
        # Quick comparison
        if control_result.success and experimental_result.success:
            speed_diff = experimental_result.time_taken - control_result.time_taken
            token_diff = experimental_result.response_tokens - control_result.response_tokens
            print(f"  📊 .ai/ vs raw: {speed_diff:+.1f}s time, {token_diff:+d} tokens")
        
        # Brief pause between tests
        time.sleep(1)

print("\n" + "=" * 80)
print("📊 RESULTS ANALYSIS")

# Aggregate results
control_results = [r for r in results if r.test_type == "control" and r.success]
experimental_results = [r for r in results if r.test_type == "experimental" and r.success]

if control_results and experimental_results:
    avg_control_time = sum(r.time_taken for r in control_results) / len(control_results)
    avg_experimental_time = sum(r.time_taken for r in experimental_results) / len(experimental_results)
    
    avg_control_tokens = sum(r.response_tokens for r in control_results) / len(control_results)
    avg_experimental_tokens = sum(r.response_tokens for r in experimental_results) / len(experimental_results)
    
    time_improvement = ((avg_control_time - avg_experimental_time) / avg_control_time) * 100
    token_improvement = ((avg_experimental_tokens - avg_control_tokens) / avg_control_tokens) * 100
    
    print(f"\n🎯 AGGREGATE FINDINGS:")
    print(f"   Speed:   .ai/ is {time_improvement:+.1f}% vs raw documentation")
    print(f"   Output:  .ai/ produces {token_improvement:+.1f}% more tokens")
    print(f"   Sample:  {len(control_results)} control, {len(experimental_results)} experimental tests")

# Detailed breakdown
print(f"\n📋 DETAILED RESULTS:")
print(f"{'Model':<20} | {'Type':<12} | {'Time':<6} | {'Tokens':<7} | {'Preview'}")
print("-" * 80)

for result in results:
    if result.success:
        print(f"{result.model:<20} | {result.test_type:<12} | {result.time_taken:6.1f}s | {result.response_tokens:7d} | {result.response_preview[:30]}...")
    else:
        print(f"{result.model:<20} | {result.test_type:<12} | FAILED | {result.response_preview[:50]}")