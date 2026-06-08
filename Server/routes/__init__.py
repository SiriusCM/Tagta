from .auth import router as auth_router
from .user import router as user_router
from .post import router as post_router
from .follow import router as follow_router

__all__ = ['auth_router', 'user_router', 'post_router', 'follow_router']