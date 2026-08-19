import uvicorn
import os
from app.core.config import settings


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        reload=settings.app_env == "development",
        log_level="info"
    )