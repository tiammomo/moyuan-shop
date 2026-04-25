from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import assets, generation_tasks, health, settings as settings_routes
from app.core.config import get_settings
from app.services.storage import storage_service

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    storage_service.ensure_directories()
    yield


app = FastAPI(
    title="Moyuan Shop API",
    version=settings.app_version,
    description="FastAPI MVP backend for ecommerce image-generation workflows. Uses a mock image provider by default.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix=settings.api_prefix)
app.include_router(assets.router, prefix=settings.api_prefix)
app.include_router(generation_tasks.router, prefix=settings.api_prefix)
app.include_router(settings_routes.router, prefix=settings.api_prefix)

