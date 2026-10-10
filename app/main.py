from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging_config import configure_logging
from app.db.session import Base, engine
from app.db import models  # noqa: F401 ensures models are registered
from app.api import chat, moderation, health, analytics, auth
from logger import get_logger
from exception import CustomException

configure_logging()
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    logger.info("TrustGuard AI started")
    yield
    logger.info("TrustGuard AI stopped")

app = FastAPI(title=settings.app_name, version="1.0.0",
              description="Customer support automation with trust and safety controls.",
              lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=[x.strip() for x in settings.cors_origins.split(",") if x.strip()],
                   allow_credentials=True, allow_methods=["GET", "POST"], allow_headers=["*"])
app.include_router(health.router, prefix=settings.api_prefix)
app.include_router(moderation.router, prefix=settings.api_prefix)
app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(chat.router, prefix=settings.api_prefix)
app.include_router(analytics.router, prefix=settings.api_prefix)

@app.exception_handler(CustomException)
async def custom_exception_handler(request: Request, exc: CustomException):
    logger.error("Handled application exception on %s: %s", request.url.path, str(exc))
    return JSONResponse(status_code=500, content={"detail": "The request could not be completed safely."})

@app.get("/")
def root():
    return {"service": settings.app_name, "docs": "/docs", "health": f"{settings.api_prefix}/health/live"}
