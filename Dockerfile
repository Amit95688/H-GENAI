# Simple Dockerfile for H-GEN-AI
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Default: run Flask (override with docker run for MySQL etc.)
ENV FLASK_APP=app.main:app
EXPOSE 5000
CMD ["python", "main.py"]
