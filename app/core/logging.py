import logging
import sys
import os
from app.core.config import settings


def setup_logging() -> logging.Logger:
    log_level = logging.DEBUG if settings.app_env == "development" else logging.INFO
    
    logger = logging.getLogger("rag_chatbot")
    logger.setLevel(log_level)
    
    if not logger.handlers:
        # Use UTF-8 encoding for Windows console
        if sys.platform == "win32":
            import io
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
        
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(log_level)
        
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


logger = setup_logging()