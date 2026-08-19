#!/usr/bin/env python
"""
Combined ingestion script for QICDOCK RAG Chatbot.
Runs both product and organization ingestion.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.rag.ingestion_org import ingest_all
from app.core.logging import logger


def main():
    print("=" * 60)
    print("QICDOCK Complete Knowledge Base Ingestion")
    print("=" * 60)
    
    try:
        result = ingest_all()
        
        print("\n" + "=" * 60)
        print("INGESTION SUMMARY")
        print("=" * 60)
        
        prod = result.get('products', {})
        org = result.get('organization', {})
        
        print(f"\nPRODUCTS:")
        print(f"  Products processed: {prod.get('total_products', 0)}")
        print(f"  Chunks inserted: {prod.get('success', 0)}")
        print(f"  Failed: {prod.get('failed', 0)}")
        
        print(f"\nORGANIZATION:")
        print(f"  Files processed: {org.get('total_files', 0)}")
        print(f"  Chunks inserted: {org.get('success', 0)}")
        print(f"  Failed: {org.get('failed', 0)}")
        
        total_chunks = prod.get('success', 0) + org.get('success', 0)
        if total_chunks > 0:
            print(f"\nSUCCESS: Total {total_chunks} chunks ingested into ChromaDB")
        else:
            print(f"\nINFO: No new chunks to insert (already exist)")
            
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        print(f"\nERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()