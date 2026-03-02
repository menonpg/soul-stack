FROM python:3.12-slim

LABEL maintainer="Prahlad G. Menon <menon.prahlad@gmail.com>"
LABEL description="soul-stack: persistent memory layer for n8n and LLM agents"
LABEL version="1.0.0"

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl wget git build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js (for n8n)
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install n8n globally
RUN npm install -g n8n

# Python deps
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Create working directory
WORKDIR /workspace

# Copy soul server
COPY soul_server/ /app/soul_server/
COPY config/ /app/config/
COPY examples/ /app/examples/

# Copy startup script
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Default SOUL.md and MEMORY.md
RUN mkdir -p /data/soul
COPY config/default_soul.md /data/soul/SOUL.md
RUN touch /data/soul/MEMORY.md

# Expose ports
# 8000 = soul.py FastAPI
# 8888 = Jupyter Lab
# 5678 = n8n
# 3000 = Open WebUI (optional, via compose)
EXPOSE 8000 8888 5678

ENV SOUL_PATH=/data/soul/SOUL.md
ENV MEMORY_PATH=/data/soul/MEMORY.md
ENV N8N_USER_FOLDER=/data/n8n
ENV JUPYTER_TOKEN=""

VOLUME ["/data/soul", "/data/n8n"]

CMD ["/start.sh"]
