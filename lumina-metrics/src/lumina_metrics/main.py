from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os

from .metrics import metrics_middleware, get_metrics
from .adapters.ollama import OllamaAdapter

app = FastAPI(title="Lumina Metrics 🐝✨")
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "static"))
ollama = OllamaAdapter()

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
    return templates.TemplateResponse(
        "dashboard.html", 
        {"request": request, "providers": [ollama_status]}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
