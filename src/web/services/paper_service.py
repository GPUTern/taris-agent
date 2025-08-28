"""
论文服务
处理论文相关的业务逻辑
"""
from typing import List, Optional, Tuple
from fastapi import HTTPException, status

from src.web.models import (
    PaperModel, CreatePaperRequest, UpdatePaperRequest,
    PaperListResponse, TagsResponse, DomainsResponse
)
from src.web.repositories import PaperRepository


class PaperService:
    """论文服务"""
    
    def __init__(self):
        self.paper_repo = PaperRepository()
    
    async def get_papers(self, 
                        tag: Optional[str] = None,
                        domain: Optional[str] = None,
                        sort: str = "newest",
                        date_range: Optional[str] = None,
                        search: Optional[str] = None,
                        page: int = 1,
                        page_size: int = 10) -> PaperListResponse:
        """获取论文列表"""
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
            papers, total = await self.paper_repo.get_papers(
                tag=tag,
                domain=domain,
                sort=sort,
                date_range=date_range,
                search=search,
                page=page,
                page_size=page_size
            )
            
            return PaperListResponse(papers=papers, total=total)
        except Exception as e:
            print(f"获取论文列表错误: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="获取论文列表失败，请稍后重试"
            )
    
    async def get_paper_by_id(self, paper_id: str) -> PaperModel:
        """根据ID获取论文详情"""
        paper = await self.paper_repo.get_paper_by_id(paper_id)
        if not paper:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="论文不存在"
            )
        return paper
    
    async def create_paper(self, paper_data: CreatePaperRequest) -> PaperModel:
        """创建论文"""
        # 验证必填字段
        if not paper_data.title.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="论文标题不能为空"
            )
        
        if not paper_data.summary.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="论文摘要不能为空"
            )
        
        if not paper_data.author.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="作者不能为空"
            )
        
        if not paper_data.domain.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="领域不能为空"
            )
        
        if not paper_data.tags or len(paper_data.tags) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="至少需要一个标签"
            )
        
        try:
            return await self.paper_repo.create_paper(paper_data)
        except Exception as e:
            print(f"创建论文错误: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="创建论文失败，请稍后重试"
            )
    
    async def update_paper(self, paper_id: str, paper_data: UpdatePaperRequest) -> PaperModel:
        """更新论文"""
        # 验证字段（如果提供了值）
        if paper_data.title is not None and not paper_data.title.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="论文标题不能为空"
            )
        
        if paper_data.summary is not None and not paper_data.summary.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="论文摘要不能为空"
            )
        
        if paper_data.author is not None and not paper_data.author.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="作者不能为空"
            )
        
        if paper_data.domain is not None and not paper_data.domain.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="领域不能为空"
            )
        
        if paper_data.tags is not None and len(paper_data.tags) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="至少需要一个标签"
            )
        
        try:
            paper = await self.paper_repo.update_paper(paper_id, paper_data)
            if not paper:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="论文不存在"
                )
            return paper
        except HTTPException:
            raise
        except Exception as e:
            print(f"更新论文错误: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="更新论文失败，请稍后重试"
            )
    
    async def delete_paper(self, paper_id: str) -> dict:
        """删除论文"""
        try:
            success = await self.paper_repo.delete_paper(paper_id)
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="论文不存在"
                )
            return {"message": "论文删除成功"}
        except HTTPException:
            raise
        except Exception as e:
            print(f"删除论文错误: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="删除论文失败，请稍后重试"
            )
    
    async def get_tags(self) -> TagsResponse:
        """获取所有标签"""
        try:
            tags = await self.paper_repo.get_all_tags()
            return TagsResponse(tags=tags)
        except Exception as e:
            print(f"获取标签错误: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="获取标签失败，请稍后重试"
            )
    
    async def get_domains(self) -> DomainsResponse:
        """获取所有领域"""
        try:
            domains = await self.paper_repo.get_all_domains()
            return DomainsResponse(domains=domains)
        except Exception as e:
            print(f"获取领域错误: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="获取领域失败，请稍后重试"
            ) 