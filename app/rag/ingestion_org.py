import os
from pathlib import Path
from typing import List, Dict, Any
from app.rag.chunking import chunk_organization_document
from app.rag.embeddings_provider import get_embedding_provider
from app.rag.chroma import get_organization_collection
from app.rag.ingestion import ingest_products
from app.core.config import settings
from app.core.logging import logger


ORG_DATA_DIR = "data/organization"


def load_organization_files() -> List[Dict[str, Any]]:
    org_dir = Path(ORG_DATA_DIR)
    
    if not org_dir.exists():
        logger.warning(f"Organization directory not found: {ORG_DATA_DIR}")
        return []
    
    files = list(org_dir.glob("*.md")) + list(org_dir.glob("*.txt")) + list(org_dir.glob("*.json"))
    logger.info(f"Found {len(files)} organization files")
    
    documents = []
    for file_path in files:
        try:
            content = file_path.read_text(encoding="utf-8")
            if content.strip():
                documents.append({
                    "filename": file_path.name,
                    "content": content
                })
                logger.info(f"Loaded: {file_path.name} ({len(content)} chars)")
        except Exception as e:
            logger.error(f"Failed to load {file_path.name}: {e}")
    
    return documents


def ingest_organization():
    documents = load_organization_files()
    
    if not documents:
        logger.warning("No organization documents to ingest")
        return {"success": 0, "failed": 0}
    
    all_chunks = []
    for doc in documents:
        chunks = chunk_organization_document(doc["content"], doc["filename"])
        all_chunks.extend(chunks)
    
    logger.info(f"Created {len(all_chunks)} chunks from {len(documents)} organization files")
    
    if not all_chunks:
        logger.warning("No chunks to embed")
        return {"success": 0, "failed": 0}
    
    embedding_provider = get_embedding_provider()
    texts = [chunk["content"] for chunk in all_chunks]
    
    logger.info("Generating embeddings...")
    embeddings = embedding_provider.embed_documents(texts)
    
    org_collection = get_organization_collection()
    
    ids = [chunk["id"] for chunk in all_chunks]
    metadatas = [chunk["metadata"] for chunk in all_chunks]
    documents_content = [chunk["content"] for chunk in all_chunks]
    
    existing = org_collection.get(ids=ids)
    existing_ids = set(existing.get("ids", [])) if existing else set()
    
    new_chunks = []
    for i, chunk_id in enumerate(ids):
        if chunk_id not in existing_ids:
            new_chunks.append({
                "id": chunk_id,
                "document": documents_content[i],
                "metadata": metadatas[i],
                "embedding": embeddings[i]
            })
    
    if new_chunks:
        logger.info(f"Inserting {len(new_chunks)} new organization chunks...")
        org_collection.add(
            ids=[c["id"] for c in new_chunks],
            documents=[c["document"] for c in new_chunks],
            metadatas=[c["metadata"] for c in new_chunks],
            embeddings=[c["embedding"] for c in new_chunks]
        )
        logger.info(f"Successfully inserted {len(new_chunks)} organization chunks")
    else:
        logger.info("All organization chunks already exist in database, skipping insertion")
    
    return {"success": len(new_chunks), "failed": 0, "total_files": len(documents)}


def ingest_all():
    product_result = ingest_products()
    org_result = ingest_organization()
    
    return {
        "products": product_result,
        "organization": org_result
    }