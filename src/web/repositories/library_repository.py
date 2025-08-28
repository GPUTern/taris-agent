"""
论文库Repository
处理论文库相关的数据库操作
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, UTC
import uuid
import json

from .base import BaseRepository
from src.web.models import LibraryModel, LibraryPaperModel, PaperModel


class LibraryRepository(BaseRepository):
    """论文库数据访问层"""
    
    async def create_library(self, library: LibraryModel) -> bool:
        """创建论文库"""
        query = """
        INSERT INTO libraries (id, name, description, username, is_public, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            library.id,
            library.name,
            library.description,
            library.username,
            1 if library.is_public else 0,
            library.created_at.isoformat(),
            library.updated_at.isoformat()
        )
        return await self.execute_insert_update(query, params)
    
    async def get_user_libraries(self, username: str, page: int = 1, page_size: int = 10) -> List[LibraryModel]:
        """获取用户的收藏库列表"""
        offset = (page - 1) * page_size
        query = """
        SELECT 
            l.*,
            COUNT(DISTINCT CASE WHEN lp.paper_id IS NOT NULL THEN lp.paper_id END) as paper_count,
            COUNT(DISTINCT CASE WHEN li.item_type = 'news' THEN li.item_id END) as news_count,
            (COUNT(DISTINCT lp.paper_id) + COUNT(DISTINCT CASE WHEN li.item_type = 'news' THEN li.item_id END)) as total_count
        FROM libraries l
        LEFT JOIN library_papers lp ON l.id = lp.library_id
        LEFT JOIN library_items li ON l.id = li.library_id
        WHERE l.username = ?
        GROUP BY l.id
        ORDER BY l.updated_at DESC
        LIMIT ? OFFSET ?
        """
        params = (username, page_size, offset)
        rows = await self.execute_query(query, params)
        
        libraries = []
        for row in rows:
            library = LibraryModel(
                id=row['id'],
                name=row['name'],
                description=row['description'],
                username=row['username'],
                is_public=bool(row['is_public']),
                created_at=datetime.fromisoformat(row['created_at']),
                updated_at=datetime.fromisoformat(row['updated_at']),
                paper_count=row['paper_count'] or 0,
                news_count=row['news_count'] or 0,
                total_count=row['total_count'] or 0
            )
            libraries.append(library)
        
        return libraries
    
    async def get_public_libraries(self, page: int = 1, page_size: int = 10) -> List[LibraryModel]:
        """获取公开的收藏库列表"""
        offset = (page - 1) * page_size
        query = """
        SELECT 
            l.*,
            COUNT(DISTINCT CASE WHEN lp.paper_id IS NOT NULL THEN lp.paper_id END) as paper_count,
            COUNT(DISTINCT CASE WHEN li.item_type = 'news' THEN li.item_id END) as news_count,
            (COUNT(DISTINCT lp.paper_id) + COUNT(DISTINCT CASE WHEN li.item_type = 'news' THEN li.item_id END)) as total_count,
            u.username
        FROM libraries l
        LEFT JOIN library_papers lp ON l.id = lp.library_id
        LEFT JOIN library_items li ON l.id = li.library_id
        LEFT JOIN users u ON l.username = u.username
        WHERE l.is_public = 1
        GROUP BY l.id
        ORDER BY l.updated_at DESC
        LIMIT ? OFFSET ?
        """
        params = (page_size, offset)
        rows = await self.execute_query(query, params)
        
        libraries = []
        for row in rows:
            library = LibraryModel(
                id=row['id'],
                name=row['name'],
                description=row['description'],
                username=row['username'],
                is_public=True,
                created_at=datetime.fromisoformat(row['created_at']),
                updated_at=datetime.fromisoformat(row['updated_at']),
                paper_count=row['paper_count'] or 0,
                news_count=row['news_count'] or 0,
                total_count=row['total_count'] or 0
            )
            libraries.append(library)
        
        return libraries
    
    async def get_library_by_id(self, library_id: str) -> Optional[LibraryModel]:
        """根据ID获取收藏库"""
        query = """
        SELECT 
            l.*,
            COUNT(DISTINCT CASE WHEN lp.paper_id IS NOT NULL THEN lp.paper_id END) as paper_count,
            COUNT(DISTINCT CASE WHEN li.item_type = 'news' THEN li.item_id END) as news_count,
            (COUNT(DISTINCT lp.paper_id) + COUNT(DISTINCT CASE WHEN li.item_type = 'news' THEN li.item_id END)) as total_count
        FROM libraries l
        LEFT JOIN library_papers lp ON l.id = lp.library_id
        LEFT JOIN library_items li ON l.id = li.library_id
        WHERE l.id = ?
        GROUP BY l.id
        """
        params = (library_id,)
        row = await self.execute_single_query(query, params)
        
        if not row:
            return None
        
        return LibraryModel(
            id=row['id'],
            name=row['name'],
            description=row['description'],
            username=row['username'],
            is_public=bool(row['is_public']),
            created_at=datetime.fromisoformat(row['created_at']),
            updated_at=datetime.fromisoformat(row['updated_at']),
            paper_count=row['paper_count'] or 0,
            news_count=row['news_count'] or 0,
            total_count=row['total_count'] or 0
        )
    
    async def update_library(self, library_id: str, updates: Dict[str, Any]) -> bool:
        """更新论文库"""
        # 构建动态更新查询
        set_clauses = []
        params = []
        
        if 'name' in updates:
            set_clauses.append("name = ?")
            params.append(updates['name'])
        
        if 'description' in updates:
            set_clauses.append("description = ?")
            params.append(updates['description'])
        
        if 'is_public' in updates:
            set_clauses.append("is_public = ?")
            params.append(1 if updates['is_public'] else 0)
        
        set_clauses.append("updated_at = ?")
        params.append(datetime.now(UTC).isoformat())
        params.append(library_id)
        
        query = f"UPDATE libraries SET {', '.join(set_clauses)} WHERE id = ?"
        return await self.execute_insert_update(query, tuple(params))
    
    async def delete_library(self, library_id: str) -> bool:
        """删除论文库"""
        query = "DELETE FROM libraries WHERE id = ?"
        params = (library_id,)
        return await self.execute_insert_update(query, params)
    
    async def add_paper_to_library(self, library_id: str, paper_id: str) -> bool:
        """添加论文到论文库"""
        # 检查是否已存在
        if await self.is_paper_in_library(library_id, paper_id):
            return False  # 已存在，不重复添加
        
        query = """
        INSERT INTO library_papers (library_id, paper_id, added_at)
        VALUES (?, ?, ?)
        """
        params = (library_id, paper_id, datetime.now(UTC).isoformat())
        
        # 添加关联关系
        success = await self.execute_insert_update(query, params)
        
        if success:
            # 更新论文库的 updated_at 时间
            await self.update_library(library_id, {})
        
        return success
    
    async def remove_paper_from_library(self, library_id: str, paper_id: str) -> bool:
        """从论文库移除论文"""
        query = "DELETE FROM library_papers WHERE library_id = ? AND paper_id = ?"
        params = (library_id, paper_id)
        
        success = await self.execute_insert_update(query, params)
        
        if success:
            # 更新论文库的 updated_at 时间
            await self.update_library(library_id, {})
        
        return success
    
    async def is_paper_in_library(self, library_id: str, paper_id: str) -> bool:
        """检查论文是否在论文库中"""
        query = "SELECT 1 FROM library_papers WHERE library_id = ? AND paper_id = ?"
        params = (library_id, paper_id)
        result = await self.execute_single_query(query, params)
        return result is not None
    
    # 新的通用方法，支持论文和资讯
    async def add_item_to_library(self, library_id: str, item_id: str, item_type: str) -> bool:
        """添加内容（论文或资讯）到收藏库"""
        # 检查是否已存在
        if await self.is_item_in_library(library_id, item_id, item_type):
            return False  # 已存在，不重复添加
        
        query = """
        INSERT INTO library_items (library_id, item_id, item_type, added_at)
        VALUES (?, ?, ?, ?)
        """
        params = (library_id, item_id, item_type, datetime.now(UTC).isoformat())
        
        # 添加关联关系
        success = await self.execute_insert_update(query, params)
        
        if success:
            # 同时添加到旧表以保持兼容性（仅论文）
            if item_type == 'paper' and not await self.is_paper_in_library(library_id, item_id):
                await self.add_paper_to_library(library_id, item_id)
            # 更新收藏库的 updated_at 时间
            await self.update_library(library_id, {})
        
        return success
    
    async def remove_item_from_library(self, library_id: str, item_id: str, item_type: str) -> bool:
        """从收藏库移除内容（论文或资讯）"""
        query = "DELETE FROM library_items WHERE library_id = ? AND item_id = ? AND item_type = ?"
        params = (library_id, item_id, item_type)
        
        success = await self.execute_insert_update(query, params)
        
        if success:
            # 同时从旧表移除（仅论文）
            if item_type == 'paper':
                await self.remove_paper_from_library(library_id, item_id)
            # 更新收藏库的 updated_at 时间
            await self.update_library(library_id, {})
        
        return success
    
    async def is_item_in_library(self, library_id: str, item_id: str, item_type: str) -> bool:
        """检查内容是否在收藏库中"""
        query = "SELECT 1 FROM library_items WHERE library_id = ? AND item_id = ? AND item_type = ?"
        params = (library_id, item_id, item_type)
        result = await self.execute_single_query(query, params)
        return result is not None
    
    async def get_user_item_libraries(self, username: str, item_id: str, item_type: str) -> List[str]:
        """获取用户收藏了特定内容的收藏库ID列表"""
        query = """
        SELECT li.library_id
        FROM library_items li
        JOIN libraries l ON li.library_id = l.id
        WHERE l.username = ? AND li.item_id = ? AND li.item_type = ?
        """
        params = (username, item_id, item_type)
        results = await self.execute_query(query, params)
        return [row['library_id'] for row in results]
    
    async def get_library_papers(self, library_id: str, page: int = 1, page_size: int = 10) -> List[Dict[str, Any]]:
        """获取论文库中的论文"""
        offset = (page - 1) * page_size
        query = """
        SELECT p.*, lp.added_at
        FROM library_papers lp
        JOIN papers p ON lp.paper_id = p.id
        WHERE lp.library_id = ?
        ORDER BY lp.added_at DESC
        LIMIT ? OFFSET ?
        """
        params = (library_id, page_size, offset)
        return await self.execute_query(query, params)
    
    async def get_library_items(self, library_id: str) -> List[Dict[str, Any]]:
        """获取收藏库中的所有内容（论文和资讯）"""
        # 获取新表中的所有内容
        items_query = """
        SELECT li.item_id, li.item_type, li.added_at
        FROM library_items li
        WHERE li.library_id = ?
        ORDER BY li.added_at DESC
        """
        item_rows = await self.execute_query(items_query, (library_id,))
        
        all_items = []
        
        for row in item_rows:
            item_id = row['item_id']
            item_type = row['item_type']
            added_at = row['added_at']
            
            if item_type == 'paper':
                # 获取论文详情
                paper_query = "SELECT * FROM papers WHERE id = ?"
                paper_data = await self.execute_single_query(paper_query, (item_id,))
                if paper_data:
                    item_dict = dict(paper_data)
                    item_dict['item_type'] = 'paper'
                    item_dict['added_at'] = added_at
                    all_items.append(item_dict)
                    
            elif item_type == 'news':
                # 获取资讯详情
                news_query = "SELECT * FROM news WHERE id = ?"
                news_data = await self.execute_single_query(news_query, (item_id,))
                if news_data:
                    item_dict = dict(news_data)
                    item_dict['item_type'] = 'news'
                    item_dict['added_at'] = added_at
                    all_items.append(item_dict)
        
        # 如果新表没有数据，回退到旧表（向后兼容）
        if not all_items:
            legacy_papers = await self.get_library_papers(library_id, 1, 1000)  # 获取所有论文
            for paper in legacy_papers:
                paper_dict = dict(paper)
                paper_dict['item_type'] = 'paper'
                all_items.append(paper_dict)
        
        return all_items

    async def count_user_libraries(self, username: str) -> int:
        """统计用户论文库数量"""
        query = "SELECT COUNT(*) FROM libraries WHERE username = ?"
        params = (username,)
        return await self.execute_count(query, params)
    
    async def count_public_libraries(self) -> int:
        """统计公开论文库数量"""
        query = "SELECT COUNT(*) FROM libraries WHERE is_public = 1"
        return await self.execute_count(query)
    
    async def count_library_papers(self, library_id: str) -> int:
        """统计论文库中的论文数量"""
        query = "SELECT COUNT(*) FROM library_papers WHERE library_id = ?"
        params = (library_id,)
        return await self.execute_count(query, params)
    
    async def get_user_library_by_name(self, username: str, name: str) -> Optional[LibraryModel]:
        """根据用户名和名称获取论文库"""
        query = """
        SELECT l.*, COUNT(lp.paper_id) as paper_count
        FROM libraries l
        LEFT JOIN library_papers lp ON l.id = lp.library_id
        WHERE l.username = ? AND l.name = ?
        GROUP BY l.id
        """
        params = (username, name)
        row = await self.execute_single_query(query, params)
        
        if not row:
            return None
        
        return LibraryModel(
            id=row['id'],
            name=row['name'],
            description=row['description'],
            username=row['username'],
            is_public=bool(row['is_public']),
            created_at=datetime.fromisoformat(row['created_at']),
            updated_at=datetime.fromisoformat(row['updated_at']),
            paper_count=row['paper_count']
        ) 