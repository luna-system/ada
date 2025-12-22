#!/usr/bin/env python3
"""
Cognitive Load Boundary Testing for qwen2.5-coder:7b
Direct Ollama API testing to map prompt complexity limits
"""

import json
import time
import requests
import sys
from datetime import datetime
from typing import Dict, List, Any

class CognitiveLoadTester:
    def __init__(self, model="qwen2.5-coder:7b", base_url="http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self.results = []
    
    def test_prompt(self, prompt: str, test_name: str, runs: int = 3) -> Dict[str, Any]:
        """Test a prompt multiple times and collect metrics"""
        print(f"\n🧪 Testing: {test_name}")
        print(f"📝 Prompt length: {len(prompt)} chars, {len(prompt.split())} words")
        
        run_results = []
        
        for run in range(runs):
            print(f"  Run {run + 1}/{runs}...", end=" ")
            
            start_time = time.time()
            
            # Make direct request to Ollama
            try:
                response = requests.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.7,
                            "max_tokens": 200  # Limit for testing
                        }
                    },
                    timeout=30
                )
                
                end_time = time.time()
                
                if response.status_code == 200:
                    result = response.json()
                    generated_text = result.get('response', '')
                    token_count = len(generated_text.split())
                    ttft = end_time - start_time
                    
                    run_result = {
                        "run": run + 1,
                        "success": True,
                        "tokens_generated": token_count,
                        "ttft": ttft,
                        "response_length": len(generated_text),
                        "response_preview": generated_text[:100] + "..." if len(generated_text) > 100 else generated_text,
                        "coherent": len(generated_text.strip()) > 0 and not generated_text.startswith("I don't")
                    }
                    
                    print(f"✅ {token_count} tokens, {ttft:.2f}s")
                    
                else:
                    run_result = {
                        "run": run + 1,
                        "success": False,
                        "error": f"HTTP {response.status_code}",
                        "tokens_generated": 0,
                        "ttft": end_time - start_time
                    }
                    print(f"❌ HTTP {response.status_code}")
                    
            except Exception as e:
                run_result = {
                    "run": run + 1,
                    "success": False,
                    "error": str(e),
                    "tokens_generated": 0,
                    "ttft": time.time() - start_time
                }
                print(f"❌ {e}")
            
            run_results.append(run_result)
            time.sleep(1)  # Brief pause between runs
        
        # Calculate aggregate metrics
        successful_runs = [r for r in run_results if r["success"]]
        
        if successful_runs:
            avg_tokens = sum(r["tokens_generated"] for r in successful_runs) / len(successful_runs)
            avg_ttft = sum(r["ttft"] for r in successful_runs) / len(successful_runs)
            coherence_rate = sum(1 for r in successful_runs if r.get("coherent", False)) / len(successful_runs)
        else:
            avg_tokens = 0
            avg_ttft = 0
            coherence_rate = 0
        
        test_result = {
            "test_name": test_name,
            "prompt_length_chars": len(prompt),
            "prompt_length_words": len(prompt.split()),
            "timestamp": datetime.now().isoformat(),
            "runs": run_results,
            "success_rate": len(successful_runs) / runs,
            "avg_tokens": avg_tokens,
            "avg_ttft": avg_ttft,
            "coherence_rate": coherence_rate,
            "overall_success": len(successful_runs) > 0 and avg_tokens > 5
        }
        
        self.results.append(test_result)
        
        # Print summary
        print(f"  📊 Success: {test_result['success_rate']:.1%}, "
              f"Tokens: {avg_tokens:.1f}, "
              f"TTFT: {avg_ttft:.2f}s, "
              f"Coherent: {coherence_rate:.1%}")
        
        return test_result
    
    def save_results(self, filename: str = None):
        """Save results to JSON file"""
        if filename is None:
            filename = f"cognitive_load_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump({
                "model": self.model,
                "test_timestamp": datetime.now().isoformat(),
                "total_tests": len(self.results),
                "results": self.results
            }, f, indent=2)
        
        print(f"\n💾 Results saved to: {filename}")
        return filename

