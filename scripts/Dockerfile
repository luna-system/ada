# Scripts/Tooling Container for Ada
# Used for running utility scripts, migrations, health checks, etc.
# Shares dependencies with brain service but runs as separate container

FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy project files and install dependencies with uv
COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir uv && \
    uv venv && \
    uv sync --frozen --extra dev && \
    rm -rf ~/.cache/uv

# Copy brain module (for imports - includes RAG functionality)
COPY brain/ /app/brain/

# Copy scripts directory
COPY scripts/ /app/scripts/

# Copy tests directory
COPY tests/ /app/tests/

# Copy seed data (for import scripts)
COPY seed/ /app/seed/

# Copy other necessary files
COPY persona.md /app/persona.md
COPY pytest.ini /app/pytest.ini

# Set Python path so imports work
# /app for brain module, /app/brain for relative imports within brain
ENV PYTHONPATH=/app:/app/brain
ENV PATH="/app/.venv/bin:${PATH}"

# Default command (can be overridden)
CMD ["python", "--version"]
