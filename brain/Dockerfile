FROM python:3.13-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# Copy project metadata for lock install
COPY pyproject.toml uv.lock ./
RUN uv venv && uv sync --frozen --no-dev

# Copy source
COPY . .

ENV PATH="/app/.venv/bin:${PATH}"

# Run gunicorn with explicit config
CMD ["gunicorn", "-c", "brain/gunicorn_config.py", "brain.wsgi:app"]
