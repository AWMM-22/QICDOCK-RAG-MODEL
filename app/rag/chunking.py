from typing import List
from app.core.config import settings
from app.core.logging import logger


def chunk_text(text: str, chunk_size: int = None, chunk_overlap: int = None) -> List[str]:
    if not text or not text.strip():
        return []
    
    chunk_size = chunk_size or settings.chunk_size
    chunk_overlap = chunk_overlap or settings.chunk_overlap
    
    words = text.split()
    if len(words) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        
        if end >= len(words):
            break
        
        start = end - chunk_overlap
    
    logger.debug(f"Created {len(chunks)} chunks from text of {len(words)} words")
    return chunks


def chunk_organization_document(content: str, filename: str) -> List[dict]:
    chunks = chunk_text(content)
    result = []
    
    for i, chunk in enumerate(chunks):
        result.append({
            "id": f"org_{filename}_{i}",
            "content": chunk,
            "metadata": {
                "type": "organization",
                "source": "organization",
                "filename": filename,
                "chunk_index": i,
                "total_chunks": len(chunks)
            }
        })
    
    return result


def chunk_product_document(product_doc: dict) -> List[dict]:
    product_id = product_doc.get("source_id", "unknown")
    content = product_doc.get("semantic_text", "")
    
    if not content:
        return []
    
    chunks = chunk_text(content)
    result = []
    
    for i, chunk in enumerate(chunks):
        result.append({
            "id": f"product_{product_id}_{i}" if len(chunks) > 1 else f"product_{product_id}",
            "content": chunk,
            "metadata": {
                "type": "product",
                "source": "excel",
                "product_id": product_id,
                "product_name": product_doc.get("product_name", ""),
                "category": product_doc.get("category", ""),
                "brand": product_doc.get("brand", ""),
                "vehicle_make": product_doc.get("vehicle_make", ""),
                "vehicle_model": product_doc.get("vehicle_model", ""),
                "price_inr": product_doc.get("price_inr"),
                "sku": product_doc.get("sku", ""),
                "chunk_index": i,
                "total_chunks": len(chunks)
            }
        })
    
    return result