"""数据模型模块

导出所有的领域模型和数据传输对象
"""

# 从domain模块导出领域模型
from .domain import (
    UserRole,
    CommentModel,
    PaperModel,
    NewsModel,
    UserModel,
    LibraryModel,
    LibraryPaperModel
)

# 从dto模块导出数据传输对象
from .dto import (
    # 通用响应
    ErrorResponse,
    
    # 认证相关
    LoginRequest,
    RegisterRequest,
    AuthResponse,
    
    # 论文相关
    CreatePaperRequest,
    UpdatePaperRequest,
    PaperListResponse,
    TagsResponse,
    DomainsResponse,
    
    # 资讯相关
    CreateNewsRequest,
    UpdateNewsRequest,
    NewsListResponse,
    CategoriesResponse,
    
    # 用户管理相关
    CreateUserRequest,
    UpdateUserInfoRequest,
    AdminUpdateUserRequest,
    UpdateUserRoleRequest,
    UserInfoResponse,
    UserListResponse,
    
    # 论文库相关
    CreateLibraryRequest,
    UpdateLibraryRequest,
    AddPaperToLibraryRequest,
    AddItemToLibraryRequest,
    LibraryListResponse,
    LibraryDetailResponse
)

__all__ = [
    # 领域模型
    "UserRole",
    "CommentModel", 
    "PaperModel",
    "NewsModel",
    "UserModel",
    "LibraryModel",
    "LibraryPaperModel",
    
    # 数据传输对象
    "ErrorResponse",
    "LoginRequest",
    "RegisterRequest",
    "AuthResponse",
    "CreatePaperRequest",
    "UpdatePaperRequest",
    "PaperListResponse",
    "TagsResponse",
    "DomainsResponse",
    "CreateNewsRequest",
    "UpdateNewsRequest",
    "NewsListResponse",
    "CategoriesResponse",
    "CreateUserRequest",
    "UpdateUserInfoRequest",
    "AdminUpdateUserRequest",
    "UpdateUserRoleRequest",
    "UserInfoResponse",
    "UserListResponse",
    "CreateLibraryRequest",
    "UpdateLibraryRequest",
    "AddPaperToLibraryRequest",
    "AddItemToLibraryRequest",
    "LibraryListResponse",
    "LibraryDetailResponse"
] 