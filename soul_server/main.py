"""
soul-stack — soul.py REST API
Wraps HybridAgent as a stateful HTTP service.
n8n workflows call this to get persistent memory.
"""
import os, uuid, time
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="soul.py API",
    description="Persistent memory layer for n8n and LLM agents",
    version="1.0.0"
)
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])

# Lazy import so startup is fast even without API keys
_agents = {}

def get_agent(agent_id: str = "default"):
    """Get or create a named agent instance."""
    if agent_id not in _agents:
        import sys
        sys.path.insert(0, "/app")
        from hybrid_agent import HybridAgent

        soul_path   = os.environ.get("SOUL_PATH",   "/data/soul/SOUL.md")
        memory_path = os.environ.get("MEMORY_PATH", f"/data/soul/MEMORY_{agent_id}.md")

        # Create per-agent memory file if needed
        if not os.path.exists(memory_path):
            open(memory_path, "w").write("# MEMORY.md\n")

        _agents[agent_id] = HybridAgent(
            soul_path=soul_path,
            memory_path=memory_path,
            mode=os.environ.get("RETRIEVAL_MODE", "auto"),
            # RAG backend: qdrant | chromadb | bm25 (default bm25 — zero config)
            rag_backend=os.environ.get("SOUL_BACKEND", "bm25"),
            qdrant_url=os.environ.get("QDRANT_URL", ""),
            qdrant_api_key=os.environ.get("QDRANT_API_KEY", ""),
            azure_embedding_endpoint=os.environ.get("AZURE_EMBEDDING_ENDPOINT", ""),
            azure_embedding_key=os.environ.get("AZURE_EMBEDDING_KEY", ""),
            # OpenAI direct embeddings (alternative to Azure)
            openai_api_key=os.environ.get("OPENAI_API_KEY", ""),
            openai_embedding_model=os.environ.get("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
            collection_name=f"soul_{agent_id}",
        )
    return _agents[agent_id]


@app.get("/")
async def root():
    return {
        "name": "soul-stack",
        "version": "1.0.0",
        "description": "Persistent memory layer for n8n and LLM agents",
        "endpoints": {
            "POST /ask": "Ask the agent (with memory)",
            "POST /remember": "Write a note to memory",
            "GET  /memory": "Read current MEMORY.md",
            "POST /reset": "Clear conversation history",
            "GET  /health": "Health check",
        }
    }


@app.post("/ask")
async def ask(request: Request):
    """
    Ask the agent. Memory persists across calls.

    Body: { "question": "...", "agent_id": "default", "mode": "auto" }
    Returns: { "answer": "...", "route": "RAG|RLM", "agent_id": "...", ... }
    """
    try:
        body = await request.json()
        question = body.get("question", "").strip()
        agent_id = body.get("agent_id", "default")
        mode     = body.get("mode", None)

        if not question:
            return JSONResponse({"error": "question is required"}, status_code=400)

        agent = get_agent(agent_id)
        if mode:
            agent.mode = mode

        result = agent.ask(question)

        return {
            "answer":       result["answer"],
            "route":        result["route"],
            "router_ms":    result["router_ms"],
            "retrieval_ms": result["retrieval_ms"],
            "total_ms":     result["total_ms"],
            "agent_id":     agent_id,
        }
    except Exception as e:
        import traceback
        return JSONResponse({"error": str(e), "trace": traceback.format_exc()},
                            status_code=500)


@app.post("/remember")
async def remember(request: Request):
    """
    Write a note directly to memory without asking a question.
    Useful for n8n workflows that want to log events.

    Body: { "note": "...", "agent_id": "default" }
    """
    try:
        body = await request.json()
        note     = body.get("note", "").strip()
        agent_id = body.get("agent_id", "default")

        if not note:
            return JSONResponse({"error": "note is required"}, status_code=400)

        agent = get_agent(agent_id)
        agent.remember(note)
        return {"ok": True, "agent_id": agent_id}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/memory")
async def get_memory(agent_id: str = "default"):
    """Read the current MEMORY.md for an agent."""
    memory_path = os.environ.get("MEMORY_PATH",
                                  f"/data/soul/MEMORY_{agent_id}.md")
    try:
        content = open(memory_path).read()
        return {"agent_id": agent_id, "memory": content,
                "size_bytes": len(content)}
    except FileNotFoundError:
        return {"agent_id": agent_id, "memory": "", "size_bytes": 0}


@app.post("/reset")
async def reset(request: Request):
    """Clear conversation history for an agent (memory file preserved)."""
    body = await request.json()
    agent_id = body.get("agent_id", "default")
    if agent_id in _agents:
        _agents[agent_id].reset_conversation()
    return {"ok": True, "agent_id": agent_id}


@app.get("/health")
async def health():
    return {
        "ok": True,
        "agents_loaded": list(_agents.keys()),
        "anthropic_key": bool(os.environ.get("ANTHROPIC_API_KEY")),
        "qdrant_configured": bool(os.environ.get("QDRANT_URL")),
        "version": "1.0.0"
    }
