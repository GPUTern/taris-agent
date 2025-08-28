"""数据访问层模块

导出所有Repository类
"""

from .base import BaseRepository
from .user_repository import UserRepository
from .paper_repository import PaperRepository
from .news_repository import NewsRepository
from .library_repository import LibraryRepository

__all__ = [
    "BaseRepository",
    "UserRepository", 
    "PaperRepository",
    "NewsRepository",
    "LibraryRepository"
] 