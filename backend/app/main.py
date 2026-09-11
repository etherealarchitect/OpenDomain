import logging
from contextlib import asynccontextmanager

from backend.app.api.routes import (
    agent,
    api_keys,
    auth,
    billing,
    bulk,
    contacts,
    dns,
    domains,
    email_forwards,
    marketplace,
    monitoring,
    ssl,
    webhooks,
    whois,
)
from backend.app.core.config import settings
from backend.app.core.database import engine
from backend.app.core.rate_limit import RateLimitUnavailableError, rate_limiter
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.validate_production()
    yield
    await rate_limiter.close()
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Open-source domain registrar platform",
    lifespan=lifespan,
)

cors_origins = settings.cors_origins
if settings.debug and "*" in cors_origins:
    raise RuntimeError("CORS wildcard cannot be used with credentialed requests")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


app.include_router(auth.router, prefix="/api/v1")
app.include_router(domains.router, prefix="/api/v1")
app.include_router(dns.router, prefix="/api/v1")
app.include_router(contacts.router, prefix="/api/v1")
app.include_router(agent.router, prefix="/api/v1")
app.include_router(whois.router, prefix="/api/v1")
app.include_router(monitoring.router, prefix="/api/v1")
app.include_router(webhooks.router, prefix="/api/v1")
app.include_router(marketplace.router, prefix="/api/v1")
app.include_router(email_forwards.router, prefix="/api/v1")
app.include_router(ssl.router, prefix="/api/v1")
app.include_router(bulk.router, prefix="/api/v1")
app.include_router(billing.router, prefix="/api/v1")
app.include_router(api_keys.router, prefix="/api/v1")


@app.get("/api/health")
async def health():
    """Liveness probe: the application process can serve requests."""
    return {"status": "ok", "service": settings.app_name}


@app.get("/api/ready")
async def readiness():
    """Readiness probe: dependencies required for authenticated traffic are live."""
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        await rate_limiter.ping()
    except RateLimitUnavailableError as exc:
        logger.warning("Readiness failed because Redis is unavailable")
        return JSONResponse(status_code=503, content={"status": "unavailable", "detail": str(exc)})
    except Exception:
        logger.exception("Readiness check failed")
        return JSONResponse(
            status_code=503,
            content={"status": "unavailable", "detail": "A required dependency is unavailable"},
        )
    return {"status": "ok", "service": settings.app_name}
