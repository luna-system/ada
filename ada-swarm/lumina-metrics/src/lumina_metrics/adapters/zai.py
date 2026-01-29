import os
import httpx
from typing import Optional
from ..models import ProviderStatus, ModelInfo

class ZaiAdapter:
    def __init__(self):
        self.api_key = os.getenv("ZAI_API_KEY")
        # Zhipu AI (GLM) uses open.bigmodel.cn
        self.base_url = "https://open.bigmodel.cn/api/paas/v4"

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
                # Query available models from Zhipu AI
                resp = await client.get(
                    f"{self.base_url}/models",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=10.0
                )
                resp.raise_for_status()
                data = resp.json()
                
                # Zhipu returns models in 'data' array
                models = [
                    ModelInfo(name=m.get('id', m.get('name', 'unknown')))
                    for m in data.get('data', [])
                ]
                
                # If no models returned, show known GLM models
                if not models:
                    models = [
                        ModelInfo(name="glm-4-flash"),
                        ModelInfo(name="glm-4-plus"),
                        ModelInfo(name="glm-4-air")
                    ]

                return ProviderStatus(
                    provider="z.ai",
                    status="online",
                    models=models,
                    quota_info="Check Zhipu dashboard for usage"
                )
        except Exception as e:
            return ProviderStatus(
                provider="z.ai",
                status=f"offline: {str(e)}",
                models=[]
            )
