import os
import uuid
from pathlib import Path

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Optional

from .retriever import retrieve, load_faq
from .memory import (
    add_message, has_history, format_history_for_prompt,
    get_memory_context_hint, should_store_long_term, store_long_term,
    get_long_term,
)

try:
    from openai import OpenAI
    _openai_available = True
except ImportError:
    _openai_available = False

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"


@asynccontextmanager
async def lifespan(app):
    load_faq()
    yield


app = FastAPI(
    title="Epic Vendor Services FAQ Support Copilot",
    version="1.0.0",
    description="A support chatbot grounded in Epic Vendor Services FAQ data",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[str] = None


class SourceInfo(BaseModel):
    title: str
    url: str
    faq_id: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceInfo]
    memory_used: bool
    memory_hint: Optional[str] = None
    session_id: str


def _get_openai_client() -> Optional["OpenAI"]:
    if not _openai_available:
        return None
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)


SYSTEM_PROMPT = """You are the Epic Vendor Services Support Copilot. Your role is to help users with questions about Epic Vendor Services.

RULES:
1. ONLY answer based on the FAQ entries provided below. Never invent information.
2. If the FAQ entries don't contain enough information, say so and ask for clarification.
3. For authentication issues (password reset, login problems, account lockout), ALWAYS direct users to their organization administrator or Epic support. NEVER generate fake steps.
4. Always cite your sources using the FAQ title and URL.
5. If the question is ambiguous, ask the user to clarify.
6. Be professional, concise, and helpful.
7. If conversation history is provided, use it for context but still ground answers in FAQ data."""


def _build_prompt(query: str, faq_entries: list[dict], history: str, long_term: list[dict]) -> str:
    parts = [SYSTEM_PROMPT, ""]

    if long_term:
        parts.append("STORED USER INFORMATION:")
        for item in long_term[-3:]:
            parts.append(f"- {item['content']}")
        parts.append("")

    if history:
        parts.append("CONVERSATION HISTORY:")
        parts.append(history)
        parts.append("")

    if faq_entries:
        parts.append("RELEVANT FAQ ENTRIES:")
        for entry in faq_entries:
            parts.append(f"[{entry['id']}] Category: {entry['category']}")
            parts.append(f"Q: {entry['question']}")
            parts.append(f"A: {entry['answer']}")
            parts.append(f"Source: {entry['source_title']} - {entry['source_url']}")
            parts.append("")
    else:
        parts.append("NO RELEVANT FAQ ENTRIES FOUND.")
        parts.append("")

    parts.append(f"USER QUESTION: {query}")
    parts.append("")
    parts.append("Respond helpfully based ONLY on the FAQ entries above. Cite sources.")

    return "\n".join(parts)


def _generate_with_openai(prompt: str, query: str) -> str:
    client = _get_openai_client()
    if not client:
        return ""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": query},
            ],
            temperature=0.3,
            max_tokens=500,
        )
        return response.choices[0].message.content or ""
    except Exception:
        return ""


def _generate_fallback(query: str, faq_entries: list[dict], history: str) -> str:
    """Template-based fallback when no LLM is available."""
    if not faq_entries:
        return "I don't have enough information to answer that question. Could you rephrase or provide more details?"

    auth_keywords = {"password", "login", "log", "locked", "reset", "forgot", "can't", "cant", "access", "mfa", "sso"}
    query_lower = set(query.lower().split())

    if query_lower & auth_keywords:
        auth_entries = [e for e in faq_entries if e["category"] == "authentication"]
        if auth_entries:
            entry = auth_entries[0]
            return (
                f"{entry['answer']}\n\n"
                f"Please contact your organization administrator or Epic support for further assistance.\n\n"
                f"Source: {entry['source_title']}\n{entry['source_url']}"
            )

    best = faq_entries[0]
    answer = best["answer"]

    sources_text = "\n".join(
        f"- {e['source_title']}: {e['source_url']}" for e in faq_entries[:2]
    )

    if history:
        return f"Based on our conversation, here's what I found:\n\n{answer}\n\nSources:\n{sources_text}"

    return f"{answer}\n\nSources:\n{sources_text}"


@app.get("/health")
async def health():
    return {"status": "ok", "service": "Epic Vendor Services FAQ Copilot"}


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    message = req.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Please enter a question.")

    session_id = req.session_id or str(uuid.uuid4())
    memory_used = has_history(session_id)

    history = format_history_for_prompt(session_id) if memory_used else ""
    long_term = get_long_term(session_id)

    faq_entries = retrieve(message, top_k=3)

    prompt = _build_prompt(message, faq_entries, history, long_term)
    answer = _generate_with_openai(prompt, message)

    if not answer:
        answer = _generate_fallback(message, faq_entries, history)

    sources = [
        SourceInfo(title=e["source_title"], url=e["source_url"], faq_id=e["id"])
        for e in faq_entries[:3]
    ]

    memory_hint = get_memory_context_hint(session_id) if memory_used else None

    add_message(session_id, "user", message)
    add_message(session_id, "assistant", answer)

    if should_store_long_term(message):
        store_long_term(session_id, message)

    return ChatResponse(
        answer=answer,
        sources=sources,
        memory_used=memory_used,
        memory_hint=memory_hint,
        session_id=session_id,
    )


app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
