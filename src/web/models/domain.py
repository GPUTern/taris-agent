"""
领域模型 - 业务实体
包含核心的业务数据模型
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class UserRole(str, Enum):
    """用户角色枚举"""
    SUPER_ADMIN = "super_admin"  # 超级管理员 - 拥有所有权限
    PAPER_ADMIN = "paper_admin"  # 论文管理员 - 只能管理论文
    USER = "user"  # 普通用户 - 只能浏览论文和修改自己信息


class CommentModel(BaseModel):
    """评论模型"""
    user: str
    content: str
    time: datetime


class PaperModel(BaseModel):
    """论文模型"""
    id: str
    title: str
    summary: str
    content: Optional[str] = None
    author: str
    tags: List[str]
    domain: str
    source: str
    publish_time: datetime
    cover_image: Optional[str] = None
    comments: List[CommentModel] = Field(default_factory=list)


class NewsModel(BaseModel):
    """资讯模型"""
    id: str
    title: str
    summary: str
    content: Optional[str] = None
    author: str
    tags: List[str]
    category: str  # 使用category替代domain
    source: str
    publish_time: datetime
    cover_image: Optional[str] = None
    view_count: int = 0  # 浏览次数
    external_url: Optional[str] = None  # 外部链接
    comments: List[CommentModel] = Field(default_factory=list)


class UserModel(BaseModel):
    """用户模型"""
    username: str
    email: str
    hashed_password: str
    role: UserRole = UserRole.USER
    created_at: datetime


class LibraryModel(BaseModel):
    """收藏库模型"""
    id: str
    name: str
    description: Optional[str] = None
    username: str
    is_public: bool = False
    created_at: datetime
    updated_at: datetime
    papers: List[PaperModel] = Field(default_factory=list)  # 包含的论文列表
    paper_count: int = 0  # 论文数量
    news_count: int = 0  # 资讯数量
    total_count: int = 0  # 总内容数量


class LibraryPaperModel(BaseModel):
    """论文库-论文关联模型"""
    library_id: str
    paper_id: str
    added_at: datetime 