from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os

from .metrics import metrics_middleware, get_metrics
from .adapters.ollama import OllamaAdapter
from .adapters.google import GoogleAdapter
from .adapters.zai import ZaiAdapter
from .adapters.moonshot import MoonshotAdapter
from .adapters.litellm import LiteLLMAdapter

app = FastAPI(title="Lumina Metrics 🐝✨")
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "static"))
ollama = OllamaAdapter()
google = GoogleAdapter()
zai = ZaiAdapter()
moonshot = MoonshotAdapter()
litellm = LiteLLMAdapter()

@app.middleware("http")
async def add_metrics_middleware(request: Request, call_next):
    return await metrics_middleware(request, call_next)

@app.get("/status")
async def status():
    return {"status": "ok", "service": "lumina-metrics"}

@app.get("/metrics")
async def metrics():
    return get_metrics()

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    ollama_status = await ollama.get_status()
    google_status = await google.get_status()
    zai_status = await zai.get_status()
    moonshot_status = await moonshot.get_status()
    litellm_status = await litellm.get_status()
    
    providers = [litellm_status, ollama_status, google_status, zai_status, moonshot_status]
    
    return templates.TemplateResponse(
        "dashboard.html", 
        {"request": request, "providers": providers}
    )

@app.get("/litellm/usage")
async def litellm_usage(limit: int = 100):
    """Get recent LiteLLM usage records"""
    records = await litellm.get_usage_records(limit=limit)
    return {"records": records, "count": len(records)}

@app.get("/litellm/metrics")
async def litellm_metrics():
    """Get per-model metrics from LiteLLM"""
    metrics = await litellm.get_model_metrics()
    return metrics

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
