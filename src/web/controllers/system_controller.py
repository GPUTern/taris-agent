"""
系统控制器
处理系统相关的HTTP请求
"""
from fastapi import APIRouter, HTTPException, status, Depends

from src.web.models import ErrorResponse
from src.web.services import AdminService
from src.web.middleware.auth_middleware import get_current_admin_user

# 创建路由器
router = APIRouter(prefix="/system", tags=["系统"])


class SystemController:
    """系统控制器"""
    
    def __init__(self):
        self.admin_service = AdminService()


# 控制器实例
system_controller = SystemController()


@router.get("/statistics")
async def get_system_statistics(
    current_admin: str = Depends(get_current_admin_user)
):
    """获取系统统计信息"""
    try:
        return await system_controller.admin_service.get_stats()
    except HTTPException:
        raise
    except Exception as e:
        print(f"获取统计信息错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取统计信息失败，请稍后重试"
        )