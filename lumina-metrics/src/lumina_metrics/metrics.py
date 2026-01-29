from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request, Response
import time

# Metrics
REQUEST_COUNT = Counter(
    "lumina_request_total", 
    "Total request count", 
    ["method", "endpoint", "http_status"]
)
REQUEST_LATENCY = Histogram(
    "lumina_request_duration_seconds", 
    "Request latency", 
    ["method", "endpoint"]
)

async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        http_status=response.status_code
    ).inc()
    
    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(process_time)
    
    return response

def get_metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
