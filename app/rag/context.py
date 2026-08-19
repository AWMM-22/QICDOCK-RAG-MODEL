from typing import List, Dict, Any
from app.models.chat import RetrievedDocument, IntentType
from app.core.config import settings
from app.core.logging import logger


def filter_relevant_documents(documents: List[RetrievedDocument], threshold: float = None) -> List[RetrievedDocument]:
    threshold = threshold or settings.relevance_threshold
    
    relevant = []
    for doc in documents:
        if doc.distance <= threshold:
            relevant.append(doc)
        else:
            logger.debug(f"Filtered out document with distance {doc.distance} > {threshold}")
    
    logger.info(f"Filtered {len(documents)} documents to {len(relevant)} relevant (threshold={threshold})")
    return relevant


def build_context(
    product_docs: List[RetrievedDocument],
    org_docs: List[RetrievedDocument],
    intent: IntentType
) -> str:
    context_parts = []
    
    if product_docs and (intent in [IntentType.PRODUCT, IntentType.MULTI]):
        context_parts.append("PRODUCT CONTEXT")
        context_parts.append("=" * 40)
        for i, doc in enumerate(product_docs, 1):
            product_name = doc.metadata.get("product_name", "Unknown Product")
            context_parts.append(f"\n[Product {i}: {product_name}]")
            context_parts.append(doc.content)
        context_parts.append("")
    
    if org_docs and (intent in [IntentType.ORGANIZATION, IntentType.MULTI]):
        context_parts.append("ORGANIZATION CONTEXT")
        context_parts.append("=" * 40)
        for i, doc in enumerate(org_docs, 1):
            filename = doc.metadata.get("filename", "Unknown Source")
            context_parts.append(f"\n[Source {i}: {filename}]")
            context_parts.append(doc.content)
        context_parts.append("")
    
    context = "\n".join(context_parts)
    
    if not context.strip():
        return "NO_RELEVANT_CONTEXT"
    
    return context


def rewrite_query_with_history(query: str, history: List[Dict[str, str]]) -> str:
    if not history:
        return query
    
    last_messages = history[-3:] if len(history) > 3 else history
    
    context = "Previous conversation:\n"
    for msg in last_messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        context += f"{role}: {content}\n"
    
    context += f"\nCurrent question: {query}\n\n"
    context += "Rewrite the current question as a standalone question that includes all necessary context from the conversation. If the question is already standalone, return it unchanged.\n\nRewritten question:"
    
    return context