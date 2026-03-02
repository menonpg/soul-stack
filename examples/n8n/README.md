# n8n + soul.py Examples

These examples show how to make your n8n workflows stateful using soul.py.

## Setup

soul.py API is available inside n8n at: `http://soul:8000`
(or `http://localhost:8000` if running outside Docker)

## Example 1: Basic Memory Call (HTTP Request node)

In any n8n workflow, add an **HTTP Request** node:

- Method: POST
- URL: `http://soul:8000/ask`
- Body (JSON):
```json
{
  "question": "{{ $json.message }}",
  "agent_id": "{{ $json.user_id }}"
}
```

The response includes `answer`, `route` (RAG/RLM), and latency stats.

## Example 2: Log an Event to Memory

Use `/remember` to log workflow events without asking a question:

- Method: POST  
- URL: `http://soul:8000/remember`
- Body:
```json
{
  "note": "User {{ $json.user_id }} completed onboarding at {{ $now }}",
  "agent_id": "{{ $json.user_id }}"
}
```

## Example 3: Per-User Memory

Pass `agent_id` to maintain separate memory per user/customer:

```json
{
  "question": "What were my last 3 orders?",
  "agent_id": "customer_{{ $json.customer_id }}"
}
```

Each agent_id gets its own MEMORY.md file — completely isolated.

## Example 4: Customer Support Bot

Workflow:
1. Webhook → receives customer message
2. HTTP Request → POST /ask with customer_id as agent_id
3. soul.py recalls previous interactions automatically
4. Respond with context-aware answer
5. (Optional) POST /remember to log ticket resolution

## Why This Works

n8n is stateless — each workflow execution forgets everything.
soul.py adds a persistent memory layer that survives across:
- Workflow executions
- Container restarts  
- n8n updates

Your workflows now remember customers, context, and history.
