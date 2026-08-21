import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.core.logging import logger


class ChromaClient:
    _instance = None
    _client = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            self._client = chromadb.PersistentClient(
                path=settings.chroma_path,
                settings=ChromaSettings(anonymized_telemetry=False)
            )
            logger.info(f"Initialized ChromaDB client at: {settings.chroma_path}")
    
    @property
    def client(self):
        return self._client
    
    def get_or_create_collection(self, name: str):
        try:
            return self._client.get_or_create_collection(name=name)
        except KeyError as e:
            if "'_type'" in str(e):
                logger.warning(f"Corrupted collection metadata for '{name}', deleting and recreating...")
                try:
                    self._client.delete_collection(name=name)
                except Exception:
                    pass
                return self._client.get_or_create_collection(name=name)
            raise
    
    def get_collection(self, name: str):
        try:
            return self._client.get_collection(name=name)
        except KeyError as e:
            if "'_type'" in str(e):
                logger.warning(f"Corrupted collection metadata for '{name}', deleting and recreating...")
                try:
                    self._client.delete_collection(name=name)
                except Exception:
                    pass
                return self._client.get_or_create_collection(name=name)
            raise
    
    def list_collections(self):
        return self._client.list_collections()


def get_chroma_client() -> ChromaClient:
    return ChromaClient()


class ProductCollection:
    def __init__(self):
        self.client = get_chroma_client()
        self.collection = self.client.get_or_create_collection(settings.product_collection)
    
    def add(self, ids: List[str], documents: List[str], metadatas: List[Dict[str, Any]], embeddings: List[List[float]] = None):
        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings
        )
    
    def query(self, query_embeddings: List[List[float]], n_results: int = 5, where: Dict[str, Any] = None):
        return self.collection.query(
            query_embeddings=query_embeddings,
            n_results=n_results,
            where=where
        )
    
    def get(self, ids: List[str] = None, where: Dict[str, Any] = None):
        return self.collection.get(ids=ids, where=where)
    
    def count(self):
        return self.collection.count()
    
    def delete(self, ids: List[str] = None, where: Dict[str, Any] = None):
        self.collection.delete(ids=ids, where=where)


class OrganizationCollection:
    def __init__(self):
        self.client = get_chroma_client()
        self.collection = self.client.get_or_create_collection(settings.organization_collection)
    
    def add(self, ids: List[str], documents: List[str], metadatas: List[Dict[str, Any]], embeddings: List[List[float]] = None):
        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings
        )
    
    def query(self, query_embeddings: List[List[float]], n_results: int = 5, where: Dict[str, Any] = None):
        return self.collection.query(
            query_embeddings=query_embeddings,
            n_results=n_results,
            where=where
        )
    
    def get(self, ids: List[str] = None, where: Dict[str, Any] = None):
        return self.collection.get(ids=ids, where=where)
    
    def count(self):
        return self.collection.count()
    
    def delete(self, ids: List[str] = None, where: Dict[str, Any] = None):
        self.collection.delete(ids=ids, where=where)


def get_product_collection() -> ProductCollection:
    return ProductCollection()


def get_organization_collection() -> OrganizationCollection:
    return OrganizationCollection()