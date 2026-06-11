
# Use a slim image for faster builds and smaller footprint
FROM python:3.11-slim

# Install system dependencies (needed for pandas/numpy wheels)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code (including the CSV file)
COPY . .

# Use the PORT environment variable provided by Cloud Run
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}

