# Base image
FROM python:3.11-slim

# System setup
WORKDIR /app
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Default command (Streamlit entrypoint, uses Railway's PORT variable)
CMD streamlit run app.py --server.port=${PORT:-8501} --server.address=0.0.0.0
