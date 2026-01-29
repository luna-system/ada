import os
import httpx
from typing import Optional
from ..models import ProviderStatus, ModelInfo

class ZaiAdapter:
    def __init__(self):
        self.api_key = os.getenv("ZAI_API_KEY")
        self.base_url = "https://api.z.ai/v1"

    async def get_status(self) -> ProviderStatus:
        if not self.api_key:
            return ProviderStatus(
                provider="z.ai",
                status="offline: no API key",
                models=[],
                quota_info="Set ZAI_API_KEY environment variable"
            )

        try:
            async with httpx.AsyncClient() as client:
                # Query available models
                resp = await client.get(
                    f"{self.base_url}/models",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=10.0
                )
                resp.raise_for_status()
                data = resp.json()
                
                models = [
                    ModelInfo(name=m['id'])
                    for m in data.get('data', [])
                ]

                return ProviderStatus(
                    provider="z.ai",
                    status="online",
                    models=models,
                    quota_info="Check Z.ai dashboard for usage"
                )
        except Exception as e:
            return ProviderStatus(
                provider="z.ai",
                status=f"offline: {str(e)}",
                models=[]
            )
