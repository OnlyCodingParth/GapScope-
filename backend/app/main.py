from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.content import router as content_router
from app.api.attempts import router as attempts_router
from app.api.auth import router as auth_router
from app.api.ai import router as ai_router
from app.core.config import get_settings
from app.core.database import initialize_database

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    yield


app = FastAPI(title="GapScope API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.frontend_origin,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Accept"],
)
app.include_router(health_router, prefix="/api")
app.include_router(content_router, prefix="/api")
app.include_router(attempts_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(ai_router, prefix="/api")
