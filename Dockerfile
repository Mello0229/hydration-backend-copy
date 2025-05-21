# Use Python 3.11 slim base
FROM python:3.11-slim

WORKDIR /app

# Install system packages
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    libatlas-base-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy code and model files
COPY . .

# Upgrade pip and install correct ML packages
RUN pip install --upgrade pip
RUN pip install \
    scikit-learn==1.4.2 \
    numpy==1.26.4 \
    -r requirements.txt

# Optional check that models exist
RUN ls -lh athlete_app/model/

ENV PYTHONPATH=/app

# Check model loads before starting API
CMD ["bash", "-c", "python check/model.py && uvicorn main:app --host 0.0.0.0 --port 8000"]
