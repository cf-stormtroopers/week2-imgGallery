from .auth_controller import router as auth_router
from .user_controller import router as user_router
from .category_controller import router as category_router
from .tag_controller import router as tag_router
from .comment_controller import router as comment_router
from .like_controller import router as like_router
from .blog_controller import router as blog_router
from .theme_controller import router as theme_router
from .uploader_controller import router as uploader_router
from .site_controller import router as site_router

__all__ = [
    "auth_router", 
    "user_router", 
    "category_router", 
    "tag_router", 
    "comment_router", 
    "like_router",
    "blog_router",
    "theme_router", 
    "uploader_router",
    "site_router"
]
