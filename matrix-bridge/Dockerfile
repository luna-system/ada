FROM python:3.13-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY *.py .

# Create data directory
RUN mkdir -p /data

# Run as non-root user
RUN useradd -m -u 1000 ada && chown -R ada:ada /app /data
USER ada

CMD ["python", "bridge.py"]
