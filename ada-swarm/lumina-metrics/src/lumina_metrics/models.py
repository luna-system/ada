from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ModelInfo(BaseModel):
    name: str
    size: Optional[int] = None
    digest: Optional[str] = None
    modified_at: Optional[datetime] = None

class ProviderStatus(BaseModel):
    provider: str
    status: str
    models: List[ModelInfo] = []
    running_models: List[str] = []
    quota_info: Optional[str] = None
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class UsageRecord(BaseModel):
    provider: str
    model: str
    tokens_in: int
    tokens_out: int
    latency_ms: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)
