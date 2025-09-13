from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from backend.config import settings
from backend.config.database import create_db_and_tables
from backend.controllers import (
    auth_router,
    user_router,
    albums_router,
    images_router,
    site_router,
    collections_router,
)


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""

    app = FastAPI(
        title="Blog Backend API",
        description="A scalable blog backend built with FastAPI and SQLModel",
        version="1.0.0",
        debug=settings.debug,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_hosts,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    print("Allowed hosts:", settings.allowed_hosts)

    # Include routers
    app.include_router(auth_router)
    app.include_router(user_router)
    app.include_router(site_router)
    app.include_router(albums_router)
    app.include_router(images_router)
    app.include_router(collections_router)

    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Global exception handler caught: {exc}")
        return JSONResponse(
            status_code=500, content={"detail": "Internal server error"}
        )

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "version": "1.0.0"}

    # Root endpoint
    @app.get("/")
    async def root():
        return {"message": "Blog Backend API", "version": "1.0.0", "docs": "/docs"}

    return app


# Create application instance
app = create_app()


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info("Starting up...")
    create_db_and_tables()
    logger.info("Database tables created/verified")

    # Initialize db
    from backend.config.initial_data import create_initial_data

    create_initial_data()

    # Initialize minio
    from backend.config.minio import create_minio_client

    create_minio_client()
    logger.info("MinIO client initialized and bucket verified/created")

    # Initialize qdrant
    from backend.config.qdrant import create_qdrant_client

    create_qdrant_client()
    logger.info("Qdrant client initialized")

    # Initialize replicate client
    from backend.config.replicate import create_replicate_client
    create_replicate_client()
    logger.info("Replicate client initialized")

    # Initialize permissions and roles
    # from backend.config.database import get_session

    # Get a database session
    # session_gen = get_session()
    # session = next(session_gen)

    # try:
    #     permission_service = PermissionService(session)
    #     permission_service.ensure_initial_data()
    #     logger.info("Initial permissions and roles ensured")
    # finally:
    #     session.close()

    # Create sample data
    # from backend.config.database import create_sample_data
    # try:
    #     create_sample_data()
    #     logger.info("Sample data created")
    # except Exception as e:
    #     logger.warning(f"Sample data creation failed: {e}")
    #     # Don't fail startup if sample data creation fails


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("Shutting down...")
