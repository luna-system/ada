FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy brain code
COPY brain/ brain/

# Expose FastAPI port
EXPOSE 8000

# Run with uvicorn
CMD ["python", "-m", "uvicorn", "brain.app:app", "--host", "0.0.0.0", "--port", "8000"]
