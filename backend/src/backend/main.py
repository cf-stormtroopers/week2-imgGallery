from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from backend.config import settings
from backend.config.database import create_db_and_tables
from backend.controllers import (
    auth_router, 
    user_router, 
    category_router, 
    tag_router, 
    comment_router, 
    like_router,
    blog_router,
    theme_router,
    uploader_router,
    site_router
)
from backend.controllers.role_controller import router as role_router


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
        debug=settings.debug
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "https://chyrp.cf1.ranjithrd.in",
            "http://chyrp.cf1.ranjithrd.in",
            "http://localhost:3000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(auth_router)
    app.include_router(user_router)
    app.include_router(blog_router)
    app.include_router(category_router)
    app.include_router(tag_router)
    app.include_router(comment_router)
    app.include_router(like_router)
    app.include_router(theme_router)
    app.include_router(uploader_router)
    app.include_router(site_router)
    app.include_router(role_router)
    
    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Global exception handler caught: {exc}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "version": "1.0.0"}
    
    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "message": "Blog Backend API",
            "version": "1.0.0",
            "docs": "/docs"
        }
    
    return app


# Create application instance
app = create_app()


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info("Starting up...")
    create_db_and_tables()
    logger.info("Database tables created/verified")
    
    # Initialize extensions
    from backend.config.database import create_extensions
    create_extensions()
    logger.info("Extensions initialized")
    
    # Initialize default settings
    from backend.config.database import create_default_settings
    create_default_settings()
    logger.info("Default settings initialized")
    
    # Initialize permissions and roles
    from backend.config.database import get_session
    from backend.services.permission_service import PermissionService
    
    # Get a database session
    session_gen = get_session()
    session = next(session_gen)
    
    try:
        permission_service = PermissionService(session)
        permission_service.ensure_initial_data()
        logger.info("Initial permissions and roles ensured")
    finally:
        session.close()
    
    # Create sample data
    from backend.config.database import create_sample_data
    try:
        create_sample_data()
        logger.info("Sample data created")
    except Exception as e:
        logger.warning(f"Sample data creation failed: {e}")
        # Don't fail startup if sample data creation fails


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("Shutting down...")
