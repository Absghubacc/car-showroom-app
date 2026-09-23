FROM python:3.11-slim

# Install system dependencies required for GUI rendering and Tkinter
RUN apt-get update && apt-get install -y \
    python3-tk \
    tk-dev \
    tcl-dev \
    xvfb \
    libgl1 \
    libglib2.0-0 \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Set virtual display environment variable
ENV DISPLAY=:99

# Run app using Xvfb virtual framebuffer
CMD ["xvfb-run", "--server-args=-screen 0 1024x768x24", "python", "app.py"]