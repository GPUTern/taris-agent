"""
论文库控制器
处理论文库相关的HTTP请求
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Query, Depends

from src.web.models import (
    LibraryListResponse, LibraryDetailResponse, LibraryModel, ErrorResponse,
    CreateLibraryRequest, UpdateLibraryRequest, AddPaperToLibraryRequest, AddItemToLibraryRequest
)
from src.web.services import LibraryService
from src.web.middleware.auth_middleware import get_current_user
from src.web.config.settings import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE

# 创建路由器
router = APIRouter(prefix="/libraries", tags=["论文库"])


class LibraryController:
    """论文库控制器"""
    
    def __init__(self):
        self.library_service = LibraryService()


# 控制器实例
library_controller = LibraryController()


@router.post("", response_model=LibraryModel, responses={400: {"model": ErrorResponse}})
async def create_library(
    library_data: CreateLibraryRequest,
    current_user: str = Depends(get_current_user)
):
    """创建论文库"""
    try:
        return await library_controller.library_service.create_library(library_data, current_user)
    except HTTPException:
        raise
    except Exception as e:
        print(f"创建论文库错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建论文库失败，请稍后重试"
        )


@router.get("", response_model=LibraryListResponse, responses={400: {"model": ErrorResponse}})
async def get_libraries(
    owner: Optional[str] = Query(None, description="所有者用户名过滤"),
    is_public: Optional[bool] = Query(None, description="公开状态过滤"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="每页条数"),
    current_user: Optional[str] = Depends(get_current_user)
):
    """获取论文库列表"""
    try:
        if owner:
            # 获取指定用户的论文库
            return await library_controller.library_service.get_user_libraries(
                username=owner,
                page=page,
                page_size=page_size
            )
        elif is_public is True:
            # 获取公开的论文库
            return await library_controller.library_service.get_public_libraries(
                page=page,
                page_size=page_size
            )
        elif current_user:
            # 获取当前用户的论文库
            return await library_controller.library_service.get_user_libraries(
                username=current_user,
                page=page,
                page_size=page_size
            )
        else:
            # 未登录用户且未指定过滤条件，返回公开论文库
            return await library_controller.library_service.get_public_libraries(
                page=page,
                page_size=page_size
            )
    except HTTPException:
        raise
    except Exception as e:
        print(f"获取论文库列表错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取论文库列表失败，请稍后重试"
        )


@router.get("/{library_id}", response_model=LibraryDetailResponse, responses={404: {"model": ErrorResponse}})
async def get_library_detail(
    library_id: str,
    current_user: Optional[str] = Depends(get_current_user)
):
    """获取论文库详情"""
    try:
        return await library_controller.library_service.get_library_detail(library_id, current_user)
    except HTTPException:
        raise
    except Exception as e:
        print(f"获取论文库详情错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取论文库详情失败，请稍后重试"
        )


@router.put("/{library_id}", response_model=LibraryModel, responses={404: {"model": ErrorResponse}})
async def update_library(
    library_id: str,
    library_data: UpdateLibraryRequest,
    current_user: str = Depends(get_current_user)
):
    """更新论文库"""
    try:
        return await library_controller.library_service.update_library(library_id, library_data, current_user)
    except HTTPException:
        raise
    except Exception as e:
        print(f"更新论文库错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新论文库失败，请稍后重试"
        )


@router.delete("/{library_id}", response_model=LibraryModel, responses={404: {"model": ErrorResponse}})
async def delete_library(
    library_id: str,
    current_user: str = Depends(get_current_user)
):
    """删除论文库"""
    try:
        return await library_controller.library_service.delete_library(library_id, current_user)
    except HTTPException:
        raise
    except Exception as e:
        print(f"删除论文库错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除论文库失败，请稍后重试"
        )


@router.post("/{library_id}/papers", response_model=dict, responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}})
async def add_paper_to_library(
    library_id: str,
    request: AddPaperToLibraryRequest,
    current_user: str = Depends(get_current_user)
):
    """添加论文到论文库"""
    try:
        return await library_controller.library_service.add_paper_to_library(library_id, request, current_user)
    except HTTPException:
        raise
    except Exception as e:
        print(f"添加论文到论文库错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="添加论文失败，请稍后重试"
        )


@router.delete("/{library_id}/papers/{paper_id}", response_model=dict, responses={404: {"model": ErrorResponse}})
async def remove_paper_from_library(
    library_id: str,
    paper_id: str,
    current_user: str = Depends(get_current_user)
):
    """从论文库移除论文"""
    try:
        return await library_controller.library_service.remove_paper_from_library(library_id, paper_id, current_user)
    except HTTPException:
        raise
    except Exception as e:
        print(f"从论文库移除论文错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="移除论文失败，请稍后重试"
        )


@router.get("/{library_id}/papers", response_model=dict, responses={404: {"model": ErrorResponse}})
async def get_library_papers(
    library_id: str,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="每页条数"),
    current_user: str = Depends(get_current_user)
):
    """获取论文库中的论文列表"""
    try:
        return await library_controller.library_service.get_library_papers(library_id, page, page_size, current_user)
    except HTTPException:
        raise
    except Exception as e:
        print(f"获取论文库中的论文列表错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取论文库中的论文列表失败，请稍后重试"
        )


# 新的通用收藏API，支持论文和资讯
@router.post("/{library_id}/items", response_model=dict, responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}})
async def add_item_to_library(
    library_id: str,
    request: AddItemToLibraryRequest,
    current_user: str = Depends(get_current_user)
):
    """添加内容（论文或资讯）到收藏库"""
    try:
        return await library_controller.library_service.add_item_to_library(library_id, request, current_user)
    except HTTPException:
        raise
    except Exception as e:
        print(f"添加内容到收藏库错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="添加内容失败，请稍后重试"
        )


@router.delete("/{library_id}/items/{item_id}/{item_type}", response_model=dict, responses={404: {"model": ErrorResponse}})
async def remove_item_from_library(
    library_id: str,
    item_id: str,
    item_type: str,
    current_user: str = Depends(get_current_user)
):
    """从收藏库移除内容（论文或资讯）"""
    try:
        return await library_controller.library_service.remove_item_from_library(library_id, item_id, item_type, current_user)
    except HTTPException:
        raise
    except Exception as e:
        print(f"从收藏库移除内容错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="移除内容失败，请稍后重试"
        )


@router.get("/{library_id}/items", response_model=dict, responses={404: {"model": ErrorResponse}})
async def get_library_items(
    library_id: str,
    item_type: Optional[str] = Query(None, description="内容类型过滤: paper, news"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="每页条数"),
    current_user: str = Depends(get_current_user)
):
    """获取收藏库中的内容列表"""
    try:
        return await library_controller.library_service.get_library_items(library_id, item_type, page, page_size, current_user)
    except HTTPException:
        raise
    except Exception as e:
        print(f"获取收藏库中的内容列表错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取收藏库中的内容列表失败，请稍后重试"
        )