from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import chat_router, health_router
from app.core.logging import logger


app = FastAPI(
    title="QICDOCK RAG Chatbot API",
    description="Retrieval-Augmented Generation chatbot for QICDOCK automotive accessories",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api")
app.include_router(health_router)


@app.on_event("startup")
async def startup_event():
    logger.info("Starting QICDOCK RAG Chatbot API")
    logger.info(f"Environment: {settings.app_env}")
    logger.info(f"ChromaDB path: {settings.chroma_path}")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down QICDOCK RAG Chatbot API")