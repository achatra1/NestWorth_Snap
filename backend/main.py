import logging

# Configured before any backend.* imports so module-load-time logging
# (e.g. the data loaders in backend/data/) isn't silently dropped by
# Python's default "no handler configured" behavior.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

import time
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
from backend.config import settings
from backend.database import connect_to_mongo, close_mongo_connection, ping_database
from backend.routers import auth, profiles, projections, summaries, exports

app = FastAPI(
    title="NestWorth API",
    description="Backend API for NestWorth baby budget calculator",
    version="1.0.0"
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log every request with method, path, status code, and duration."""
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    log = logger.error if response.status_code >= 500 else logger.info
    log(f"{request.method} {request.url.path} -> {response.status_code} ({duration_ms:.1f}ms)")
    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Custom handler for validation errors to provide better error messages."""
    logger.warning(f"Validation error on {request.method} {request.url}: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Catch-all handler so unexpected errors are logged with a traceback instead of silently 500ing."""
    logger.exception(f"Unhandled exception on {request.method} {request.url}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(profiles.router)
app.include_router(projections.router)
app.include_router(summaries.router)
app.include_router(exports.router)


@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup."""
    logger.info("Starting NestWorth API")
    await connect_to_mongo()


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown."""
    logger.info("Shutting down NestWorth API")
    await close_mongo_connection()


@app.get("/")
async def root():
    """Root endpoint - database cleared and ready for fresh start"""
    return {"message": "NestWorth API", "version": "1.0.0"}


@app.get("/healthz")
async def health_check():
    """Health check endpoint that verifies database connectivity."""
    db_connected = await ping_database()
    
    return {
        "status": "ok",
        "database": "connected" if db_connected else "disconnected",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }