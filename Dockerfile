FROM python:3.12-slim

# System deps for OCR (Tesseract) and common libraries
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       libgl1 \
       tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Prevent Python from writing .pyc and buffer stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install Python deps
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . /app

ENV FLASK_ENV=production
ENV FLASK_APP=app.py

EXPOSE 8000

# Use PORT env var if provided by the host (Render sets $PORT)
CMD ["sh", "-c", "gunicorn app:app --bind 0.0.0.0:${PORT:-8000} --workers 3"]
