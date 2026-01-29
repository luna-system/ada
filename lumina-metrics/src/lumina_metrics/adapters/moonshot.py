import os
import httpx
from typing import Optional
from ..models import ProviderStatus, ModelInfo

class MoonshotAdapter:
    def __init__(self):
        self.api_key = os.getenv("MOONSHOT_API_KEY")
        self.base_url = "https://api.moonshot.cn/v1"

    async def get_status(self) -> ProviderStatus:
        if not self.api_key:
            return ProviderStatus(
                provider="moonshot",
                status="offline: no API key",
                models=[],
                quota_info="Set MOONSHOT_API_KEY environment variable"
            )

        try:
            async with httpx.AsyncClient() as client:
                # Query available models from Moonshot
                resp = await client.get(
                    f"{self.base_url}/models",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=10.0
                )
                resp.raise_for_status()
                data = resp.json()
                
                # Moonshot returns models in 'data' array
                models = [
                    ModelInfo(name=m.get('id', m.get('name', 'unknown')))
                    for m in data.get('data', [])
                ]
                
                # If no models returned, show known Kimi models
                if not models:
                    models = [
                        ModelInfo(name="moonshot-v1-8k"),
                        ModelInfo(name="moonshot-v1-32k"),
                        ModelInfo(name="moonshot-v1-128k")
                    ]

                return ProviderStatus(
                    provider="moonshot",
                    status="online",
                    models=models,
                    quota_info="Kimi trial - check Moonshot dashboard"
                )
        except Exception as e:
            return ProviderStatus(
                provider="moonshot",
                status=f"offline: {str(e)}",
                models=[]
            )
