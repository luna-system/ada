import httpx
from typing import Optional
from ..models import ProviderStatus, ModelInfo

class OllamaAdapter:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url

    async def get_status(self) -> ProviderStatus:
        try:
            async with httpx.AsyncClient() as client:
                # Get available models
                tags_resp = await client.get(f"{self.base_url}/api/tags")
                tags_resp.raise_for_status()
                tags_data = tags_resp.json()
                
                models = [
                    ModelInfo(name=m['name'], size=m.get('size'), digest=m.get('digest'))
                    for m in tags_data.get('models', [])
                ]

                # Get running models
                ps_resp = await client.get(f"{self.base_url}/api/ps")
                ps_resp.raise_for_status()
                ps_data = ps_resp.json()
                running = [m['name'] for m in ps_data.get('models', [])]

                return ProviderStatus(
                    provider="ollama",
                    status="online",
                    models=models,
                    running_models=running
                )
        except Exception as e:
            return ProviderStatus(
                provider="ollama",
                status=f"offline: {str(e)}",
                models=[],
                running_models=[]
            )
