"""
领域控制器
处理研究领域相关的HTTP请求
"""
from fastapi import APIRouter, HTTPException, status

from src.web.models import DomainsResponse, ErrorResponse
from src.web.services import PaperService

# 创建路由器
router = APIRouter(prefix="/domains", tags=["研究领域"])


class DomainsController:
    """领域控制器"""
    
    def __init__(self):
        self.paper_service = PaperService()


# 控制器实例
domains_controller = DomainsController()


@router.get("", response_model=DomainsResponse, responses={400: {"model": ErrorResponse}})
async def get_domains():
    """获取所有研究领域"""
    try:
        return await domains_controller.paper_service.get_domains()
    except HTTPException:
        raise
    except Exception as e:
        print(f"获取研究领域错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取研究领域失败，请稍后重试"
        ) 