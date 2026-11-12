# Epic Vendor Services FAQ Support Copilot

A small support chatbot that answers vendor-portal FAQ questions. You type a question such as "How do I reset my password?", and it finds the most relevant FAQ entries, answers from them, and links the sources. Login and password problems are always sent to an administrator or support instead of inventing steps. It is a portfolio project that uses synthetic FAQ data modeled on a typical vendor services portal. It is not affiliated with Epic Systems and contains no real Epic data.

**Status:** working. It runs with no API keys using a built-in template answer mode. Setting an OpenAI key (optional) switches answers to GPT-4o-mini.

**Hosted instance:** [https://support-epic.maxawad.com](https://support-epic.maxawad.com) (may be offline at any time).

**Try it locally:** the app is a Python server (FastAPI) that also serves the chat page, so it is not a static site. Follow the Quick Start below and open http://localhost:8000.

## Features

- **FAQ Retrieval**: Keyword-scored retrieval from 17 structured FAQ entries across 4 categories
- **Source Grounding**: Every answer cites FAQ title and URL: no hallucinations
- **Session Memory**: Short-term conversational memory for follow-up questions with `memory_used` indicator
- **Long-term Memory**: Stores user-specific facts (e.g., "My admin is John") across sessions
- **Support-Safe Routing**: Authentication issues always routed to admin/support: never generates fake steps
- **LLM + Fallback**: Uses OpenAI GPT-4o-mini when available, template fallback otherwise
- **Modern Chat UI**: Clean, responsive interface with quick actions, source display, and memory badges

## Quick Start

```bash
# Clone the repo
git clone https://github.com/maxawad/epic-vendor-support-copilot.git
cd epic-vendor-support-copilot

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Optional: copy the example file and add your own OpenAI key.
# Without a key the app uses the template fallback.
cp .env.example .env

# Run the server
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Open in browser: http://localhost:8000
```

Or use the start script:

```bash
chmod +x start.sh
./start.sh
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
  "memory_hint": null,
  "session_id": "abc123"
}
```

### `GET /health`

Returns `{"status": "ok", "service": "Epic Vendor Services FAQ Copilot"}`.

## Project Structure

```
/app
  main.py            # FastAPI application with chat endpoint
  retriever.py       # FAQ keyword retrieval with auth-aware boosting
  memory.py          # Short-term session & long-term memory system
/SEED_DATA
  epic_vendor_faq.json   # 17 FAQ entries (7 auth, 3 billing, 3 reporting, 4 general)
/frontend
  index.html         # Chat UI
  style.css          # Modern responsive styles
  app.js             # Client-side chat logic
/tests
  test_retriever.py  # 10 retrieval tests
  test_api.py        # 9 API endpoint tests
  test_memory.py     # 12 memory system tests
requirements.txt     # Python dependencies
start.sh             # Quick-start script
```

## Testing

```bash
source venv/bin/activate
pytest tests/ -v
```

All 38 tests cover: FAQ loading/validation, keyword retrieval accuracy, auth boosting, API endpoints, session memory, long-term memory, and edge cases.

## Deployment

The hosted instance is deployed via Cloudflare Tunnel with systemd services for auto-restart:

- **API Service**: `epic-support-api.service`: runs uvicorn on port 8000
- **Tunnel Service**: `epic-support-tunnel.service`: runs cloudflared tunnel
- **Public URL**: [https://support-epic.maxawad.com](https://support-epic.maxawad.com)

## Tech Stack

- **Backend**: Python 3.12, FastAPI, OpenAI API (GPT-4o-mini)
- **Frontend**: Vanilla HTML/CSS/JS with Inter font
- **Retrieval**: Keyword scoring with auth-aware boosting
- **Memory**: In-memory session store + JSON-based long-term memory
- **Deployment**: Cloudflare Tunnel, systemd

## Notes

- Conversation memory lives in the server process. Long-term facts (for example "My admin is John") are written to `memory_store.json` next to the app, which is git-ignored. Do not put real personal data into the chat on a public deployment.
- The systemd unit files assume a specific server path and are examples only.
- No license file is included yet, so all rights are reserved by default.

## Credits

Built by Max Awad with AI assistance (see `AI_USAGE.md`). The FAQ content is synthetic.
