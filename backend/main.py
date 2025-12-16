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

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Custom handler for validation errors to provide better error messages."""
    print(f"Validation error on {request.method} {request.url}")
    print(f"Error details: {exc.errors()}")
    print(f"Request body: {exc.body}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body},
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
    await connect_to_mongo()


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown."""
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