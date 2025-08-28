"""
论文数据访问Repository
"""
import json
import uuid
from datetime import UTC, datetime, timedelta
from typing import List, Optional, Tuple
from src.web.models.domain import PaperModel, CommentModel
from src.web.models.dto import CreatePaperRequest, UpdatePaperRequest
from .base import BaseRepository


class PaperRepository(BaseRepository):
    """论文数据访问层"""
    
    async def create_paper(self, paper_data: CreatePaperRequest) -> PaperModel:
        """创建论文"""
        paper_id = str(uuid.uuid4())
        now = datetime.now(UTC)
        
        paper = PaperModel(
            id=paper_id,
            title=paper_data.title,
            summary=paper_data.summary,
            content=paper_data.content,
            author=paper_data.author,
            tags=paper_data.tags,
            domain=paper_data.domain,
            source=paper_data.source,
            publish_time=now,
            cover_image=paper_data.cover_image,
            comments=[]
        )
        
        await self._create_paper_internal(paper)
        return paper
    
    async def _create_paper_internal(self, paper: PaperModel):
        """内部创建论文方法"""
        # 序列化评论数据
        comments_data = []
        for comment in paper.comments:
            comment_dict = comment.dict()
            if 'time' in comment_dict and isinstance(comment_dict['time'], datetime):
                comment_dict['time'] = comment_dict['time'].isoformat()
            comments_data.append(comment_dict)
        
        query = '''
            INSERT INTO papers (
                id, title, summary, content, author, tags, domain,
                source, publish_time, cover_image, comments
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        params = (
            paper.id, paper.title, paper.summary, paper.content,
            paper.author, json.dumps(paper.tags), paper.domain,
            paper.source, paper.publish_time.isoformat(),
            paper.cover_image, json.dumps(comments_data)
        )
        
        await self.execute_insert_update(query, params)
    
    async def get_paper_by_id(self, paper_id: str) -> Optional[PaperModel]:
        """根据ID获取论文"""
        query = "SELECT * FROM papers WHERE id = ?"
        result = await self.execute_single_query(query, (paper_id,))
        
        if not result:
            return None
        
        return self._build_paper_from_result(result)
    
    async def get_papers(self, 
                        tag: Optional[str] = None,
                        domain: Optional[str] = None,
                        sort: str = "newest",
                        date_range: Optional[str] = None,
                        search: Optional[str] = None,
                        page: int = 1,
                        page_size: int = 10) -> Tuple[List[PaperModel], int]:
        """获取论文列表"""
        
        # 构建查询条件
        where_conditions = []
        params = []
        
        if tag:
            # 支持JSON数组中的标签搜索，包括Unicode转义和普通格式
            where_conditions.append("(tags LIKE ? OR tags LIKE ?)")
            # 搜索普通格式和Unicode转义格式
            params.extend([f'%"{tag}"%', f'%{json.dumps(tag, ensure_ascii=True)}%'])
        
        if domain:
            where_conditions.append("domain = ?")
            params.append(domain)
        
        if search:
            # 搜索标题、作者、摘要、内容
            search_pattern = f"%{search}%"
            where_conditions.append("(title LIKE ? OR author LIKE ? OR summary LIKE ? OR content LIKE ?)")
            params.extend([search_pattern, search_pattern, search_pattern, search_pattern])
        
        if date_range and date_range != "all":
            cutoff = self._get_date_cutoff(date_range)
            if cutoff:
                where_conditions.append("publish_time >= ?")
                params.append(cutoff.isoformat())
        
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        
        # 排序
        order_clause = self._get_order_clause(sort)
        
        # 获取总数
        count_query = f"SELECT COUNT(*) FROM papers WHERE {where_clause}"
        total = await self.execute_count(count_query, tuple(params))
        
        # 获取分页数据
        offset = (page - 1) * page_size
        query = f'''
            SELECT * FROM papers WHERE {where_clause} {order_clause}
            LIMIT ? OFFSET ?
        '''
        results = await self.execute_query(query, tuple(params + [page_size, offset]))
        
        papers = [self._build_paper_from_result(result) for result in results]
        
        return papers, total
    
    async def update_paper(self, paper_id: str, paper_data: UpdatePaperRequest) -> Optional[PaperModel]:
        """更新论文"""
        # 检查论文是否存在
        existing_paper = await self.get_paper_by_id(paper_id)
        if not existing_paper:
            return None
        
        # 构建更新参数
        set_clauses = []
        params = []
        
        if paper_data.title is not None:
            set_clauses.append("title = ?")
            params.append(paper_data.title)
        
        if paper_data.summary is not None:
            set_clauses.append("summary = ?")
            params.append(paper_data.summary)
        
        if paper_data.content is not None:
            set_clauses.append("content = ?")
            params.append(paper_data.content)
        
        if paper_data.author is not None:
            set_clauses.append("author = ?")
            params.append(paper_data.author)
        
        if paper_data.tags is not None:
            set_clauses.append("tags = ?")
            params.append(json.dumps(paper_data.tags))
        
        if paper_data.domain is not None:
            set_clauses.append("domain = ?")
            params.append(paper_data.domain)
        
        if paper_data.source is not None:
            set_clauses.append("source = ?")
            params.append(paper_data.source)
        
        if paper_data.cover_image is not None:
            set_clauses.append("cover_image = ?")
            params.append(paper_data.cover_image)
        
        if not set_clauses:
            return existing_paper  # 没有要更新的内容
        
        query = f"UPDATE papers SET {', '.join(set_clauses)} WHERE id = ?"
        params.append(paper_id)
        
        success = await self.execute_insert_update(query, tuple(params))
        if success:
            return await self.get_paper_by_id(paper_id)
        return None
    
    async def delete_paper(self, paper_id: str) -> bool:
        """删除论文"""
        query = "DELETE FROM papers WHERE id = ?"
        return await self.execute_insert_update(query, (paper_id,))
    
    async def get_all_tags(self) -> List[str]:
        """获取所有标签"""
        query = "SELECT tags FROM papers"
        results = await self.execute_query(query)
        
        all_tags = set()
        for result in results:
            tags = json.loads(result['tags'])
            all_tags.update(tags)
        
        return sorted(list(all_tags))
    
    async def get_all_domains(self) -> List[str]:
        """获取所有领域"""
        query = "SELECT DISTINCT domain FROM papers ORDER BY domain"
        results = await self.execute_query(query)
        
        return [result['domain'] for result in results]
    
    async def get_paper_count(self) -> int:
        """获取论文总数"""
        return await self.execute_count("SELECT COUNT(*) FROM papers")
    
    async def get_recent_papers(self, limit: int = 5) -> List[dict]:
        """获取最近的论文"""
        query = "SELECT id, title, author, publish_time FROM papers ORDER BY publish_time DESC LIMIT ?"
        results = await self.execute_query(query, (limit,))
        
        papers = []
        for result in results:
            papers.append({
                'id': result['id'],
                'title': result['title'],
                'author': result['author'],
                'publish_time': result['publish_time']
            })
        
        return papers
    
    def _build_paper_from_result(self, result: dict) -> PaperModel:
        """从查询结果构建论文模型"""
        comments_data = json.loads(result['comments']) if result['comments'] else []
        comments = []
        for comment_data in comments_data:
            if 'time' in comment_data and isinstance(comment_data['time'], str):
                comment_data['time'] = datetime.fromisoformat(comment_data['time'])
            comments.append(CommentModel(**comment_data))
        
        return PaperModel(
            id=result['id'],
            title=result['title'],
            summary=result['summary'],
            content=result['content'],
            author=result['author'],
            tags=json.loads(result['tags']),
            domain=result['domain'],
            source=result['source'],
            publish_time=datetime.fromisoformat(result['publish_time']),
            cover_image=result['cover_image'],
            comments=comments
        )
    
    def _get_date_cutoff(self, date_range: str) -> Optional[datetime]:
        """根据日期范围获取截止日期"""
        now = datetime.now()
        if date_range == "1d":
            return now - timedelta(days=1)
        elif date_range == "3d":
            return now - timedelta(days=3)
        elif date_range == "7d":
            return now - timedelta(days=7)
        elif date_range == "30d":
            return now - timedelta(days=30)
        elif date_range == "180d":
            return now - timedelta(days=180)
        elif date_range == "1y":
            return now - timedelta(days=365)
        return None
    
    def _get_order_clause(self, sort: str) -> str:
        """根据排序参数获取ORDER BY子句"""
        if sort == "newest":
            return "ORDER BY publish_time DESC"
        elif sort == "hot":
            return "ORDER BY LENGTH(comments) - LENGTH(REPLACE(comments, '},{', '')) DESC"
        else:
            return "ORDER BY publish_time DESC" 