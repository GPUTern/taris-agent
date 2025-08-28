"""
资讯服务
处理资讯相关的业务逻辑
"""
from typing import List, Optional, Tuple
from fastapi import HTTPException, status

from src.web.models import (
    NewsModel, CreateNewsRequest, UpdateNewsRequest,
    NewsListResponse, TagsResponse, CategoriesResponse
)
from src.web.repositories import NewsRepository


class NewsService:
    """资讯服务"""
    
    def __init__(self):
        self.news_repo = NewsRepository()
    
    async def get_news_list(self, 
                           tag: Optional[str] = None,
                           category: Optional[str] = None,
                           sort: str = "newest",
                           date_range: Optional[str] = None,
                           search: Optional[str] = None,
                           page: int = 1,
                           page_size: int = 10) -> NewsListResponse:
        """获取资讯列表"""
        if page < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="页码必须大于0"
            )
        
        if page_size < 1 or page_size > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="每页数量必须在1-100之间"
            )
        
        try:
            news_list, total = await self.news_repo.get_news_list(
                tag=tag,
                category=category,
                sort=sort,
                date_range=date_range,
                search=search,
                page=page,
                page_size=page_size
            )
            
            return NewsListResponse(news=news_list, total=total)
        except Exception as e:
            print(f"获取资讯列表错误: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="获取资讯列表失败，请稍后重试"
            )
    
    async def get_news_by_id(self, news_id: str, increment_view: bool = True) -> NewsModel:
        """根据ID获取资讯详情"""
        news = await self.news_repo.get_news_by_id(news_id)
        if not news:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="资讯不存在"
            )
        
        # 增加浏览次数
        if increment_view:
            try:
                await self.news_repo.increment_view_count(news_id)
                # 更新返回对象的浏览次数
                news.view_count += 1
            except Exception as e:
                print(f"更新浏览次数失败: {e}")
                # 不影响主要功能，继续返回资讯
        
        return news
    
    async def create_news(self, news_data: CreateNewsRequest) -> NewsModel:
        """创建资讯"""
        # 验证必填字段
        if not news_data.title.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="资讯标题不能为空"
            )
        
        if not news_data.summary.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="资讯摘要不能为空"
            )
        
        if not news_data.author.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="作者不能为空"
            )
        
        if not news_data.category.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="分类不能为空"
            )
        
        if not news_data.tags or len(news_data.tags) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="至少需要一个标签"
            )
        
        try:
            return await self.news_repo.create_news(news_data)
        except Exception as e:
            print(f"创建资讯错误: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="创建资讯失败，请稍后重试"
            )
    
    async def update_news(self, news_id: str, news_data: UpdateNewsRequest) -> NewsModel:
        """更新资讯"""
        # 验证更新数据
        if news_data.title is not None and not news_data.title.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="资讯标题不能为空"
            )
        
        if news_data.summary is not None and not news_data.summary.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="资讯摘要不能为空"
            )
        
        if news_data.author is not None and not news_data.author.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="作者不能为空"
            )
        
        if news_data.category is not None and not news_data.category.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="分类不能为空"
            )
        
        try:
            updated_news = await self.news_repo.update_news(news_id, news_data)
            if not updated_news:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="资讯不存在"
                )
            return updated_news
        except HTTPException:
            raise
        except Exception as e:
            print(f"更新资讯错误: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="更新资讯失败，请稍后重试"
            )
    
    async def delete_news(self, news_id: str) -> bool:
        """删除资讯"""
        # 检查资讯是否存在
        existing_news = await self.news_repo.get_news_by_id(news_id)
        if not existing_news:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="资讯不存在"
            )
        
        try:
            return await self.news_repo.delete_news(news_id)
        except Exception as e:
            print(f"删除资讯错误: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="删除资讯失败，请稍后重试"
            )
    
    async def get_all_tags(self) -> TagsResponse:
        """获取所有标签"""
        try:
            tags = await self.news_repo.get_all_tags()
            return TagsResponse(tags=tags)
        except Exception as e:
            print(f"获取标签错误: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="获取标签失败，请稍后重试"
            )
    
    async def get_all_categories(self) -> CategoriesResponse:
        """获取所有分类"""
        try:
            categories = await self.news_repo.get_all_categories()
            return CategoriesResponse(categories=categories)
        except Exception as e:
            print(f"获取分类错误: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="获取分类失败，请稍后重试"
            ) 