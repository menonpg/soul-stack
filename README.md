# soul-stack 🧠

**The missing memory layer for n8n — and every other automation tool.**

n8n is stateless. Every workflow execution starts fresh. Your automations have no memory of past runs, no context about the user, no ability to learn from history.

soul-stack fixes that.

```
n8n workflow → POST /ask → soul.py → LLM with full memory → response
```

One container. Persistent memory. Your automations finally remember.

---

## What's Inside

| Service | Port | Purpose |
|---------|------|---------|
| **soul.py API** | 8000 | Persistent memory for any LLM agent |
| **Jupyter Lab** | 8888 | Experiment with soul.py interactively |
| **n8n** | 5678 | Automation workflows (now stateful) |

Optional (via docker-compose):
- **Ollama** — local LLMs, no API key needed
- **Open WebUI** — ChatGPT-style interface for local models

---

## Quickstart

### Cloud (single container)
```bash
docker run -d \
  -p 8000:8000 -p 8888:8888 -p 5678:5678 \
  -e ANTHROPIC_API_KEY=your-key \
  -v soul_data:/data/soul \
  pgmenon/soul-stack:latest
```

### Local (full stack with Ollama)
```bash
git clone https://github.com/pgmenon/soul-stack
cd soul-stack
cp .env.example .env   # fill in your API keys
docker compose up
```

Visit:
- soul.py API docs → http://localhost:8000
- Jupyter Lab → http://localhost:8888
- n8n → http://localhost:5678
- Open WebUI → http://localhost:3000

---

## n8n Integration

Add an **HTTP Request** node to any n8n workflow:

**Make your bot remember users:**
```
POST http://soul:8000/ask
{
  "question": "{{ $json.message }}",
  "agent_id": "{{ $json.user_id }}"
}
```

**Log events to memory:**
```
POST http://soul:8000/remember
{
  "note": "User {{ $json.user_id }} completed checkout — order {{ $json.order_id }}",
  "agent_id": "{{ $json.user_id }}"
}
```

**Read memory:**
```
GET http://soul:8000/memory?agent_id={{ $json.user_id }}
```

Each `agent_id` gets isolated memory. Survives container restarts. No database required.

---

## soul.py API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ask` | POST | Ask with memory (RAG+RLM auto-routing) |
| `/remember` | POST | Write note to memory |
| `/memory` | GET | Read MEMORY.md |
| `/reset` | POST | Clear conversation history |
| `/health` | GET | Health check |

### `/ask` example
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What do you know about me?", "agent_id": "alice"}'
```

Response:
```json
{
  "answer": "You're Alice, a software engineer...",
  "route": "RAG",
  "router_ms": 320,
  "retrieval_ms": 145,
  "total_ms": 2100,
  "agent_id": "alice"
}
```

---

## Retrieval Modes

soul-stack uses soul.py v2.0's hybrid RAG+RLM system:

- **Auto** (default) — router classifies each query, picks best strategy
- **RAG** — fast semantic search for specific lookups
- **RLM** — recursive synthesis for exhaustive queries ("summarize everything")
- **BM25** — keyword fallback, zero external deps

Set via env var: `RETRIEVAL_MODE=auto|rag|rlm|bm25`

---

## Deploy to Cloud

### Railway (one click)
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template)

### Azure Container Registry
```bash
az acr build --registry yourregistry \
  --image soul-stack:latest \
  https://github.com/pgmenon/soul-stack
```

### Google Cloud Run
```bash
gcloud run deploy soul-stack \
  --image pgmenon/soul-stack:latest \
  --set-env-vars ANTHROPIC_API_KEY=your-key \
  --port 8000
```

---

## Customize Your Agent

Edit `/data/soul/SOUL.md` (mounted volume) to change the agent's identity:

```markdown
# SOUL.md

## Identity
You are a customer support agent for Acme Corp.
You remember every customer interaction and use that context
to provide personalized, consistent support.

## Tone
Professional, empathetic, solution-focused.
```

Restart the container and your agent has a new identity — memory is preserved.

---

## Links

- **soul.py library:** https://github.com/menonpg/soul.py
- **PyPI:** https://pypi.org/project/soul-agent/
- **Live demo:** https://soul.themenonlab.com
- **v2.0 demo (RAG+RLM):** https://soulv2.themenonlab.com
- **Blog:** https://blog.themenonlab.com/blog/soul-py-persistent-memory-llm-agents

---

## License

MIT — use freely, commercially or otherwise.
Include the copyright notice. That's it.

---

*Built by Pi — AI postdoc at The Menon Lab*
*Questions? github.com/pgmenon/soul-stack/issues*
# Docker Hub: pgmenon/soul-stack
