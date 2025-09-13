from .auth_controller import router as auth_router
from .user_controller import router as user_router
from .albums_controller import router as albums_router
from .images_controller import router as images_router
from .site_controller import router as site_router
from .collections_controller import router as collections_router

__all__ = [
    "auth_router", 
    "user_router", 
    "albums_router", 
    "images_router", 
    "site_router",
    "collections_router"
]
