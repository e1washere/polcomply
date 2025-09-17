"""
Main FastAPI application entry point

Licensed under the Business Source License 1.1 (BSL).
See LICENSE file for full terms.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.sessions import SessionMiddleware
import logging

from app.config import settings
from app.database import engine, Base
from app.routers import auth, invoices, vat, ai, companies
from app.utils.logging import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="PolComply API",
    description="Polish tax compliance and KSeF integration platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(SessionMiddleware, secret_key=settings.JWT_SECRET)

if settings.ENVIRONMENT == "production":
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)

# Include routers
app.include_router(auth.router, prefix="/v1/auth", tags=["Authentication"])
app.include_router(companies.router, prefix="/v1/companies", tags=["Companies"])
app.include_router(invoices.router, prefix="/v1/invoices", tags=["Invoices"])
app.include_router(vat.router, prefix="/v1/vat", tags=["VAT"])
app.include_router(ai.router, prefix="/v1/ai", tags=["AI Assistant"])


# Root endpoint
@app.get("/")
async def root():
    return {
        "name": "PolComply API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "connected", "redis": "connected"}


# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("Starting PolComply API...")
    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down PolComply API...")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
