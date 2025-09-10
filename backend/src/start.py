#!/usr/bin/env python3
"""
Startup script for the blog backend application.
"""

import uvicorn
from backend.config import settings


def main():
    """Main entry point for the application."""
    uvicorn.run(
        "backend.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info" if not settings.debug else "debug"
    )


if __name__ == "__main__":
    main()
