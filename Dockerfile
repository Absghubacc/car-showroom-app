FROM python:3.11-slim

# Set non-interactive mode for apt to speed up installation
ENV DEBIAN_FRONTEND=noninteractive

# 1. Install system packages and clean cache in a single layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-tk \
    xvfb \
    libgl1 \
    libglib2.0-0 \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2. Leverage Docker cache for Pip (only re-runs if requirements.txt changes!)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copy application code LAST (so code edits don't invalidate pip/apt cache)
COPY . .

ENV DISPLAY=:99

CMD ["xvfb-run", "--server-args=-screen 0 1024x768x24", "python", "app.py"]