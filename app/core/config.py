from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    app_env: str = "development"
    
    groq_api_key: str = ""
    groq_model: str = "llama-3.1-8b-instant"
    
    embedding_provider: str = "sentence-transformers"
    embedding_model: str = "all-MiniLM-L6-v2"
    
    chroma_path: str = "./chroma_db"
    product_collection: str = "products"
    organization_collection: str = "organization"
    
    top_k: int = 5
    relevance_threshold: float = 1.5
    
    chunk_size: int = 700
    chunk_overlap: int = 100
    
    max_history_messages: int = 10
    
    cors_origins: List[str] = ["*"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()