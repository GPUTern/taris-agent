"""
认证中间件
处理JWT令牌验证和权限检查
"""
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.web.models import UserRole
from src.web.services import AuthService

# HTTP Bearer 认证
security = HTTPBearer()

# 认证服务实例
auth_service = AuthService()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """获取当前用户（依赖注入）"""
    token = credentials.credentials
    user_info = await auth_service.get_current_user_info(token)
    return user_info["username"]


async def get_current_user_with_role(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """获取当前用户和角色信息"""
    token = credentials.credentials
    return await auth_service.get_current_user_info(token)


async def get_current_super_admin_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """获取当前超级管理员用户（只允许超级管理员访问）"""
    token = credentials.credentials
    return await auth_service.verify_admin_permission(token, UserRole.SUPER_ADMIN)


async def get_current_paper_admin_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """获取当前论文管理员用户（允许超级管理员和论文管理员访问）"""
    token = credentials.credentials
    return await auth_service.verify_admin_permission(token, UserRole.PAPER_ADMIN)


async def get_current_admin_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """获取当前管理员用户（兼容性函数，允许任何级别的管理员访问）"""
    token = credentials.credentials
    return await auth_service.verify_admin_permission(token, UserRole.PAPER_ADMIN) 