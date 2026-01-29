import os
from typing import Optional
from ..models import ProviderStatus, ModelInfo

class GoogleAdapter:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        # Known Gemini 3 models
        self.known_models = [
            "gemini-3-flash-preview",
            "gemini-3-pro-preview"
        ]

    async def get_status(self) -> ProviderStatus:
        if not self.api_key:
            return ProviderStatus(
                provider="google",
                status="offline: no API key",
                models=[],
                quota_info="Set GOOGLE_API_KEY environment variable"
            )

        try:
            # For now, just return known models
            # TODO: Query actual available models when API supports it
            models = [
                ModelInfo(name=model)
                for model in self.known_models
            ]

            return ProviderStatus(
                provider="google",
                status="online",
                models=models,
                quota_info="Quota resets every 5 hours"
            )
        except Exception as e:
            return ProviderStatus(
                provider="google",
                status=f"offline: {str(e)}",
                models=[]
            )
