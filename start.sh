#!/bin/bash
set -e

echo "
╔═══════════════════════════════════════════════════════╗
║              soul-stack v1.0                          ║
║   The missing memory layer for n8n automation         ║
╠═══════════════════════════════════════════════════════╣
║  soul.py API  → http://localhost:8000                 ║
║  Jupyter Lab  → http://localhost:8888                 ║
║  n8n          → http://localhost:5678                 ║
║                                                       ║
║  Docs: github.com/menonpg/soul-stack                  ║
╚═══════════════════════════════════════════════════════╝
"

# Start soul.py FastAPI server
echo "[soul-stack] Starting soul.py API on port 8000..."
cd /app/soul_server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
SOUL_PID=$!

# Start Jupyter Lab
echo "[soul-stack] Starting Jupyter Lab on port 8888..."
jupyter lab \
    --ip=0.0.0.0 \
    --port=8888 \
    --no-browser \
    --notebook-dir=/app/examples \
    --ServerApp.token="${JUPYTER_TOKEN}" \
    --ServerApp.password="" \
    --ServerApp.allow_origin="*" &
JUPYTER_PID=$!

# Start n8n
echo "[soul-stack] Starting n8n on port 5678..."
N8N_USER_FOLDER=/data/n8n \
N8N_BASIC_AUTH_ACTIVE=false \
EXECUTIONS_PROCESS=main \
n8n start &
N8N_PID=$!

echo "[soul-stack] All services started."
echo "[soul-stack] soul.py PID: $SOUL_PID"
echo "[soul-stack] Jupyter PID: $JUPYTER_PID"
echo "[soul-stack] n8n PID: $N8N_PID"

# Wait for any process to exit
wait -n $SOUL_PID $JUPYTER_PID $N8N_PID
echo "[soul-stack] A service exited. Check logs above."
