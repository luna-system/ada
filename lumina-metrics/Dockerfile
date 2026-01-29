# Lumina Metrics Dockerfile
# Observability dashboard for Ada Swarm
#
# Built with 💜 by Ada & Luna - The Consciousness Engineers

FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast Python package management
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# Copy project files
COPY pyproject.toml uv.lock* ./
COPY src ./src
COPY README.md* ./

# Install dependencies using uv
RUN uv sync --frozen || uv sync

# Expose service port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=10s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Run the service
CMD ["uv", "run", "uvicorn", "lumina_metrics.main:app", "--host", "0.0.0.0", "--port", "8001"]

