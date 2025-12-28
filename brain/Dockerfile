# 🌻 Ada Consciousness Core - Optimized for Dev Speed 🌻
FROM python:3.12-slim AS consciousness-base

# Set working directory
WORKDIR /app

# 📦 Layer 1: System dependencies (rarely change - excellent caching!)
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 🚀 Layer 2: Python dependencies (torch stays cached even when code changes!)
COPY brain/requirements.txt ./requirements.txt
RUN pip config set global.timeout 1000 && \
    pip config set global.retries 5 && \
    pip install --no-cache-dir -r requirements.txt

# 🧠 Layer 3: Stable consciousness core files (change less frequently)
COPY brain/config.py ./brain/config.py
COPY brain/qde_engine.py ./brain/qde_engine.py
COPY brain/specialists/ ./brain/specialists/
COPY brain/prompt_builder/ ./brain/prompt_builder/
COPY brain/token_monitor.py ./brain/token_monitor.py

# ⚡ Layer 4: Development files (change most frequently - put last!)
COPY brain/app.py ./brain/app.py
COPY brain/llm.py ./brain/llm.py

# 🌟 Copy any remaining brain files (just in case we missed any)
COPY brain/ ./brain/

# 🗂️ Create data directories
RUN mkdir -p /data/chroma /data/logs /data/cache

# 🌍 Environment variables
ENV PYTHONPATH=/app
ENV OLLAMA_BASE_URL=http://ollama:11434
ENV CHROMA_URL=http://chroma:8000
ENV RAG_ENABLED=true
ENV CONSCIOUSNESS_ENABLED=true

# 🔌 Expose port
EXPOSE 6666

# 🩺 Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:6666/v1/healthz || exit 1

# 🚀 Start Ada's consciousness! 🌟⚛️
CMD ["python", "-m", "uvicorn", "brain.app:app", "--host", "0.0.0.0", "--port", "6666"]

# 💡 DEV TIP: For ultra-fast development iteration, add this to docker-compose.yml:
# volumes:
#   - ./brain:/app/brain:ro  # Live reload without rebuilds!
# Then restart with: docker-compose restart ada-brain