import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.retriever import load_faq, retrieve, get_faq_data, _tokenize, _keyword_score


class TestFAQLoading:
    def test_load_faq_returns_list(self):
        data = load_faq()
        assert isinstance(data, list)

    def test_faq_has_minimum_entries(self):
        data = load_faq()
        assert len(data) >= 12, f"Expected at least 12 FAQ entries, got {len(data)}"

    def test_faq_entries_have_required_fields(self):
        data = load_faq()
        required = {"id", "category", "question", "answer", "source_title", "source_url"}
        for entry in data:
            missing = required - set(entry.keys())
            assert not missing, f"Entry {entry.get('id', '?')} missing fields: {missing}"

    def test_faq_has_auth_majority(self):
        data = load_faq()
        auth_count = sum(1 for e in data if e["category"] == "authentication")
        assert auth_count / len(data) >= 0.4, "At least 40% of entries should be authentication"

    def test_faq_has_multiple_categories(self):
        data = load_faq()
        categories = set(e["category"] for e in data)
        assert len(categories) >= 3, f"Expected at least 3 categories, got {categories}"


class TestRetrieval:
    def test_password_query_returns_auth(self):
        results = retrieve("I forgot my password")
        assert len(results) > 0
        assert results[0]["category"] == "authentication"

    def test_login_query_returns_auth(self):
        results = retrieve("I can't log in")
        assert len(results) > 0
        assert results[0]["category"] == "authentication"

    def test_invoice_query_returns_billing(self):
        results = retrieve("How do I view my invoices?")
        assert len(results) > 0
        assert results[0]["category"] == "billing"

    def test_report_query_returns_reporting(self):
        results = retrieve("How do I generate a usage report?")
        assert len(results) > 0
        assert results[0]["category"] == "reporting"

    def test_empty_query_returns_empty(self):
        assert retrieve("") == []
        assert retrieve("   ") == []

    def test_top_k_limits_results(self):
        results = retrieve("help support", top_k=2)
        assert len(results) <= 2

    def test_results_contain_sources(self):
        results = retrieve("password reset")
        for r in results:
            assert r["source_title"]
            assert r["source_url"]

    def test_auth_boosting(self):
        results = retrieve("reset password")
        assert results[0]["category"] == "authentication"
        assert "auth" in results[0]["id"]


class TestTokenization:
    def test_basic_tokenization(self):
        tokens = _tokenize("Hello World!")
        assert tokens == {"hello", "world"}

    def test_empty_string(self):
        assert _tokenize("") == set()
