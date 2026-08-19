#!/usr/bin/env python
"""
Product ingestion script for QICDOCK RAG Chatbot.
Loads product catalog from Excel and ingests into ChromaDB.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.rag.ingestion import ingest_products
from app.core.logging import logger


def main():
    print("=" * 60)
    print("QICDOCK Product Ingestion")
    print("=" * 60)
    
    filepath = "data/qicdock_products_catalog.xlsx"
    
    if not os.path.exists(filepath):
        print(f"ERROR: File not found: {filepath}")
        sys.exit(1)
    
    print(f"Loading Excel file: {filepath}")
    
    try:
        result = ingest_products(filepath)
        
        print(f"\nIngestion Complete!")
        print(f"  Products processed: {result.get('total_products', 0)}")
        print(f"  Chunks inserted: {result.get('success', 0)}")
        print(f"  Failed: {result.get('failed', 0)}")
        
        if result.get('success', 0) > 0:
            print("\nSUCCESS: Products ingested into ChromaDB")
        else:
            print("\nINFO: No new products to insert (already exist)")
            
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        print(f"\nERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()