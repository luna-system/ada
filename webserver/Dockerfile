FROM python:3.13-slim

WORKDIR /app

# Install curl to fetch uv
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install uv (Python package/deps manager)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# Copy project metadata and lock file first for better caching
COPY pyproject.toml uv.lock ./

# Create a project virtualenv explicitly and install dependencies into it
RUN uv venv && uv sync --frozen --no-dev

# Now copy the rest of the source
COPY . .

# Ensure our virtualenv is on PATH for runtime
ENV PATH="/app/.venv/bin:${PATH}"

# Run via uv so the project virtualenv is always used, avoiding PATH/shebang issues
CMD ["uv", "run", "gunicorn", "webserver.app:app", "--bind", "0.0.0.0:5000"]