import json
import time
from pathlib import Path
from typing import Optional

MAX_HISTORY = 20
LONG_TERM_PATH = Path(__file__).parent.parent / "memory_store.json"

_sessions: dict[str, list[dict]] = {}


def get_history(session_id: str) -> list[dict]:
    return _sessions.get(session_id, [])


def add_message(session_id: str, role: str, content: str) -> None:
    if session_id not in _sessions:
        _sessions[session_id] = []
    _sessions[session_id].append({"role": role, "content": content})
    if len(_sessions[session_id]) > MAX_HISTORY:
        _sessions[session_id] = _sessions[session_id][-MAX_HISTORY:]


def has_history(session_id: str) -> bool:
    return bool(_sessions.get(session_id))


def clear_session(session_id: str) -> None:
    _sessions.pop(session_id, None)


def format_history_for_prompt(session_id: str) -> str:
    history = get_history(session_id)
    if not history:
        return ""
    lines = []
    for msg in history[-6:]:
        prefix = "User" if msg["role"] == "user" else "Assistant"
        lines.append(f"{prefix}: {msg['content']}")
    return "\n".join(lines)


def get_memory_context_hint(session_id: str) -> Optional[str]:
    """Return a short hint about what previous conversation covered, if any."""
    history = get_history(session_id)
    if not history:
        return None
    user_msgs = [m["content"] for m in history if m["role"] == "user"]
    if not user_msgs:
        return None
    last = user_msgs[-1]
    if len(last) > 60:
        last = last[:60] + "..."
    return f"Used your previous question: \"{last}\""


# --- Long-term memory (stretch goal) ---

def _load_long_term() -> dict:
    if LONG_TERM_PATH.exists():
        with open(LONG_TERM_PATH, "r") as f:
            return json.load(f)
    return {}


def _save_long_term(data: dict) -> None:
    with open(LONG_TERM_PATH, "w") as f:
        json.dump(data, f, indent=2)


STORE_PATTERNS = [
    "my admin is", "my name is", "my organization is", "my org is",
    "my email is", "my phone is", "i work at", "my role is",
]


def should_store_long_term(message: str) -> bool:
    lower = message.lower()
    return any(p in lower for p in STORE_PATTERNS)


def store_long_term(session_id: str, message: str) -> None:
    data = _load_long_term()
    if session_id not in data:
        data[session_id] = []
    data[session_id].append({
        "content": message,
        "timestamp": time.time(),
    })
    _save_long_term(data)


def get_long_term(session_id: str) -> list[dict]:
    data = _load_long_term()
    return data.get(session_id, [])
