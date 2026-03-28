FROM python:3.11-slim

WORKDIR /app

# Install system dependencies that might be needed by the agent's simulated environment
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    bash \
    procps \
    nano \
    vim \
    curl \
    grep \
    sed \
    gawk \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ensure necessary directories exist
RUN mkdir -p /var/log /app/config /workspace && \
    chmod -R 777 /var/log /app/config /workspace

EXPOSE 7860

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
