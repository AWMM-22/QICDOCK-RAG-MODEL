import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.rag.router import classify_intent_simple, IntentType


def test_product_intent():
    queries = [
        "What is the price of the wireless charger?",
        "Does this charger support iPhone 15?",
        "Which charger for Toyota Glanza?",
        "What products do you have?",
        "Specifications for Mahindra XUV 3XO charger",
    ]
    
    for query in queries:
        intent = classify_intent_simple(query)
        assert intent == IntentType.PRODUCT, f"Failed for: {query}"


def test_organization_intent():
    queries = [
        "What is your return policy?",
        "How long does shipping take?",
        "How can I contact support?",
        "What is your warranty?",
        "Tell me about your company",
    ]
    
    for query in queries:
        intent = classify_intent_simple(query)
        assert intent == IntentType.ORGANIZATION, f"Failed for: {query}"


def test_multi_intent():
    queries = [
        "What is the price of the charger and what is your return policy?",
        "Which charger for my car and how long is warranty?",
    ]
    
    for query in queries:
        intent = classify_intent_simple(query)
        assert intent == IntentType.MULTI, f"Failed for: {query}"


def test_out_of_scope_intent():
    queries = [
        "Who is the president of the USA?",
        "What is Python?",
        "Tell me a joke",
        "What's the weather today?",
    ]
    
    for query in queries:
        intent = classify_intent_simple(query)
        assert intent == IntentType.OUT_OF_SCOPE, f"Failed for: {query}"