# Use Python 3.11 slim base
FROM python:3.11-slim

WORKDIR /app

# Install system packages and git-lfs
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    git \
    git-lfs \
    libatlas-base-dev \
    && rm -rf /var/lib/apt/lists/*

# Enable Git LFS
RUN git lfs install

# Copy the entire repo including .git and LFS pointer files
COPY . .

# Pull LFS files (this must come after COPY)
RUN git lfs pull

# Upgrade pip and install requirements
RUN pip install --upgrade pip
RUN pip install \
    scikit-learn==1.4.2 \
    numpy==1.26.4 \
    -r requirements.txt

# Optional check that models exist
RUN ls -lh athlete_app/model/

# Check model loads before starting API
CMD ["bash", "-c", "python check/model.py && uvicorn main:app --host 0.0.0.0 --port 8000"]