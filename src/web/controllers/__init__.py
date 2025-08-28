"""控制器层模块

导出所有控制器的路由
"""

from .auth_controller import router as auth_router
from .paper_controller import router as paper_router
from .news_controller import router as news_router
from .admin_controller import router as admin_router
from .tags_controller import router as tags_router
from .domains_controller import router as domains_router
from .library_controller import router as library_router
from .system_controller import router as system_router

__all__ = [
    "auth_router",
    "paper_router",
    "news_router",
    "admin_router",
    "tags_router",
    "domains_router",
    "library_router",
    "system_router"
]