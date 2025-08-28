"""
数据传输对象 (DTO)
包含API请求和响应的数据模型
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from .domain import PaperModel, NewsModel, UserModel, UserRole, LibraryModel


# 通用响应模型
class ErrorResponse(BaseModel):
    """错误响应"""
    error: str


# 认证相关DTO
class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., min_length=1, max_length=50, description="用户名")
    password: str = Field(..., min_length=1, description="密码")


class RegisterRequest(BaseModel):
    """注册请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名（3-50字符）")
    password: str = Field(..., min_length=6, max_length=128, description="密码（至少6个字符）")
    confirmPassword: str = Field(..., min_length=6, max_length=128, description="确认密码")
    email: str = Field(..., max_length=100, pattern=r'^[^@]+@[^@]+\.[^@]+$', description="有效的邮箱地址")


class AuthResponse(BaseModel):
    """认证响应"""
    token: str
    expires_in: int
    user_role: UserRole


# 论文相关DTO
class CreatePaperRequest(BaseModel):
    """创建论文请求"""
    title: str
    summary: str
    content: Optional[str] = None
    author: str
    tags: List[str]
    domain: str
    source: str
    cover_image: Optional[str] = None


class UpdatePaperRequest(BaseModel):
    """更新论文请求"""
    title: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    author: Optional[str] = None
    tags: Optional[List[str]] = None
    domain: Optional[str] = None
    source: Optional[str] = None
    cover_image: Optional[str] = None


class PaperListResponse(BaseModel):
    """论文列表响应"""
    papers: List[PaperModel]
    total: int


class TagsResponse(BaseModel):
    """标签响应"""
    tags: List[str]


class DomainsResponse(BaseModel):
    """领域响应"""
    domains: List[str]


# 资讯相关DTO
class CreateNewsRequest(BaseModel):
    """创建资讯请求"""
    title: str
    summary: str
    content: Optional[str] = None
    author: str
    tags: List[str]
    category: str
    source: str
    cover_image: Optional[str] = None
    external_url: Optional[str] = None


class UpdateNewsRequest(BaseModel):
    """更新资讯请求"""
    title: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    author: Optional[str] = None
    tags: Optional[List[str]] = None
    category: Optional[str] = None
    source: Optional[str] = None
    cover_image: Optional[str] = None
    external_url: Optional[str] = None


class NewsListResponse(BaseModel):
    """资讯列表响应"""
    news: List[NewsModel]
    total: int


class CategoriesResponse(BaseModel):
    """分类响应"""
    categories: List[str]


# 用户管理相关DTO
class CreateUserRequest(BaseModel):
    """创建用户请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名（3-50字符）")
    password: str = Field(..., min_length=6, max_length=128, description="密码（至少6个字符）")
    email: str = Field(..., max_length=100, pattern=r'^[^@]+@[^@]+\.[^@]+$', description="有效的邮箱地址")
    role: UserRole = Field(default=UserRole.USER, description="用户角色")


class UpdateUserInfoRequest(BaseModel):
    """更新用户信息请求"""
    email: Optional[str] = Field(None, max_length=100, pattern=r'^[^@]+@[^@]+\.[^@]+$', description="有效的邮箱地址")
    current_password: Optional[str] = Field(None, min_length=1, description="当前密码（修改密码时必填）")
    new_password: Optional[str] = Field(None, min_length=6, max_length=128, description="新密码（至少6个字符）")


class AdminUpdateUserRequest(BaseModel):
    """管理员更新用户请求"""
    email: Optional[str] = Field(None, max_length=100, pattern=r'^[^@]+@[^@]+\.[^@]+$', description="有效的邮箱地址")
    role: Optional[UserRole] = Field(None, description="用户角色")
    reset_password: Optional[str] = Field(None, min_length=6, max_length=128, description="重置密码（可选）")


class UpdateUserRoleRequest(BaseModel):
    """更新用户角色请求"""
    role: UserRole


class UserInfoResponse(BaseModel):
    """用户信息响应"""
    username: str
    email: str
    role: UserRole
    created_at: datetime


class UserListResponse(BaseModel):
    """用户列表响应"""
    users: List[UserModel]
    total: int


# 论文库相关DTO
class CreateLibraryRequest(BaseModel):
    """创建论文库请求"""
    name: str = Field(..., min_length=1, max_length=100, description="论文库名称（1-100字符）")
    description: Optional[str] = Field(None, max_length=500, description="论文库描述（可选，最多500字符）")
    is_public: bool = Field(False, description="是否公开（默认私有）")


class UpdateLibraryRequest(BaseModel):
    """更新论文库请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="论文库名称（1-100字符）")
    description: Optional[str] = Field(None, max_length=500, description="论文库描述（最多500字符）")
    is_public: Optional[bool] = Field(None, description="是否公开")


class AddPaperToLibraryRequest(BaseModel):
    """添加论文到论文库请求"""
    paper_id: str


class AddItemToLibraryRequest(BaseModel):
    """添加内容到收藏库请求"""
    item_id: str
    item_type: str  # 'paper' or 'news' = Field(..., description="论文ID")


class LibraryListResponse(BaseModel):
    """论文库列表响应"""
    libraries: List[LibraryModel]
    total: int


class LibraryDetailResponse(BaseModel):
    """论文库详情响应"""
    library: LibraryModel
    papers: List[PaperModel]
    news: List[NewsModel] = Field(default_factory=list)  # 新增资讯列表 