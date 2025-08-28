"""资讯控制器
处理资讯相关的HTTP请求.
"""  # noqa: D205
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.web.config.settings import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from src.web.middleware.auth_middleware import get_current_paper_admin_user
from src.web.models import (
    CategoriesResponse,
    CreateNewsRequest,
    ErrorResponse,
    NewsListResponse,
    NewsModel,
    TagsResponse,
    UpdateNewsRequest,
)
from src.web.services import NewsService

# 创建路由器
router = APIRouter(prefix="/news", tags=["资讯"])


class NewsController:
    """资讯控制器"""
    
    def __init__(self):
        self.news_service = NewsService()


# 创建控制器实例
news_controller = NewsController()


# 公共接口 - 获取资讯列表
@router.get("", response_model=NewsListResponse, responses={400: {"model": ErrorResponse}})
async def get_news_list(
    tag: Optional[str] = Query(None, description="标签筛选"),
    category: Optional[str] = Query(None, description="分类筛选"),
    sort: str = Query("newest", description="排序方式: newest(最新), hot(热门), popular(最受欢迎)"),
    date_range: Optional[str] = Query(None, pattern="^(1d|3d|7d|30d|180d|1y|all)$", description="日期范围: 1d, 3d, 7d, 30d, 180d, 1y, all"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="每页数量")
):
    """获取资讯列表"""
    return await news_controller.news_service.get_news_list(
        tag=tag,
        category=category,
        sort=sort,
        date_range=date_range,
        search=search,
        page=page,
        page_size=page_size
    )


# 公共接口 - 获取资讯详情
@router.get("/{news_id}", response_model=NewsModel, responses={404: {"model": ErrorResponse}})
async def get_news_detail(news_id: str):
    """获取资讯详情"""
    return await news_controller.news_service.get_news_by_id(news_id)


# 公共接口 - 获取所有标签
@router.get("/tags/all", response_model=TagsResponse)
async def get_all_tags():
    """获取所有标签"""
    return await news_controller.news_service.get_all_tags()


# 公共接口 - 获取所有分类
@router.get("/categories/all", response_model=CategoriesResponse)
async def get_all_categories():
    """获取所有分类"""
    return await news_controller.news_service.get_all_categories()


# 管理员功能 - 创建资讯
@router.post("", response_model=NewsModel, responses={400: {"model": ErrorResponse}})
async def create_news(
    news_data: CreateNewsRequest,
    current_admin: str = Depends(get_current_paper_admin_user)
):
    """创建资讯（论文管理员和超级管理员）"""
    try:
        return await news_controller.news_service.create_news(news_data)
    except HTTPException:
        raise
    except Exception as e:
        print(f"创建资讯错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建资讯失败，请稍后重试"
        )


# 管理员功能 - 更新资讯
@router.put("/{news_id}", response_model=NewsModel, responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}})
async def update_news(
    news_id: str,
    news_data: UpdateNewsRequest,
    current_admin: str = Depends(get_current_paper_admin_user)
):
    """更新资讯（论文管理员和超级管理员）"""
    try:
        return await news_controller.news_service.update_news(news_id, news_data)
    except HTTPException:
        raise
    except Exception as e:
        print(f"更新资讯错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新资讯失败，请稍后重试"
        )


# 管理员功能 - 删除资讯
@router.delete("/{news_id}", response_model=NewsModel, responses={404: {"model": ErrorResponse}})
async def delete_news(
    news_id: str,
    current_admin: str = Depends(get_current_paper_admin_user)
):
    """删除资讯（论文管理员和超级管理员）"""
    try:
        return await news_controller.news_service.delete_news(news_id)
    except HTTPException:
        raise
    except Exception as e:
        print(f"删除资讯错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除资讯失败，请稍后重试"
        )