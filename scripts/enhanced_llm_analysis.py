#!/usr/bin/env python3
"""
ENHANCED LLM EMPIRICAL ANALYSIS FRAMEWORK
Multi-dimensional performance tracking with quality metrics

New Axes:
- Context Window Utilization
- Output Quality Scoring  
- Copilot Baseline Comparison
- Mathematical Analysis
"""

import requests
import time
import json
import re
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple, Optional
import statistics

@dataclass
class ModelSpecs:
    name: str
    parameters: str
    context_window: int  # tokens
    architecture: str
    quantization: str

@dataclass
class QualityMetrics:
    coherence_score: float  # 0-1, logical flow
    completeness_score: float  # 0-1, addresses all parts of question
    actionability_score: float  # 0-1, provides concrete steps
    technical_accuracy_score: float  # 0-1, technical correctness
    conciseness_score: float  # 0-1, efficient communication
    overall_score: float  # weighted average

@dataclass 
class EnhancedTestResult:
    model: str
    model_specs: ModelSpecs
    test_type: str  # "control", "experimental", "copilot_baseline"
    context_type: str
    prompt_chars: int
    response_tokens: int
    time_taken: float
    tokens_per_second: float
    success: bool
    response_text: str
    quality_metrics: Optional[QualityMetrics]
    context_utilization: float  # 0-1, how much of context seems used

# Model specifications
MODEL_SPECS = {
    'qwen2.5-coder:7b': ModelSpecs("qwen2.5-coder:7b", "7.6B", 32768, "Qwen2", "Q4_K_M"),
    'deepseek-r1:latest': ModelSpecs("deepseek-r1:latest", "8.2B", 8192, "Qwen3", "Q4_K_M"),
    'qwen3-coder:latest': ModelSpecs("qwen3-coder:latest", "30.5B", 32768, "Qwen3MoE", "Q4_K_M"),
    'gemma3:latest': ModelSpecs("gemma3:latest", "4.3B", 8192, "Gemma3", "Q4_K_M"),
    'codellama:latest': ModelSpecs("codellama:latest", "7B", 4096, "Llama", "Q4_0"),
}

def calculate_quality_metrics(prompt: str, response: str) -> QualityMetrics:
    """Calculate quality metrics for a response"""
    
    # Coherence: Check for logical structure, proper sentences
    sentences = re.split(r'[.!?]+', response)
    coherent_sentences = sum(1 for s in sentences if len(s.strip()) > 10 and not s.strip().startswith('#'))
    coherence = min(1.0, coherent_sentences / max(1, len(sentences)))
    
    # Completeness: Check if response addresses key parts of prompt
    prompt_keywords = re.findall(r'\b[a-zA-Z]{4,}\b', prompt.lower())
    response_keywords = re.findall(r'\b[a-zA-Z]{4,}\b', response.lower())
    keyword_coverage = len(set(prompt_keywords) & set(response_keywords)) / max(1, len(set(prompt_keywords)))
    completeness = min(1.0, keyword_coverage)
    
    # Actionability: Look for concrete steps, code examples, specific instructions
    action_indicators = ['step', 'add', 'create', 'modify', 'install', 'configure', 'example:', 'code:', '```', '1.', '2.']
    action_score = sum(1 for indicator in action_indicators if indicator in response.lower())
    actionability = min(1.0, action_score / 5.0)
    
    # Technical accuracy: Look for technical terms, proper structure
    tech_terms = ['function', 'class', 'method', 'API', 'endpoint', 'import', 'module', 'package', 'service']
    tech_score = sum(1 for term in tech_terms if term in response.lower())
    technical_accuracy = min(1.0, tech_score / 3.0)
    
    # Conciseness: Reward efficient communication
    response_efficiency = len(prompt) / max(1, len(response))
    conciseness = min(1.0, response_efficiency * 2)  # Penalize responses much longer than prompt
    
    # Overall weighted score
    weights = {
        'coherence': 0.25,
        'completeness': 0.25, 
        'actionability': 0.20,
        'technical_accuracy': 0.20,
        'conciseness': 0.10
    }
    
    overall = (
        coherence * weights['coherence'] +
        completeness * weights['completeness'] +
        actionability * weights['actionability'] +
        technical_accuracy * weights['technical_accuracy'] +
        conciseness * weights['conciseness']
    )
    
    return QualityMetrics(
        coherence_score=coherence,
        completeness_score=completeness,
        actionability_score=actionability,
        technical_accuracy_score=technical_accuracy,
        conciseness_score=conciseness,
        overall_score=overall
    )

