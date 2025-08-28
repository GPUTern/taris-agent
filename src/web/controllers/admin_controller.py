"""
管理员控制器
处理管理员相关的HTTP请求
"""
from fastapi import APIRouter, HTTPException, status, Depends, Query

from src.web.models import (
    PaperModel, CreatePaperRequest, UpdatePaperRequest,
    UserListResponse, UpdateUserRoleRequest, ErrorResponse,
    CreateUserRequest, AdminUpdateUserRequest, UserInfoResponse
)
from src.web.services import AdminService, PaperService
from src.web.middleware.auth_middleware import (
    get_current_admin_user, get_current_super_admin_user, get_current_paper_admin_user
)

# 创建路由器
router = APIRouter(prefix="/admin", tags=["管理员"])


class AdminController:
    """管理员控制器"""
    
    def __init__(self):
        self.admin_service = AdminService()
        self.paper_service = PaperService()


# 控制器实例
admin_controller = AdminController()




# 用户管理
@router.get("/users", response_model=UserListResponse)
async def get_users(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    current_admin: str = Depends(get_current_super_admin_user)
):
    """获取用户列表（仅超级管理员）"""
    try:
        return await admin_controller.admin_service.get_users(page=page, page_size=page_size)
    except HTTPException:
        raise
    except Exception as e:
        print(f"获取用户列表错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户列表失败，请稍后重试"
        )


@router.post("/users", response_model=UserInfoResponse, responses={400: {"model": ErrorResponse}})
async def create_user(
    user_data: CreateUserRequest,
    current_admin: str = Depends(get_current_super_admin_user)
):
    """创建用户（仅超级管理员）"""
    try:
        return await admin_controller.admin_service.create_user(user_data)
    except HTTPException:
        raise
    except Exception as e:
        print(f"创建用户错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建用户失败，请稍后重试"
        )


@router.put("/users/{username}", response_model=UserInfoResponse, responses={404: {"model": ErrorResponse}})
async def admin_update_user(
    username: str,
    update_data: AdminUpdateUserRequest,
    current_admin: str = Depends(get_current_super_admin_user)
):
    """管理员编辑用户信息（仅超级管理员）"""
    try:
        return await admin_controller.admin_service.admin_update_user(username, update_data)
    except HTTPException:
        raise
    except Exception as e:
        print(f"编辑用户错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="编辑用户失败，请稍后重试"
        )


@router.put("/users/{username}/role", response_model=UserInfoResponse, responses={404: {"model": ErrorResponse}})
async def update_user_role(
    username: str,
    role_data: UpdateUserRoleRequest,
    current_admin: str = Depends(get_current_super_admin_user)
):
    """更新用户角色（仅超级管理员）"""
    try:
        return await admin_controller.admin_service.update_user_role(username, role_data, current_admin)
    except HTTPException:
        raise
    except Exception as e:
        print(f"更新用户角色错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新用户角色失败，请稍后重试"
        )


@router.delete("/users/{username}", response_model=UserInfoResponse, responses={404: {"model": ErrorResponse}})
async def delete_user(
    username: str,
    current_admin: str = Depends(get_current_super_admin_user)
):
    """删除用户（仅超级管理员）"""
    try:
        return await admin_controller.admin_service.delete_user(username, current_admin)
    except HTTPException:
        raise
    except Exception as e:
        print(f"删除用户错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除用户失败，请稍后重试"
        )
