#!/usr/bin/env python
"""
Organization knowledge ingestion script for QICDOCK RAG Chatbot.
Loads markdown files from data/organization/ and ingests into ChromaDB.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.rag.ingestion_org import ingest_organization
from app.core.logging import logger


def main():
    print("=" * 60)
    print("QICDOCK Organization Knowledge Ingestion")
    print("=" * 60)
    
    org_dir = "data/organization"
    
    if not os.path.exists(org_dir):
        print(f"ERROR: Directory not found: {org_dir}")
        sys.exit(1)
    
    print(f"Loading organization files from: {org_dir}")
    
    try:
        result = ingest_organization()
        
        print(f"\nIngestion Complete!")
        print(f"  Files processed: {result.get('total_files', 0)}")
        print(f"  Chunks inserted: {result.get('success', 0)}")
        print(f"  Failed: {result.get('failed', 0)}")
        
        if result.get('success', 0) > 0:
            print("\nSUCCESS: Organization knowledge ingested into ChromaDB")
        else:
            print("\nINFO: No new chunks to insert (already exist)")
            
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        print(f"\nERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()