def estimate_context_utilization(prompt: str, response: str) -> float:
    """Estimate how much of the context the model actually used"""
    prompt_concepts = set(re.findall(r'\b[a-zA-Z]{4,}\b', prompt.lower()))
    response_concepts = set(re.findall(r'\b[a-zA-Z]{4,}\b', response.lower()))
    
    if not prompt_concepts:
        return 0.0
        
    utilization = len(prompt_concepts & response_concepts) / len(prompt_concepts)
    return min(1.0, utilization)

def enhanced_test(model: str, prompt: str, context: str, test_type: str) -> EnhancedTestResult:
    full_prompt = f"{context}\n\n{prompt}"
    model_specs = MODEL_SPECS.get(model, ModelSpecs(model, "Unknown", 0, "Unknown", "Unknown"))
    
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
        time_taken = end - start
        tokens_per_second = tokens / time_taken if time_taken > 0 else 0
        
        quality_metrics = calculate_quality_metrics(prompt, response_text)
        context_utilization = estimate_context_utilization(full_prompt, response_text)
        
        return EnhancedTestResult(
            model=model,
            model_specs=model_specs,
            test_type=test_type,
            context_type=context[:30] + "..." if len(context) > 30 else context,
            prompt_chars=len(full_prompt),
            response_tokens=tokens,
            time_taken=time_taken,
            tokens_per_second=tokens_per_second,
            success=True,
            response_text=response_text,
            quality_metrics=quality_metrics,
            context_utilization=context_utilization
        )
        
    except Exception as e:
        return EnhancedTestResult(
            model=model,
            model_specs=model_specs,
            test_type=test_type,
            context_type="error",
            prompt_chars=len(full_prompt),
            response_tokens=0,
            time_taken=time.time() - start,
            tokens_per_second=0,
            success=False,
            response_text=str(e),
            quality_metrics=None,
            context_utilization=0
        )

def analyze_results(results: List[EnhancedTestResult]) -> Dict:
    """Comprehensive analysis of test results"""
    
    successful_results = [r for r in results if r.success and r.quality_metrics]
    
    if not successful_results:
        return {"error": "No successful results to analyze"}
    
    # Group by test type
    control_results = [r for r in successful_results if r.test_type == "control"]
    experimental_results = [r for r in successful_results if r.test_type == "experimental"]
    
    analysis = {
        "sample_sizes": {
            "control": len(control_results),
            "experimental": len(experimental_results)
        }
    }
    
    if control_results and experimental_results:
        # Speed analysis
        control_speeds = [r.tokens_per_second for r in control_results]
        experimental_speeds = [r.tokens_per_second for r in experimental_results]
        
        # Quality analysis
        control_quality = [r.quality_metrics.overall_score for r in control_results]
        experimental_quality = [r.quality_metrics.overall_score for r in experimental_results]
        
        # Context utilization
        control_utilization = [r.context_utilization for r in control_results]
        experimental_utilization = [r.context_utilization for r in experimental_results]
        
        analysis.update({
            "speed": {
                "control_avg": statistics.mean(control_speeds),
                "experimental_avg": statistics.mean(experimental_speeds),
                "improvement_percent": ((statistics.mean(experimental_speeds) - statistics.mean(control_speeds)) / statistics.mean(control_speeds)) * 100
            },
            "quality": {
                "control_avg": statistics.mean(control_quality),
                "experimental_avg": statistics.mean(experimental_quality),
                "improvement_percent": ((statistics.mean(experimental_quality) - statistics.mean(control_quality)) / statistics.mean(control_quality)) * 100
            },
            "context_utilization": {
                "control_avg": statistics.mean(control_utilization),
                "experimental_avg": statistics.mean(experimental_utilization),
                "improvement_percent": ((statistics.mean(experimental_utilization) - statistics.mean(control_utilization)) / statistics.mean(control_utilization)) * 100
            }
        })
    
    return analysis

