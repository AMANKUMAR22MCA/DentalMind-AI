from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from app.routes.chat import router as chat_router
from app.core.config import get_settings
from app.routes.ask import router as ask_router,embeddings
from app.routes.upload import router as upload_router
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Runs during application startup and shutdown.
    Similar to Django startup initialization.
    """

    # Startup logic
    print(f"{settings.APP_NAME} starting...")
    print("Loading embedding model...")
    embeddings.embed_query("warmup")
    print("Embedding model ready!")

    yield

    # Shutdown logic
    print(f"{settings.APP_NAME} shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,  # hide swagger in prod
    redoc_url="/redoc" if settings.DEBUG else None,
)


app.include_router(
    ask_router,
    prefix="/api/v1",
    tags=["Ask"]
)
app.include_router(
    upload_router,
    prefix="/api/v1",
    tags=["Upload"]
)

@app.get("/health")
async def health() -> dict[str, str]:
    return {
        "status": "ok",
        "app": settings.APP_NAME,
    }

app.include_router(
    chat_router,
    prefix="/api/v1",
    tags=["Chat"]
)