# Test prompts of increasing complexity
PROMPTS = {
    "baseline_simple": "Hello! How can I help you today?",
    
    "basic_assistant": "You are a helpful AI assistant. Please respond to this user message naturally: Hello! How can I help you today?",
    
    "single_tool": """You are an AI assistant that can read files. When you need to read a file, use: TOOL_REQUEST[read_file:{"path":"filename"}]

User message: Hello! How can I help you today?""",
    
    "two_tools": """You are an AI assistant with file access. Available tools:
- Read file: TOOL_REQUEST[read_file:{"path":"filename"}]  
- Search code: TOOL_REQUEST[search:{"query":"pattern"}]

User message: Hello! How can I help you today?""",
    
    "ada_minimal": """You are Ada, an AI assistant with VS Code tools. Available:
- TOOL_REQUEST[ada_read_file:{"path":"file.ts"}]
- TOOL_REQUEST[ada_search:{"query":"pattern"}]

User message: Hello! How can I help you today?""",
    
    "ada_medium": """You have access to VS Code tools via the extension. Available tools:

- ada_read_file: Read file contents
  Example: TOOL_REQUEST[ada_read_file:{"path":"src/index.ts"}]

- ada_search: Search for text patterns  
  Example: TOOL_REQUEST[ada_search:{"query":"function handleMessage"}]

User request: Hello! How can I help you today?""",
    
    # This is the one that BREAKS qwen2.5-coder:7b
    "ada_full_original": """You have access to VS Code tools via the extension. When you need to read files, search code, or analyze the workspace, request tools using this syntax:

TOOL_REQUEST[tool_name:{"param":"value"}]

Available tools:

- ada_introspect: Analyze workspace structure, find TODOs/FIXMEs, understand project
  When to use: Understanding the codebase, finding tasks, getting project overview
  Example: TOOL_REQUEST[ada_introspect:{"query":"TODOs in the project"}]
  Returns: Project structure, package.json info, TODO/FIXME items with file locations

- ada_read_file: Read file contents with optional line range
  When to use: Reading specific files to understand code, reviewing implementations
  Example: TOOL_REQUEST[ada_read_file:{"path":"src/index.ts"}]
  Example: TOOL_REQUEST[ada_read_file:{"path":"src/app.py","startLine":10,"endLine":50}]
  Returns: File contents (or portion if line range specified)

- ada_search: Search for text patterns in the codebase
  When to use: Finding where something is defined, used, or referenced
  Example: TOOL_REQUEST[ada_search:{"query":"handleMessage","includePattern":"**/*.ts"}]
  Returns: Matching lines with file paths and line numbers

- ada_list_files: List files in a directory with optional glob pattern
  When to use: Exploring folder structure, finding files of a certain type
  Example: TOOL_REQUEST[ada_list_files:{"path":"src","pattern":"**/*.ts"}]
  Returns: List of matching files

---

User request: Hello! How can I help you today?"""
}

def main():
    print("🔬 Starting Cognitive Load Boundary Testing")
    print(f"🎯 Target: qwen2.5-coder:7b")
    print(f"📊 Testing {len(PROMPTS)} prompt variants")
    
    tester = CognitiveLoadTester()
    
    # Test in order of increasing complexity
    for prompt_name in [
        "baseline_simple",
        "basic_assistant", 
        "single_tool",
        "two_tools",
        "ada_minimal",
        "ada_medium",
        "ada_full_original"
    ]:
        prompt = PROMPTS[prompt_name]
        result = tester.test_prompt(prompt, prompt_name)
        
        # If this prompt fails completely, note the boundary
        if not result["overall_success"]:
            print(f"🚨 COGNITIVE BOUNDARY DETECTED at: {prompt_name}")
            print(f"   Previous prompt worked, this one failed!")
            break
    
    # Save results
    filename = tester.save_results()
    
    # Print summary
    print(f"\n📈 RESULTS SUMMARY:")
    for result in tester.results:
        status = "✅" if result["overall_success"] else "❌"
        print(f"  {status} {result['test_name']:20} | "
              f"Words: {result['prompt_length_words']:3d} | "
              f"Success: {result['success_rate']:.1%} | "
              f"Tokens: {result['avg_tokens']:4.1f}")

if __name__ == "__main__":
    main()