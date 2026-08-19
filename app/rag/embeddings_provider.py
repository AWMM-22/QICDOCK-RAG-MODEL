from typing import List
from sentence_transformers import SentenceTransformer
from app.rag.embeddings import EmbeddingProvider
from app.core.config import settings
from app.core.logging import logger


class SentenceTransformerEmbeddingProvider(EmbeddingProvider):
    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.embedding_model
        self._model = None
        logger.info(f"Initializing SentenceTransformer with model: {self.model_name}")
    
    @property
    def model(self) -> SentenceTransformer:
        if self._model is None:
            self._model = SentenceTransformer(self.model_name)
        return self._model
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        logger.debug(f"Embedding {len(texts)} documents")
        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        return embeddings.tolist()
    
    def embed_query(self, text: str) -> List[float]:
        logger.debug(f"Embedding query: {text[:50]}...")
        embedding = self.model.encode(text, convert_to_numpy=True, show_progress_bar=False)
        return embedding.tolist()
    
    @property
    def dimension(self) -> int:
        return self.model.get_sentence_embedding_dimension()


def get_embedding_provider() -> EmbeddingProvider:
    provider_type = settings.embedding_provider.lower()
    if provider_type == "sentence-transformers":
        return SentenceTransformerEmbeddingProvider()
    else:
        raise ValueError(f"Unknown embedding provider: {provider_type}")