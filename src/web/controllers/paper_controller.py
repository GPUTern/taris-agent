"""
论文控制器
处理论文相关的HTTP请求
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Query, Depends

from src.web.models import (
    PaperListResponse, PaperModel, ErrorResponse,
    CreatePaperRequest, UpdatePaperRequest,
    TagsResponse, DomainsResponse
)
from src.web.services import PaperService
from src.web.middleware.auth_middleware import get_current_paper_admin_user
from src.web.config.settings import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE

# 创建路由器
router = APIRouter(prefix="/papers", tags=["论文"])


class PaperController:
    """论文控制器"""
    
    def __init__(self):
        self.paper_service = PaperService()


# 控制器实例
paper_controller = PaperController()


@router.get("", response_model=PaperListResponse, responses={400: {"model": ErrorResponse}})
async def get_papers(
    tag: Optional[str] = Query(None, description="标签过滤"),
    domain: Optional[str] = Query(None, description="研究领域"),
    sort: str = Query("newest", pattern="^(newest|hot)$", description="排序方式"),
    date_range: Optional[str] = Query(None, pattern="^(1d|3d|7d|30d|180d|1y|all)$", description="时间范围"),
    search: Optional[str] = Query(None, description="搜索关键词（搜索标题、作者、内容）"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="每页条数")
):
    """获取论文列表"""
    try:
        return await paper_controller.paper_service.get_papers(
            tag=tag,
            domain=domain,
            sort=sort,
            date_range=date_range,
            search=search,
            page=page,
            page_size=page_size
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"获取论文列表错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取论文列表失败，请稍后重试"
        )


@router.get("/{paper_id}", response_model=PaperModel, responses={404: {"model": ErrorResponse}})
async def get_paper(paper_id: str):
    """获取论文详情"""
    try:
        return await paper_controller.paper_service.get_paper_by_id(paper_id)
    except HTTPException:
        raise
    except Exception as e:
        print(f"获取论文详情错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取论文详情失败，请稍后重试"
        )


# 管理员功能 - 创建论文
@router.post("", response_model=PaperModel, responses={400: {"model": ErrorResponse}})
async def create_paper(
    paper_data: CreatePaperRequest,
    current_admin: str = Depends(get_current_paper_admin_user)
):
    """创建论文（论文管理员和超级管理员）"""
    try:
        return await paper_controller.paper_service.create_paper(paper_data)
    except HTTPException:
        raise
    except Exception as e:
        print(f"创建论文错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建论文失败，请稍后重试"
        )


# 管理员功能 - 更新论文
@router.put("/{paper_id}", response_model=PaperModel, responses={404: {"model": ErrorResponse}})
async def update_paper(
    paper_id: str,
    paper_data: UpdatePaperRequest,
    current_admin: str = Depends(get_current_paper_admin_user)
):
    """更新论文（论文管理员和超级管理员）"""
    try:
        return await paper_controller.paper_service.update_paper(paper_id, paper_data)
    except HTTPException:
        raise
    except Exception as e:
        print(f"更新论文错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新论文失败，请稍后重试"
        )


# 管理员功能 - 删除论文
@router.delete("/{paper_id}", response_model=PaperModel, responses={404: {"model": ErrorResponse}})
async def delete_paper(
    paper_id: str,
    current_admin: str = Depends(get_current_paper_admin_user)
):
    """删除论文（论文管理员和超级管理员）"""
    try:
        return await paper_controller.paper_service.delete_paper(paper_id)
    except HTTPException:
        raise
    except Exception as e:
        print(f"删除论文错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除论文失败，请稍后重试"
        )