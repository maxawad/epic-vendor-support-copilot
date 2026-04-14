import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_ok(self, client):
        data = client.get("/health").json()
        assert data["status"] == "ok"


class TestChatEndpoint:
    def test_chat_with_valid_message(self, client):
        response = client.post("/chat", json={"message": "How do I reset my password?"})
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "sources" in data
        assert "memory_used" in data
        assert "session_id" in data

    def test_chat_returns_sources(self, client):
        response = client.post("/chat", json={"message": "How do I view my invoices?"})
        data = response.json()
        assert len(data["sources"]) > 0
        source = data["sources"][0]
        assert "title" in source
        assert "url" in source

    def test_chat_empty_message_returns_400(self, client):
        response = client.post("/chat", json={"message": ""})
        assert response.status_code == 422

    def test_chat_preserves_session_id(self, client):
        response = client.post("/chat", json={
            "message": "reset password",
            "session_id": "test-session-123"
        })
        data = response.json()
        assert data["session_id"] == "test-session-123"

    def test_chat_generates_session_id_if_missing(self, client):
        response = client.post("/chat", json={"message": "hello"})
        data = response.json()
        assert data["session_id"]

    def test_chat_memory_used_false_on_first_message(self, client):
        response = client.post("/chat", json={
            "message": "password help",
            "session_id": "fresh-session-xyz"
        })
        data = response.json()
        assert data["memory_used"] is False

    def test_chat_memory_used_true_on_followup(self, client):
        sid = "memory-test-session"
        client.post("/chat", json={"message": "password help", "session_id": sid})
        response = client.post("/chat", json={"message": "I still can't log in", "session_id": sid})
        data = response.json()
        assert data["memory_used"] is True
