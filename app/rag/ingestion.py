import pandas as pd
from typing import List, Dict, Any
import numpy as np
from app.models.documents import ProductDocument
from app.rag.chunking import chunk_product_document
from app.rag.embeddings_provider import get_embedding_provider
from app.rag.chroma import get_product_collection
from app.core.config import settings
from app.core.logging import logger


def load_product_excel(filepath: str) -> pd.DataFrame:
    logger.info(f"Loading Excel file: {filepath}")
    df = pd.read_excel(filepath)
    logger.info(f"Loaded {len(df)} rows, {len(df.columns)} columns")
    return df


def create_product_semantic_text(row: pd.Series) -> str:
    parts = []
    
    product_name = row.get("product_name", "")
    if product_name:
        parts.append(f"Product Name: {product_name}")
    
    category = row.get("category", "")
    if category:
        parts.append(f"Category: {category}")
    
    brand = row.get("brand", "")
    if brand:
        parts.append(f"Brand: {brand}")
    
    vehicle_make = row.get("vehicle_make", "")
    vehicle_model = row.get("vehicle_model", "")
    if vehicle_make or vehicle_model:
        parts.append(f"Vehicle: {vehicle_make} {vehicle_model}".strip())
    
    compatibility = row.get("compatibility", "")
    if compatibility and compatibility != "nan":
        parts.append(f"Compatibility: {compatibility}")
    
    price_inr = row.get("price_inr")
    if pd.notna(price_inr):
        parts.append(f"Price: {int(price_inr):,}")
    
    mrp_inr = row.get("mrp_inr")
    if pd.notna(mrp_inr):
        parts.append(f"MRP: {int(mrp_inr):,}")
    
    discount_percent = row.get("discount_percent")
    if pd.notna(discount_percent):
        parts.append(f"Discount: {int(discount_percent)}%")
    
    availability = row.get("availability", "")
    if availability and availability != "nan":
        parts.append(f"Availability: {availability}")
    
    sku = row.get("sku", "")
    if sku:
        parts.append(f"SKU: {sku}")
    
    description = row.get("description", "")
    if description and description != "nan":
        parts.append(f"Description: {description}")
    
    features = row.get("features", "")
    if features and features != "nan":
        parts.append(f"Features: {features}")
    
    return "\n".join(parts)


def prepare_product_documents(df: pd.DataFrame) -> List[Dict[str, Any]]:
    documents = []
    
    for _, row in df.iterrows():
        try:
            source_id = row.get("source_id", "")
            if not source_id or pd.isna(source_id):
                logger.warning("Skipping row with missing source_id")
                continue
            
            semantic_text = create_product_semantic_text(row)
            
            doc = {
                "source_id": str(source_id),
                "product_name": str(row.get("product_name", "")),
                "category": str(row.get("category", "")),
                "brand": str(row.get("brand", "")),
                "vehicle_make": str(row.get("vehicle_make", "")) if pd.notna(row.get("vehicle_make")) else "",
                "vehicle_model": str(row.get("vehicle_model", "")) if pd.notna(row.get("vehicle_model")) else "",
                "compatibility": str(row.get("compatibility", "")) if pd.notna(row.get("compatibility")) else "",
                "price_inr": int(row["price_inr"]) if pd.notna(row.get("price_inr")) else None,
                "mrp_inr": int(row["mrp_inr"]) if pd.notna(row.get("mrp_inr")) else None,
                "discount_percent": int(row["discount_percent"]) if pd.notna(row.get("discount_percent")) else None,
                "availability": str(row.get("availability", "")) if pd.notna(row.get("availability")) else "",
                "stock_quantity": int(row["stock_quantity"]) if pd.notna(row.get("stock_quantity")) else None,
                "sku": str(row.get("sku", "")) if pd.notna(row.get("sku")) else "",
                "description": str(row.get("description", "")) if pd.notna(row.get("description")) else "",
                "features": str(row.get("features", "")) if pd.notna(row.get("features")) else "",
                "product_url": str(row.get("product_url", "")) if pd.notna(row.get("product_url")) else "",
                "image_url": str(row.get("image_url", "")) if pd.notna(row.get("image_url")) else "",
                "rating": float(row["rating"]) if pd.notna(row.get("rating")) else None,
                "review_count": int(row["review_count"]) if pd.notna(row.get("review_count")) else None,
                "source_type": str(row.get("source_type", "")) if pd.notna(row.get("source_type")) else "",
                "source_reference": str(row.get("source_reference", "")) if pd.notna(row.get("source_reference")) else "",
                "semantic_text": semantic_text
            }
            documents.append(doc)
        except Exception as e:
            logger.error(f"Failed to process row {row.get('source_id', 'unknown')}: {e}")
            continue
    
    logger.info(f"Prepared {len(documents)} product documents")
    return documents


def ingest_products(filepath: str = None):
    filepath = filepath or "data/qicdock_products_catalog.xlsx"
    
    try:
        df = load_product_excel(filepath)
        product_docs = prepare_product_documents(df)
        
        if not product_docs:
            logger.warning("No valid product documents to ingest")
            return {"success": 0, "failed": 0}
        
        all_chunks = []
        for doc in product_docs:
            chunks = chunk_product_document(doc)
            all_chunks.extend(chunks)
        
        logger.info(f"Created {len(all_chunks)} chunks from {len(product_docs)} products")
        
        if not all_chunks:
            logger.warning("No chunks to embed")
            return {"success": 0, "failed": 0}
        
        embedding_provider = get_embedding_provider()
        texts = [chunk["content"] for chunk in all_chunks]
        
        logger.info("Generating embeddings...")
        embeddings = embedding_provider.embed_documents(texts)
        
        product_collection = get_product_collection()
        
        ids = [chunk["id"] for chunk in all_chunks]
        metadatas = [chunk["metadata"] for chunk in all_chunks]
        documents = [chunk["content"] for chunk in all_chunks]
        
        existing = product_collection.get(ids=ids)
        existing_ids = set(existing.get("ids", [])) if existing else set()
        
        new_chunks = []
        for i, chunk_id in enumerate(ids):
            if chunk_id not in existing_ids:
                new_chunks.append({
                    "id": chunk_id,
                    "document": documents[i],
                    "metadata": metadatas[i],
                    "embedding": embeddings[i]
                })
        
        if new_chunks:
            logger.info(f"Inserting {len(new_chunks)} new product chunks...")
            product_collection.add(
                ids=[c["id"] for c in new_chunks],
                documents=[c["document"] for c in new_chunks],
                metadatas=[c["metadata"] for c in new_chunks],
                embeddings=[c["embedding"] for c in new_chunks]
            )
            logger.info(f"Successfully inserted {len(new_chunks)} product chunks")
        else:
            logger.info("All products already exist in database, skipping insertion")
        
        return {"success": len(new_chunks), "failed": 0, "total_products": len(product_docs)}
    
    except Exception as e:
        logger.error(f"Product ingestion failed: {e}")
        raise