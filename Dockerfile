# Inherit from your pre-built base image (No apt-get needed!)
FROM abhishaccount/car-showroom-base:latest

WORKDIR /app

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

ENV DISPLAY=:99

CMD ["xvfb-run", "--server-args=-screen 0 1024x768x24", "python", "app.py"]