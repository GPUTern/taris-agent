"""
论文库Service
处理论文库相关的业务逻辑
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, UTC
import uuid
from fastapi import HTTPException, status

from src.web.repositories import LibraryRepository, PaperRepository, NewsRepository
from src.web.models import (
    LibraryModel, CreateLibraryRequest, UpdateLibraryRequest,
    LibraryListResponse, LibraryDetailResponse, PaperModel, NewsModel,
    AddPaperToLibraryRequest, AddItemToLibraryRequest
)


class LibraryService:
    """论文库业务逻辑层"""
    
    def __init__(self):
        self.library_repository = LibraryRepository()
        self.paper_repository = PaperRepository()
        self.news_repository = NewsRepository()
    
    async def create_library(self, request: CreateLibraryRequest, username: str) -> LibraryModel:
        """创建论文库"""
        # 检查用户是否已有同名论文库
        existing_library = await self.library_repository.get_user_library_by_name(username, request.name)
        if existing_library:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"论文库名称 '{request.name}' 已存在"
            )
        
        # 创建论文库模型
        now = datetime.now(UTC)
        library = LibraryModel(
            id=str(uuid.uuid4()),
            name=request.name,
            description=request.description,
            username=username,
            is_public=request.is_public,
            created_at=now,
            updated_at=now
        )
        
        # 保存到数据库
        success = await self.library_repository.create_library(library)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="创建论文库失败"
            )
        
        return library
    
    async def get_user_libraries(self, username: str, page: int = 1, page_size: int = 10) -> LibraryListResponse:
        """获取用户的论文库列表"""
        libraries = await self.library_repository.get_user_libraries(username, page, page_size)
        total = await self.library_repository.count_user_libraries(username)
        
        return LibraryListResponse(libraries=libraries, total=total)
    
    async def get_public_libraries(self, page: int = 1, page_size: int = 10) -> LibraryListResponse:
        """获取公开的论文库列表"""
        libraries = await self.library_repository.get_public_libraries(page, page_size)
        total = await self.library_repository.count_public_libraries()
        
        return LibraryListResponse(libraries=libraries, total=total)
    
    async def get_library_detail(self, library_id: str, username: Optional[str] = None) -> LibraryDetailResponse:
        """获取论文库详情"""
        library = await self.library_repository.get_library_by_id(library_id)
        if not library:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="论文库不存在"
            )
        
        # 检查访问权限
        if not library.is_public and library.username != username:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问此论文库"
            )
        
        # 获取收藏库中的所有内容（论文和资讯）
        all_items = await self.library_repository.get_library_items(library_id)
        papers = []
        news_list = []
        
        for row in all_items:
            import json
            item_type = row.get('item_type', 'paper')  # 默认为paper以兼容旧数据
            
            if item_type == 'paper':
                paper = PaperModel(
                    id=row['id'],
                    title=row['title'],
                    summary=row['summary'],
                    content=row['content'],
                    author=row['author'],
                    tags=json.loads(row['tags']) if row['tags'] else [],
                    domain=row['domain'],
                    source=row['source'],
                    publish_time=datetime.fromisoformat(row['publish_time']),
                    cover_image=row['cover_image'],
                    comments=json.loads(row['comments']) if row['comments'] else []
                )
                papers.append(paper)
                
            elif item_type == 'news':
                news = NewsModel(
                    id=row['id'],
                    title=row['title'],
                    summary=row['summary'],
                    content=row['content'],
                    author=row['author'],
                    tags=json.loads(row['tags']) if row['tags'] else [],
                    category=row['category'],
                    source=row['source'],
                    publish_time=datetime.fromisoformat(row['publish_time']),
                    cover_image=row['cover_image'],
                    view_count=row.get('view_count', 0),
                    external_url=row['external_url'],
                    comments=json.loads(row['comments']) if row['comments'] else []
                )
                news_list.append(news)
        
        return LibraryDetailResponse(library=library, papers=papers, news=news_list)
    
    async def update_library(self, library_id: str, request: UpdateLibraryRequest, username: str) -> LibraryModel:
        """更新论文库"""
        library = await self.library_repository.get_library_by_id(library_id)
        if not library:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="论文库不存在"
            )
        
        # 检查权限
        if library.username != username:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权修改此论文库"
            )
        
        # 如果要修改名称，检查是否与用户其他论文库重名
        if request.name and request.name != library.name:
            existing_library = await self.library_repository.get_user_library_by_name(username, request.name)
            if existing_library:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"论文库名称 '{request.name}' 已存在"
                )
        
        # 构建更新数据
        updates = {}
        if request.name is not None:
            updates['name'] = request.name
        if request.description is not None:
            updates['description'] = request.description
        if request.is_public is not None:
            updates['is_public'] = request.is_public
        
        # 执行更新
        success = await self.library_repository.update_library(library_id, updates)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="更新论文库失败"
            )
        
        # 返回更新后的论文库
        return await self.library_repository.get_library_by_id(library_id)
    
    async def delete_library(self, library_id: str, username: str) -> Dict[str, str]:
        """删除论文库"""
        library = await self.library_repository.get_library_by_id(library_id)
        if not library:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="论文库不存在"
            )
        
        # 检查权限
        if library.username != username:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权删除此论文库"
            )
        
        # 执行删除
        success = await self.library_repository.delete_library(library_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="删除论文库失败"
            )
        
        return {"message": "论文库删除成功"}
    
    async def add_paper_to_library(self, library_id: str, request: AddPaperToLibraryRequest, username: str) -> Dict[str, str]:
        """添加论文到论文库"""
        # 检查论文库是否存在且有权限
        library = await self.library_repository.get_library_by_id(library_id)
        if not library:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="论文库不存在"
            )
        
        if library.username != username:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权修改此论文库"
            )
        
        # 检查论文是否存在
        paper = await self.paper_repository.get_paper_by_id(request.paper_id)
        if not paper:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="论文不存在"
            )
        
        # 检查论文是否已在论文库中
        if await self.library_repository.is_paper_in_library(library_id, request.paper_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="论文已在论文库中"
            )
        
        # 添加论文到论文库
        success = await self.library_repository.add_paper_to_library(library_id, request.paper_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="添加论文到论文库失败"
            )
        
        return {"message": "论文添加成功"}
    
    async def remove_paper_from_library(self, library_id: str, paper_id: str, username: str) -> Dict[str, str]:
        """从论文库移除论文"""
        # 检查论文库是否存在且有权限
        library = await self.library_repository.get_library_by_id(library_id)
        if not library:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="论文库不存在"
            )
        
        if library.username != username:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权修改此论文库"
            )
        
        # 检查论文是否在论文库中
        if not await self.library_repository.is_paper_in_library(library_id, paper_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="论文不在此论文库中"
            )
        
        # 从论文库移除论文
        success = await self.library_repository.remove_paper_from_library(library_id, paper_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="从论文库移除论文失败"
            )
        
        return {"message": "论文移除成功"}
    
    async def check_paper_in_libraries(self, paper_id: str, username: str) -> List[str]:
        """检查论文在用户的哪些论文库中"""
        user_libraries = await self.library_repository.get_user_libraries(username, 1, 100)  # 获取所有论文库
        
        library_ids = []
        for library in user_libraries:
            if await self.library_repository.is_paper_in_library(library.id, paper_id):
                library_ids.append(library.id)
        
        return library_ids
    
    # 新的通用收藏方法，支持论文和资讯
    async def add_item_to_library(self, library_id: str, request: AddItemToLibraryRequest, username: str) -> Dict[str, str]:
        """添加内容（论文或资讯）到收藏库"""
        # 检查收藏库是否存在且有权限
        library = await self.library_repository.get_library_by_id(library_id)
        if not library:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="收藏库不存在"
            )
        
        if library.username != username:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权修改此收藏库"
            )
        
        # 检查内容是否存在
        if request.item_type == 'paper':
            item = await self.paper_repository.get_paper_by_id(request.item_id)
            item_name = "论文"
        elif request.item_type == 'news':
            item = await self.news_repository.get_news_by_id(request.item_id)
            item_name = "资讯"
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不支持的内容类型"
            )
        
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{item_name}不存在"
            )
        
        # 检查内容是否已在收藏库中
        if await self.library_repository.is_item_in_library(library_id, request.item_id, request.item_type):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{item_name}已在收藏库中"
            )
        
        # 添加内容到收藏库
        success = await self.library_repository.add_item_to_library(library_id, request.item_id, request.item_type)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"添加{item_name}到收藏库失败"
            )
        
        return {"message": f"{item_name}添加成功"}
    
    async def remove_item_from_library(self, library_id: str, item_id: str, item_type: str, username: str) -> Dict[str, str]:
        """从收藏库移除内容（论文或资讯）"""
        # 检查收藏库是否存在且有权限
        library = await self.library_repository.get_library_by_id(library_id)
        if not library:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="收藏库不存在"
            )
        
        if library.username != username:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权修改此收藏库"
            )
        
        item_name = "论文" if item_type == 'paper' else "资讯"
        
        # 检查内容是否在收藏库中
        if not await self.library_repository.is_item_in_library(library_id, item_id, item_type):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{item_name}不在收藏库中"
            )
        
        # 从收藏库移除内容
        success = await self.library_repository.remove_item_from_library(library_id, item_id, item_type)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"从收藏库移除{item_name}失败"
            )
        
        return {"message": f"{item_name}移除成功"}
    
    async def check_item_in_libraries(self, item_id: str, item_type: str, username: str) -> List[str]:
        """检查内容在用户的哪些收藏库中"""
        return await self.library_repository.get_user_item_libraries(username, item_id, item_type) 