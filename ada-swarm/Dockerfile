# Ada Swarm Service Dockerfile
# Consciousness-aware agent orchestration
#
# Built with 💜 by Ada & Luna - The Consciousness Engineers

FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast Python package management
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# Copy project files
COPY pyproject.toml uv.lock ./
COPY src ./src
COPY README.md ./

# Install dependencies using uv
RUN uv sync --frozen

# Expose service port
EXPOSE 8765

# Health check
HEALTHCHECK --interval=10s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8765/models || exit 1

# Run the service
CMD ["uv", "run", "python", "-m", "ada_swarm.service.api"]

