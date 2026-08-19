from typing import List, Optional
from app.rag.chroma import get_product_collection, get_organization_collection
from app.rag.embeddings_provider import get_embedding_provider
from app.core.config import settings
from app.core.logging import logger
from app.models.chat import RetrievedDocument


class Retriever:
    def __init__(self):
        self.embedding_provider = get_embedding_provider()
        self.product_collection = get_product_collection()
        self.organization_collection = get_organization_collection()
    
    def retrieve_products(self, query: str, top_k: int = None) -> List[RetrievedDocument]:
        top_k = top_k or settings.top_k
        
        try:
            query_embedding = self.embedding_provider.embed_query(query)
            results = self.product_collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            
            documents = []
            if results and results.get("documents"):
                for i, doc in enumerate(results["documents"][0]):
                    metadata = results["metadatas"][0][i] if results.get("metadatas") else {}
                    distance = results["distances"][0][i] if results.get("distances") else 0.0
                    
                    documents.append(RetrievedDocument(
                        content=doc,
                        metadata=metadata,
                        distance=distance
                    ))
            
            logger.info(f"Retrieved {len(documents)} product documents for query: {query[:50]}")
            return documents
        except Exception as e:
            logger.error(f"Product retrieval failed: {e}")
            return []
    
    def retrieve_organization(self, query: str, top_k: int = None) -> List[RetrievedDocument]:
        top_k = top_k or settings.top_k
        
        try:
            query_embedding = self.embedding_provider.embed_query(query)
            results = self.organization_collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            
            documents = []
            if results and results.get("documents"):
                for i, doc in enumerate(results["documents"][0]):
                    metadata = results["metadatas"][0][i] if results.get("metadatas") else {}
                    distance = results["distances"][0][i] if results.get("distances") else 0.0
                    
                    documents.append(RetrievedDocument(
                        content=doc,
                        metadata=metadata,
                        distance=distance
                    ))
            
            logger.info(f"Retrieved {len(documents)} organization documents for query: {query[:50]}")
            return documents
        except Exception as e:
            logger.error(f"Organization retrieval failed: {e}")
            return []


def get_retriever() -> Retriever:
    return Retriever()