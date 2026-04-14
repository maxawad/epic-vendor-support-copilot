import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.memory import (
    add_message, get_history, has_history, clear_session,
    format_history_for_prompt, get_memory_context_hint,
    should_store_long_term, MAX_HISTORY,
)


class TestShortTermMemory:
    def setup_method(self):
        clear_session("test-session")

    def test_add_and_retrieve_message(self):
        add_message("test-session", "user", "Hello")
        history = get_history("test-session")
        assert len(history) == 1
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "Hello"

    def test_has_history(self):
        assert has_history("test-session") is False
        add_message("test-session", "user", "Hello")
        assert has_history("test-session") is True

    def test_multiple_messages(self):
        add_message("test-session", "user", "Q1")
        add_message("test-session", "assistant", "A1")
        add_message("test-session", "user", "Q2")
        history = get_history("test-session")
        assert len(history) == 3

    def test_session_isolation(self):
        add_message("session-a", "user", "Hello A")
        add_message("session-b", "user", "Hello B")
        assert len(get_history("session-a")) == 1
        assert len(get_history("session-b")) == 1
        assert get_history("session-a")[0]["content"] == "Hello A"
        clear_session("session-a")
        clear_session("session-b")

    def test_clear_session(self):
        add_message("test-session", "user", "Hello")
        clear_session("test-session")
        assert has_history("test-session") is False

    def test_max_history_limit(self):
        for i in range(MAX_HISTORY + 10):
            add_message("test-session", "user", f"Message {i}")
        history = get_history("test-session")
        assert len(history) == MAX_HISTORY

    def test_format_history(self):
        add_message("test-session", "user", "What is this?")
        add_message("test-session", "assistant", "This is a FAQ bot.")
        formatted = format_history_for_prompt("test-session")
        assert "User: What is this?" in formatted
        assert "Assistant: This is a FAQ bot." in formatted

    def test_empty_history_format(self):
        assert format_history_for_prompt("nonexistent") == ""


class TestMemoryHint:
    def setup_method(self):
        clear_session("hint-test")

    def test_no_hint_without_history(self):
        assert get_memory_context_hint("hint-test") is None

    def test_hint_with_history(self):
        add_message("hint-test", "user", "How do I reset my password?")
        hint = get_memory_context_hint("hint-test")
        assert hint is not None
        assert "reset my password" in hint


class TestLongTermMemory:
    def test_should_store_admin_info(self):
        assert should_store_long_term("My admin is John Smith") is True

    def test_should_store_org_info(self):
        assert should_store_long_term("My organization is Acme Corp") is True

    def test_should_not_store_question(self):
        assert should_store_long_term("How do I reset my password?") is False

    def test_should_not_store_generic(self):
        assert should_store_long_term("Thanks for your help!") is False
