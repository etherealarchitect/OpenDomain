from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.routes import agent, auth, contacts, dns, domains
from backend.app.core.config import settings
from backend.app.core.database import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Open-source domain registrar platform",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(domains.router, prefix="/api/v1")
app.include_router(dns.router, prefix="/api/v1")
app.include_router(contacts.router, prefix="/api/v1")
app.include_router(agent.router, prefix="/api/v1")


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": settings.app_name}
