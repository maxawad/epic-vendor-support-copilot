import json
import os
import re
from pathlib import Path
from typing import Optional

FAQ_PATH = Path(__file__).parent.parent / "SEED_DATA" / "epic_vendor_faq.json"

_faq_data: list[dict] = []


def load_faq(path: Optional[str] = None) -> list[dict]:
    global _faq_data
    faq_path = Path(path) if path else FAQ_PATH
    with open(faq_path, "r") as f:
        _faq_data = json.load(f)
    return _faq_data


def get_faq_data() -> list[dict]:
    if not _faq_data:
        load_faq()
    return _faq_data


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"\w+", text.lower()))


def _keyword_score(query_tokens: set[str], entry: dict) -> float:
    question_tokens = _tokenize(entry["question"])
    answer_tokens = _tokenize(entry["answer"])
    category_tokens = _tokenize(entry.get("category", ""))

    q_overlap = len(query_tokens & question_tokens)
    a_overlap = len(query_tokens & answer_tokens)
    c_overlap = len(query_tokens & category_tokens)

    return (q_overlap * 3.0) + (a_overlap * 1.0) + (c_overlap * 2.0)


AUTH_KEYWORDS = {
    "password", "login", "log", "signin", "sign", "locked", "lock",
    "unlock", "mfa", "authentication", "authenticate", "sso", "credential",
    "credentials", "username", "reset", "forgot", "can't", "cant", "unable",
    "access", "denied", "two-factor", "2fa", "otp", "verification",
}


def _boost_auth_relevance(query_tokens: set[str], entry: dict, base_score: float) -> float:
    if query_tokens & AUTH_KEYWORDS and entry["category"] == "authentication":
        return base_score + 5.0
    return base_score


def retrieve(query: str, top_k: int = 3) -> list[dict]:
    """Retrieve the top-k FAQ entries most relevant to the query using keyword scoring."""
    if not query or not query.strip():
        return []

    faq = get_faq_data()
    query_tokens = _tokenize(query)

    scored = []
    for entry in faq:
        score = _keyword_score(query_tokens, entry)
        score = _boost_auth_relevance(query_tokens, entry, score)
        if score > 0:
            scored.append((score, entry))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [entry for _, entry in scored[:top_k]]
