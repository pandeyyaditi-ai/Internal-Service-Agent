"""
Unit tests for policy/FAQ search functionality.
"""
import pytest
from app.services.policy_search import search_faqs, load_faq_data


def test_load_faq_data():
    """Verify that FAQ database loads correctly from disk."""
    data = load_faq_data()
    assert "faqs" in data
    assert len(data["faqs"]) > 0


def test_search_faqs_matching():
    """Verify search returns relevant answers with source metadata."""
    results = search_faqs("vpn connect globalprotect", top_k=3)
    assert len(results) > 0
    top_result = results[0]
    assert "faq_id" in top_result
    assert "question" in top_result
    assert "answer" in top_result
    assert "relevance_score" in top_result
    assert top_result["relevance_score"] > 0


def test_search_faqs_category_filter():
    """Verify filtering by category."""
    results = search_faqs("password reset", category="password", top_k=2)
    assert len(results) > 0
    for r in results:
        assert r["category"] == "password"
