import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.rag.retriever import get_retriever
from app.rag.chunking import chunk_text


def test_chunk_text():
    text = "This is a test sentence. " * 50
    chunks = chunk_text(text, chunk_size=100, chunk_overlap=20)
    assert len(chunks) > 1
    assert all(len(c.split()) <= 100 for c in chunks)


def test_retriever_initialization():
    retriever = get_retriever()
    assert retriever is not None
    assert retriever.product_collection is not None
    assert retriever.organization_collection is not None


@pytest.mark.skipif(
    not os.path.exists("chroma_db"),
    reason="ChromaDB not initialized"
)
def test_product_retrieval():
    retriever = get_retriever()
    results = retriever.retrieve_products("wireless charger for Toyota Glanza", top_k=3)
    assert isinstance(results, list)


@pytest.mark.skipif(
    not os.path.exists("chroma_db"),
    reason="ChromaDB not initialized"
)
def test_organization_retrieval():
    retriever = get_retriever()
    results = retriever.retrieve_organization("return policy", top_k=3)
    assert isinstance(results, list)