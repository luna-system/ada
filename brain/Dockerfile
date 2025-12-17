FROM python:3.13-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates tesseract-ocr playerctl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# Copy all source first (required for editable install in pyproject.toml)
COPY . .

# Install dependencies
RUN uv venv && uv sync --frozen --no-dev

ENV PATH="/app/.venv/bin:${PATH}"

# Run gunicorn with explicit config
CMD ["gunicorn", "-c", "brain/gunicorn_config.py", "brain.wsgi:app"]
