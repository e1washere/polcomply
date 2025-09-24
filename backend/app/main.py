"""
Main FastAPI application entry point

Licensed under the Business Source License 1.1 (BSL).
See LICENSE file for full terms.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.middleware.sessions import SessionMiddleware
import logging
from pathlib import Path

from app.config import settings
from app.database import engine, Base
from app.routers import auth, invoices, vat, ai, companies, validate, lead
from app.utils.logging import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="PolComply API",
    description="""
    **Бесплатная проверка XML по FA-3** 🎯
    
    Проверьте соответствие ваших фактур требованиям польского электронного документооборота FA-3.
    
    ## Основные возможности:
    - ✅ **Бесплатная валидация XML** по схеме FA-3
    - 🔍 **Детальная проверка** всех полей и форматов
    - 📊 **Отчет об ошибках** с указанием строк и столбцов
    - 🚀 **Быстрая интеграция** через REST API
    
    ## Для бизнеса:
    - Интеграция с KSeF (Krajowy System e-Faktur)
    - Автоматизация налоговой отчетности
    - Соответствие требованиям польского законодательства
    
    *Начните с бесплатной проверки ваших XML файлов!*
    """,
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
app.include_router(validate.router)  # Free FA-3 validation (no prefix for easy access)
app.include_router(auth.router, prefix="/v1/auth", tags=["Authentication"])
app.include_router(companies.router, prefix="/v1/companies", tags=["Companies"])
app.include_router(invoices.router, prefix="/v1/invoices", tags=["Invoices"])
app.include_router(vat.router, prefix="/v1/vat", tags=["VAT"])
app.include_router(ai.router, prefix="/v1/ai", tags=["AI Assistant"])
app.include_router(lead.router)


# Resolve absolute static directory (backend/static)
BASE_DIR = Path(__file__).resolve().parent.parent  # backend
STATIC_DIR = BASE_DIR / "static"  # backend/static


# Upload page (root endpoint)
@app.get("/")
async def upload_page():
    """Serve the XML upload page"""
    upload_file = STATIC_DIR / "upload.html"
    return FileResponse(str(upload_file))


# API info endpoint
@app.get("/api")
async def api_info():
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


# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


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
