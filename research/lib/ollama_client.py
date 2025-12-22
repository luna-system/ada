"""
Sterile Ollama Client for Experiments

This client treats the model as a black box under measurement.
No opinions, no retries, no error handling that changes behavior.
Just record exactly what happens.
"""

import time
import requests
from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class ModelResponse:
    """Complete record of a single model call"""
    success: bool
    response_text: str
    latency_seconds: float
    tokens_generated: int
    error: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None
    
    # Timing breakdown if available
    time_to_first_token: Optional[float] = None
    total_duration_ns: Optional[int] = None
    load_duration_ns: Optional[int] = None
    eval_count: Optional[int] = None
    eval_duration_ns: Optional[int] = None


class OllamaClient:
    """
    Minimal Ollama client for experiments.
    
    Design principles:
    - No retry logic (we want to measure failures)
    - No response modification (raw data only)
    - Complete timing information
    - Explicit error recording
    """
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
    
    def generate(
        self, 
        model: str, 
        prompt: str, 
        options: Optional[Dict[str, Any]] = None,
        timeout: float = 60.0
    ) -> ModelResponse:
        """
        Single model generation call with complete recording.
        
        Args:
            model: Model name (e.g., "qwen2.5-coder:7b")
            prompt: The exact prompt to send
            options: Ollama options (temperature, max_tokens, etc.)
            timeout: Request timeout in seconds
            
        Returns:
            ModelResponse with complete call information
        """
        start_time = time.time()
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
        }
        
        if options:
            payload["options"] = options
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=timeout
            )
            
            end_time = time.time()
            latency = end_time - start_time
            
            if response.status_code == 200:
                data = response.json()
                response_text = data.get('response', '')
                
                return ModelResponse(
                    success=True,
                    response_text=response_text,
                    latency_seconds=latency,
                    tokens_generated=len(response_text.split()),  # Rough estimate
                    raw_response=data,
                    total_duration_ns=data.get('total_duration'),
                    load_duration_ns=data.get('load_duration'),
                    eval_count=data.get('eval_count'),
                    eval_duration_ns=data.get('eval_duration'),
                )
            else:
                return ModelResponse(
                    success=False,
                    response_text='',
                    latency_seconds=latency,
                    tokens_generated=0,
                    error=f"HTTP {response.status_code}: {response.text[:200]}"
                )
                
        except requests.Timeout:
            return ModelResponse(
                success=False,
                response_text='',
                latency_seconds=time.time() - start_time,
                tokens_generated=0,
                error=f"Timeout after {timeout}s"
            )
        except requests.ConnectionError as e:
            return ModelResponse(
                success=False,
                response_text='',
                latency_seconds=time.time() - start_time,
                tokens_generated=0,
                error=f"Connection error: {e}"
            )
        except Exception as e:
            return ModelResponse(
                success=False,
                response_text='',
                latency_seconds=time.time() - start_time,
                tokens_generated=0,
                error=f"Unexpected error: {type(e).__name__}: {e}"
            )
    
    def health_check(self) -> bool:
        """Check if Ollama is reachable"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def list_models(self) -> list[str]:
        """List available models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return [m['name'] for m in data.get('models', [])]
        except:
            pass
        return []
