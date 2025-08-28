"""
标签控制器
处理标签相关的HTTP请求
"""
from fastapi import APIRouter, HTTPException, status

from src.web.models import TagsResponse, ErrorResponse
from src.web.services import PaperService

# 创建路由器
router = APIRouter(prefix="/tags", tags=["标签"])


class TagsController:
    """标签控制器"""
    
    def __init__(self):
        self.paper_service = PaperService()


# 控制器实例
tags_controller = TagsController()


@router.get("", response_model=TagsResponse, responses={400: {"model": ErrorResponse}})
async def get_tags():
    """获取所有标签"""
    try:
        return await tags_controller.paper_service.get_tags()
    except HTTPException:
        raise
    except Exception as e:
        print(f"获取标签错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取标签失败，请稍后重试"
        ) 