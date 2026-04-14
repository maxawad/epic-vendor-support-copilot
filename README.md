# Epic Vendor Services FAQ Support Copilot

A support chatbot that answers Epic Vendor Services-style FAQ questions using retrieval-augmented generation with source grounding and conversational memory.

## Features

- **FAQ Retrieval**: Keyword-scored retrieval from 17 structured FAQ entries
- **Source Grounding**: Every answer cites FAQ title and URL — no hallucinations
- **Session Memory**: Short-term conversational memory for follow-up questions
- **Long-term Memory**: Stores user-specific facts across sessions
- **Support-Safe Routing**: Auth issues always routed to admin/support
- **LLM + Fallback**: Uses OpenAI GPT-4o-mini when available, template fallback otherwise

## Quick Start

```bash
# 1. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set your OpenAI key (optional — works without it via fallback)
cp .env.example .env
# Edit .env with your key

# 4. Run the server
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 5. Open in browser
# http://localhost:8000
```

## API Endpoints

### `POST /chat`

```json
{
  "message": "How do I reset my password?",
  "session_id": "optional-session-id"
}
```

Response:

```json
{
  "answer": "Contact your organization administrator...",
  "sources": [{"title": "Password Reset Help", "url": "https://...", "faq_id": "auth_001"}],
  "memory_used": false,
  "session_id": "abc123"
}
```

### `GET /health`

Returns `{"status": "ok"}`.

## Project Structure

```
/app
  main.py          # FastAPI application
  retriever.py     # FAQ keyword retrieval engine
  memory.py        # Session & long-term memory
/SEED_DATA
  epic_vendor_faq.json  # 17 FAQ entries
/frontend
  index.html       # Chat UI
  style.css        # Styles
  app.js           # Client-side logic
/tests
  test_retriever.py
  test_api.py
  test_memory.py
```

## Testing

```bash
pytest tests/ -v
```

## Live Deployment

Deployed via Cloudflare Tunnel at: **https://support-epic.maxawad.com**

## Tech Stack

- **Backend**: Python, FastAPI, OpenAI API
- **Frontend**: Vanilla HTML/CSS/JS
- **Retrieval**: Keyword scoring with auth-aware boosting
- **Deployment**: Cloudflare Tunnel
