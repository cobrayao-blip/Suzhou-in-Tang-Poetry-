from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import meta, poems, search

# 加载项目根 .env
_root_env = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(_root_env)

app = FastAPI(
    title="全唐诗检索 API",
    description="Phase 1 + Meilisearch + PostgreSQL",
    version="0.1.0",
)

origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router, prefix="/api")
app.include_router(poems.router, prefix="/api")
app.include_router(meta.router, prefix="/api")


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}
