import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import timedelta

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import delete, text

from . import models  # noqa: F401  (register tables)
from .config import settings
from .database import Base, SessionLocal, engine
from .models import ProfilerSession
from .routers import auth, matches, me, payments, profiler, stories
from .utils import utcnow

log = logging.getLogger("kutana")


async def purge_stale_sessions():
    """Abandoned profiling chats are deleted (data minimisation)."""
    while True:
        try:
            async with SessionLocal() as db:
                cutoff = utcnow() - timedelta(hours=settings.session_ttl_hours)
                await db.execute(delete(ProfilerSession).where(ProfilerSession.created_at < cutoff))
                await db.commit()
        except Exception:
            log.exception("purge failed")
        await asyncio.sleep(3600)


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)   # use Alembic migrations in production
    task = asyncio.create_task(purge_stale_sessions())
    yield
    task.cancel()
    await engine.dispose()


app = FastAPI(title="Kutana AI API", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])

for r in (auth.router, profiler.router, matches.router, stories.router, me.router, payments.router):
    app.include_router(r, prefix="/api")


@app.get("/health")
async def health():
    return {"status": "ok"}
