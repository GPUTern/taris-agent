"""认证控制器
处理用户认证相关的HTTP请求.
"""  # noqa: D205
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer

from src.web.middleware.auth_middleware import get_current_user
from src.web.models import (
    AuthResponse,
    ErrorResponse,
    LoginRequest,
    RegisterRequest,
    UpdateUserInfoRequest,
    UserInfoResponse,
)
from src.web.services import AuthService

# 创建路由器
router = APIRouter(prefix="/auth", tags=["认证"])

# HTTP Bearer 认证
security = HTTPBearer()


class AuthController:
    """认证控制器."""
    
    def __init__(self):  # noqa: D107
        self.auth_service = AuthService()


# 控制器实例
auth_controller = AuthController()


@router.post("/login", response_model=AuthResponse, responses={400: {"model": ErrorResponse}})
async def login(request: LoginRequest):
    """用户登录."""
    try:
        return await auth_controller.auth_service.login(request)
    except HTTPException:
        raise
    except Exception as e:
        print(f"登录错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登录服务暂时不可用，请稍后重试"
        )


@router.post("/register", response_model=UserInfoResponse, responses={400: {"model": ErrorResponse}})
async def register(request: RegisterRequest):
    """用户注册."""
    try:
        return await auth_controller.auth_service.register(request)
    except HTTPException:
        raise
    except Exception as e:
        print(f"注册错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="注册服务暂时不可用，请稍后重试"
        )


@router.get("/users/current", response_model=UserInfoResponse, responses={401: {"model": ErrorResponse}})
async def get_current_user_info(current_user: str = Depends(get_current_user)):
    """获取当前用户信息."""
    try:
        user_info = await auth_controller.auth_service.get_user_info(current_user)
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户信息不存在"
            )
        return user_info
    except HTTPException:
        raise
    except Exception as e:
        print(f"获取用户信息错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户信息失败，请稍后重试"
        )


@router.put("/users/current", response_model=UserInfoResponse, responses={400: {"model": ErrorResponse}, 401: {"model": ErrorResponse}})
async def update_user_info(
    update_data: UpdateUserInfoRequest,
    current_user: str = Depends(get_current_user)
):
    """更新当前用户信息"""
    try:
        return await auth_controller.auth_service.update_user_profile(
            username=current_user,
            email=update_data.email,
            current_password=update_data.current_password,
            new_password=update_data.new_password
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"更新用户信息错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新用户信息失败，请稍后重试"
        )