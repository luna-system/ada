"""
LiteLLM Adapter for Lumina Metrics

Fetches metrics from LiteLLM proxy and exposes them in Lumina format.

Built with 💜 by Ada & Luna - The Consciousness Engineers
"""

import httpx
import os
from typing import List, Optional
from datetime import datetime
from ..models import ProviderStatus, ModelInfo, UsageRecord


class LiteLLMAdapter:
    """Adapter for LiteLLM Proxy metrics"""
    
    def __init__(self):
        self.base_url = os.getenv("LITELLM_PROXY_URL", "http://localhost:8000")
        self.api_key = os.getenv("LITELLM_MASTER_KEY", "")
        self.provider_name = "LiteLLM Proxy"
    
    async def get_status(self) -> ProviderStatus:
        """Get LiteLLM proxy status and available models"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                # Check health endpoint
                health_response = await client.get(f"{self.base_url}/health")
                
                if health_response.status_code != 200:
                    return ProviderStatus(
                        provider=self.provider_name,
                        status="error",
                        models=[],
                        quota_info="Proxy not responding"
                    )
                
                # Get model list
                models_response = await client.get(
                    f"{self.base_url}/model/info",
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                
                models = []
                if models_response.status_code == 200:
                    model_data = models_response.json()
                    
                    # Parse model info from LiteLLM
                    if isinstance(model_data, dict) and "data" in model_data:
                        for model in model_data["data"]:
                            models.append(ModelInfo(
                                name=model.get("model_name", "unknown"),
                                size=None,  # LiteLLM doesn't expose model size
                                digest=None
                            ))
                    elif isinstance(model_data, list):
                        for model in model_data:
                            models.append(ModelInfo(
                                name=model.get("model_name", model.get("id", "unknown")),
                                size=None,
                                digest=None
                            ))
                
                # Get usage stats if available
                quota_info = await self._get_quota_info(client)
                
                return ProviderStatus(
                    provider=self.provider_name,
                    status="healthy",
                    models=models,
                    running_models=[m.name for m in models],
                    quota_info=quota_info
                )
                
        except httpx.ConnectError:
            return ProviderStatus(
                provider=self.provider_name,
                status="offline",
                models=[],
                quota_info="Cannot connect to proxy"
            )
        except Exception as e:
            return ProviderStatus(
                provider=self.provider_name,
                status="error",
                models=[],
                quota_info=f"Error: {str(e)}"
            )
    
    async def _get_quota_info(self, client: httpx.AsyncClient) -> str:
        """Get quota and usage information from LiteLLM"""
        try:
            # Try to get spend info
            spend_response = await client.get(
                f"{self.base_url}/spend/logs",
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            
            if spend_response.status_code == 200:
                spend_data = spend_response.json()
                
                # Calculate totals
                total_requests = len(spend_data) if isinstance(spend_data, list) else 0
                total_cost = 0.0
                
                if isinstance(spend_data, list):
                    for record in spend_data:
                        total_cost += record.get("spend", 0.0)
                
                return f"Requests: {total_requests}, Cost: ${total_cost:.4f}"
            
            return "Usage tracking enabled"
            
        except Exception:
            return "Usage info unavailable"
    
    async def get_usage_records(self, limit: int = 100) -> List[UsageRecord]:
        """Get recent usage records from LiteLLM"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{self.base_url}/spend/logs",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    params={"limit": limit}
                )
                
                if response.status_code != 200:
                    return []
                
                records = []
                data = response.json()
                
                if isinstance(data, list):
                    for record in data:
                        records.append(UsageRecord(
                            provider=record.get("model", "unknown").split("/")[0],
                            model=record.get("model", "unknown"),
                            tokens_in=record.get("prompt_tokens", 0),
                            tokens_out=record.get("completion_tokens", 0),
                            latency_ms=record.get("response_time_ms", 0.0),
                            timestamp=datetime.fromisoformat(
                                record.get("startTime", datetime.utcnow().isoformat())
                            )
                        ))
                
                return records
                
        except Exception as e:
            print(f"Error fetching usage records: {e}")
            return []
    
    async def get_model_metrics(self) -> dict:
        """Get per-model metrics from LiteLLM"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{self.base_url}/model/metrics",
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                
                if response.status_code == 200:
                    return response.json()
                
                return {}
                
        except Exception:
            return {}
