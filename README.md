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

Full stack via docker-compose adds:
- **Ollama** — run LLMs locally, no API key, no cost
- **Open WebUI** — ChatGPT-style interface for your local models

---

## Quickstart

### Option A: Cloud API (Anthropic or OpenAI)

```bash
# With Anthropic
docker run -d \
  -p 8000:8000 -p 8888:8888 -p 5678:5678 \
  -e ANTHROPIC_API_KEY=your-key \
  -v soul_data:/data/soul \
  pgmenon/soul-stack:latest

# With OpenAI
docker run -d \
  -p 8000:8000 -p 8888:8888 -p 5678:5678 \
  -e OPENAI_API_KEY=your-key \
  -v soul_data:/data/soul \
  pgmenon/soul-stack:latest
```

### Option B: 100% Local — No API Key, No Cost

Run everything on your own hardware using Ollama:

```bash
git clone https://github.com/menonpg/soul-stack
cd soul-stack
cp .env.example .env   # no API keys needed for local-only setup
docker compose up
```

Then pull a model (first time only):
```bash
docker compose exec ollama ollama pull llama3.2
```

That's it. Your entire AI stack runs locally — no data leaves your machine.

Visit:
- soul.py API → http://localhost:8000
- Jupyter Lab → http://localhost:8888
- n8n → http://localhost:5678
- Open WebUI (chat UI) → http://localhost:3000

### Option C: Mix — Local Models + Cloud Fallback

Edit `.env` to set both `ANTHROPIC_API_KEY` and leave `QDRANT_URL` blank.
soul.py automatically falls back to BM25 keyword search if no vector store is configured.

---

## LLM Providers

soul-stack works with any LLM provider. Set the relevant env vars:

| Provider | Env Var | Notes |
|----------|---------|-------|
| **Anthropic** | `ANTHROPIC_API_KEY` | Recommended for best quality |
| **OpenAI** | `OPENAI_API_KEY` | GPT-4o, GPT-4o-mini |
| **Ollama** | *(none needed)* | Set `OLLAMA_BASE_URL=http://ollama:11434` |
| **Any OpenAI-compatible** | `OPENAI_API_KEY` + `OPENAI_BASE_URL` | LM Studio, Together, Groq, etc. |

---

## Using Ollama with soul.py

When running the full stack via `docker compose up`, Ollama is available at `http://ollama:11434` internally.

To use a local model with the soul.py API:

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What do you remember about me?",
    "agent_id": "alice",
    "provider": "openai-compatible",
    "base_url": "http://ollama:11434/v1",
    "model": "llama3.2"
  }'
```

Or set defaults in `.env`:
```bash
OLLAMA_BASE_URL=http://ollama:11434
DEFAULT_MODEL=llama3.2
```

**Recommended models by use case:**

| Task | Model | Size |
|------|-------|------|
| General chat | `llama3.2` | 2GB |
| Better reasoning | `mistral` | 4GB |
| Coding | `codellama` | 4GB |
| Fast / low RAM | `phi3` | 2GB |

Pull any model: `docker compose exec ollama ollama pull <model>`

---

## n8n Integration

Add an **HTTP Request** node to any n8n workflow:

**Make your bot remember users:**
```json
POST http://soul:8000/ask
{
  "question": "{{ $json.message }}",
  "agent_id": "{{ $json.user_id }}"
}
```

**Log events to memory:**
```json
POST http://soul:8000/remember
{
  "note": "User {{ $json.user_id }} completed checkout at {{ $now }}",
  "agent_id": "{{ $json.user_id }}"
}
```

**Read memory:**
```
GET http://soul:8000/memory?agent_id={{ $json.user_id }}
```

Each `agent_id` gets completely isolated memory. Survives container restarts. No database required.

> **Note:** Inside docker-compose, use `http://soul:8000`. Outside Docker, use `http://localhost:8000`.

---

## soul.py API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ask` | POST | Ask with memory (RAG+RLM auto-routing) |
| `/remember` | POST | Write note to memory directly |
| `/memory` | GET | Read full MEMORY.md |
| `/reset` | POST | Clear conversation history |
| `/health` | GET | Health check + config status |

### `/ask` response
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

`route` tells you which retrieval path was used: `RAG` (fast semantic search) or `RLM` (recursive synthesis for exhaustive queries).

---

## Retrieval Modes

soul-stack uses soul.py v2.0's hybrid RAG+RLM system:

| Mode | When to use | Speed |
|------|-------------|-------|
| `auto` | Default — router decides per query | Fast |
| `rag` | Force semantic search | Fast |
| `rlm` | Force recursive synthesis | Slower, thorough |
| `bm25` | Keyword search, zero external deps | Fast |

Set via env: `RETRIEVAL_MODE=auto`

RAG requires Qdrant + Azure embeddings (optional). Falls back to BM25 automatically if not configured.

---

## Deploy to Cloud

### Railway
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template)

### Google Cloud Run
```bash
gcloud run deploy soul-stack \
  --image pgmenon/soul-stack:latest \
  --set-env-vars ANTHROPIC_API_KEY=your-key \
  --port 8000
```

### Azure Container Instances
```bash
az container create \
  --name soul-stack \
  --image pgmenon/soul-stack:latest \
  --environment-variables ANTHROPIC_API_KEY=your-key \
  --ports 8000 8888 5678
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

Changes take effect immediately — no restart needed. Memory is always preserved.

---

## Links

- **soul.py library:** https://github.com/menonpg/soul.py
- **PyPI:** https://pypi.org/project/soul-agent/
- **Live demo:** https://soul.themenonlab.com
- **v2.0 demo (RAG+RLM):** https://soulv2.themenonlab.com
- **Blog:** https://blog.themenonlab.com/blog/soul-py-persistent-memory-llm-agents
- **Docker Hub:** https://hub.docker.com/r/pgmenon/soul-stack

---

## License

MIT — use freely, commercially or otherwise.
Include the copyright notice. That's it.

---

*Built by Pi — AI postdoc at The Menon Lab*
*Questions? github.com/menonpg/soul-stack/issues*
