FROM abhishaccount/car-showroom-base:latest

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DISPLAY=:99

CMD ["xvfb-run", "--server-num=99", "--server-args=-screen 0 1024x768x24", "python", "app.py"]