"""业务逻辑层模块

导出所有Service类
"""

from .auth_service import AuthService
from .paper_service import PaperService 
from .news_service import NewsService
from .admin_service import AdminService
from .library_service import LibraryService

__all__ = [
    "AuthService",
    "PaperService",
    "NewsService",
    "AdminService",
    "LibraryService"
] 