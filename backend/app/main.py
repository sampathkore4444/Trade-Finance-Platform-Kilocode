"""
Trade Finance Platform - Main Application Entry Point

This module initializes the FastAPI application and configures all middleware,
routers, and event handlers.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import time

from app.config import settings
from app.database import engine, Base
from app.common.exceptions import (
    TradeFinanceException,
    UnauthorizedException,
    NotFoundException,
    ValidationException,
)
from app.modules.users.routers import router as users_router
from app.modules.auth.routers import router as auth_router
from app.modules.letter_of_credit.routers import router as lc_router
from app.modules.bank_guarantee.routers import router as guarantee_router
from app.modules.documentary_collection.routers import router as collection_router
from app.modules.invoice_financing.routers import router as invoice_router
from app.modules.trade_loan.routers import router as loan_router
from app.modules.risk_management.routers import router as risk_router
from app.modules.compliance.routers import router as compliance_router
from app.modules.documents.routers import router as documents_router
from app.modules.reports.routers import router as reports_router
from app.modules.notifications.routers import router as notifications_router
from app.modules.smart_engines.routers import router as smart_engines_router
from app.core.security.audit_logger import AuditLogger


async def lifespan(app: FastAPI):
    """
    Application lifespan handler for startup and shutdown events.
    """
    # Startup: Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Initialize audit logger
    audit_logger = AuditLogger()
    app.state.audit_logger = audit_logger

    yield

    # Shutdown: Close database connections
    await engine.dispose()


def create_app() -> FastAPI:
    """
    Factory function to create and configure the FastAPI application.
    """
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="""
        Enterprise-grade Trade Finance Platform for commercial banks.
        
        ## Features
        - Letter of Credit (LC) Management
        - Bank Guarantees
        - Documentary Collection
        - Invoice Financing
        - Trade Loans
        - Risk Management
        - Compliance & KYC
        
        ## Security
        - JWT Authentication with Refresh Tokens
        - Role-Based Access Control (RBAC)
        - Multi-Factor Authentication (MFA)
        - AES-256 Data Encryption
        """,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add Gzip compression
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # Add request timing middleware
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response

    # Global exception handlers
    @app.exception_handler(TradeFinanceException)
    async def trade_finance_exception_handler(
        request: Request, exc: TradeFinanceException
    ):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": exc.__class__.__name__,
                "message": exc.message,
                "details": exc.details,
            },
        )

    @app.exception_handler(UnauthorizedException)
    async def unauthorized_exception_handler(
        request: Request, exc: UnauthorizedException
    ):
        return JSONResponse(
            status_code=401,
            content={
                "success": False,
                "error": "Unauthorized",
                "message": exc.message,
            },
        )

    @app.exception_handler(NotFoundException)
    async def not_found_exception_handler(request: Request, exc: NotFoundException):
        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "error": "NotFound",
                "message": exc.message,
            },
        )

    @app.exception_handler(ValidationException)
    async def validation_exception_handler(request: Request, exc: ValidationException):
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error": "ValidationError",
                "message": exc.message,
                "details": exc.details,
            },
        )

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "version": settings.APP_VERSION,
            "timestamp": time.time(),
        }

    # Include routers
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
    app.include_router(users_router, prefix="/api/v1/users", tags=["Users"])
    app.include_router(lc_router, prefix="/api/v1/lc", tags=["Letter of Credit"])
    app.include_router(
        guarantee_router, prefix="/api/v1/guarantee", tags=["Bank Guarantee"]
    )
    app.include_router(
        collection_router, prefix="/api/v1/collection", tags=["Documentary Collection"]
    )
    app.include_router(
        invoice_router, prefix="/api/v1/invoice", tags=["Invoice Financing"]
    )
    app.include_router(loan_router, prefix="/api/v1/loan", tags=["Trade Loan"])
    app.include_router(risk_router, prefix="/api/v1/risk", tags=["Risk Management"])
    app.include_router(
        compliance_router, prefix="/api/v1/compliance", tags=["Compliance"]
    )
    app.include_router(documents_router, prefix="/api/v1/documents", tags=["Documents"])
    app.include_router(reports_router, prefix="/api/v1/reports", tags=["Reports"])
    app.include_router(
        notifications_router, prefix="/api/v1/notifications", tags=["Notifications"]
    )
    app.include_router(
        smart_engines_router, prefix="/api/v1/smart-engines", tags=["Smart Engines"]
    )

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info",
    )