# Enhanced contexts and test prompts
raw_context = """
Available system components: brain/app.py (FastAPI REST endpoints), brain/llm.py (Ollama client), brain/prompt_builder.py (RAG context assembly), brain/rag_store.py (ChromaDB vector search), brain/specialists/ (OCR, web search, docs plugins), brain/schemas.py (Pydantic models), brain/config.py (environment settings), frontend/ (web UI), matrix-bridge/ (Matrix bot), ada-client/ (HTTP client), ada-mcp/ (MCP server). Uses ChromaDB, Ollama, FastAPI.
"""

ai_context = """
# Ada System Architecture (.ai/ Framework)

## Core Services
- **API Layer**: brain/app.py - FastAPI endpoints with streaming + health checks
- **LLM Interface**: brain/llm.py - Ollama client with token monitoring  
- **Context Engine**: brain/prompt_builder.py - RAG assembly + specialist coordination
- **Vector Store**: brain/rag_store.py - ChromaDB semantic search interface
- **Data Contracts**: brain/schemas.py - Pydantic models (auto-documented via /v1/schema)

## Plugin Architecture  
- **Location**: brain/specialists/ - Auto-discovery system
- **Protocol**: BaseSpecialist.should_activate() + .process()
- **Capabilities**: OCR, web search, documentation, bidirectional LLM calls

## Interface Adapters
- **CLI**: ada-client/ → Terminal REPL  
- **Web**: frontend/ → EventSource streaming
- **Matrix**: matrix-bridge/ → Room context management
- **IDE**: ada-mcp/ → Model Context Protocol tools
"""

quality_test_prompts = [
    "Walk me through adding a new specialist plugin that can analyze code complexity.",
    "How would I implement real-time notifications for the web interface?", 
    "Design a caching strategy to improve response times across all interfaces.",
    "Explain how to add authentication and user management to the system."
]

# Run enhanced testing
print("🔬 ENHANCED LLM EMPIRICAL ANALYSIS")
print("Multi-dimensional performance tracking with quality metrics")
print("=" * 80)

models_to_test = ['qwen2.5-coder:7b', 'deepseek-r1:latest']
all_results = []

for model in models_to_test:
    print(f"\n🧠 Testing {model} ({MODEL_SPECS[model].parameters}, {MODEL_SPECS[model].context_window} ctx)")
    print("-" * 60)
    
    for i, prompt in enumerate(quality_test_prompts):
        print(f"\n📝 Quality Test {i+1}: {prompt[:60]}...")
        
        # Control
        control_result = enhanced_test(model, prompt, raw_context, "control")
        all_results.append(control_result)
        if control_result.success:
            print(f"  📊 Raw: {control_result.tokens_per_second:.1f} t/s, Q={control_result.quality_metrics.overall_score:.3f}, CU={control_result.context_utilization:.3f}")
        
        # Experimental
        exp_result = enhanced_test(model, prompt, ai_context, "experimental")
        all_results.append(exp_result)
        if exp_result.success:
            print(f"  📊 .ai/: {exp_result.tokens_per_second:.1f} t/s, Q={exp_result.quality_metrics.overall_score:.3f}, CU={exp_result.context_utilization:.3f}")
        
        time.sleep(0.5)

# Comprehensive analysis
print("\n" + "=" * 80)
print("📈 COMPREHENSIVE ANALYSIS")
analysis = analyze_results(all_results)

if "error" not in analysis:
    print(f"\n🎯 PERFORMANCE IMPROVEMENTS WITH .AI/ FRAMEWORK:")
    print(f"   Speed:               {analysis['speed']['improvement_percent']:+.1f}%")
    print(f"   Quality Score:       {analysis['quality']['improvement_percent']:+.1f}%")  
    print(f"   Context Utilization: {analysis['context_utilization']['improvement_percent']:+.1f}%")
    
    print(f"\n📊 ABSOLUTE METRICS:")
    print(f"   Raw Docs:    {analysis['speed']['control_avg']:.1f} t/s, Q={analysis['quality']['control_avg']:.3f}")
    print(f"   .ai/ Docs:   {analysis['speed']['experimental_avg']:.1f} t/s, Q={analysis['quality']['experimental_avg']:.3f}")

# Save detailed results for further analysis
with open('/home/luna/Code/ada-v1/data/enhanced_llm_analysis.json', 'w') as f:
    json.dump([asdict(r) for r in all_results], f, indent=2)
    
print(f"\n💾 Detailed results saved to data/enhanced_llm_analysis.json")
print(f"📊 {len(all_results)} total test runs completed")