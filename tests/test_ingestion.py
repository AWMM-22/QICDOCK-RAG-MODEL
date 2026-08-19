import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.rag.ingestion import load_product_excel, prepare_product_documents, create_product_semantic_text
from app.rag.ingestion_org import load_organization_files
import pandas as pd


def test_load_product_excel():
    df = load_product_excel("data/qicdock_products_catalog.xlsx")
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
    assert "source_id" in df.columns
    assert "product_name" in df.columns


def test_prepare_product_documents():
    df = load_product_excel("data/qicdock_products_catalog.xlsx")
    docs = prepare_product_documents(df)
    assert len(docs) > 0
    assert all("semantic_text" in doc for doc in docs)
    assert all("source_id" in doc for doc in docs)


def test_create_product_semantic_text():
    df = load_product_excel("data/qicdock_products_catalog.xlsx")
    row = df.iloc[0]
    text = create_product_semantic_text(row)
    assert "Product Name:" in text
    assert "Category:" in text
    assert "Price:" in text
    assert "₹" in text


def test_load_organization_files():
    docs = load_organization_files()
    assert len(docs) > 0
    assert all("filename" in doc for doc in docs)
    assert all("content" in doc for doc in docs)
    assert all(len(doc["content"]) > 0 for doc in docs)