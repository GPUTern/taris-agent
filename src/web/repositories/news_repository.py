"""
资讯数据访问Repository
"""
import json
import uuid
from datetime import UTC, datetime, timedelta
from typing import List, Optional, Tuple
from src.web.models.domain import NewsModel, CommentModel
from src.web.models.dto import CreateNewsRequest, UpdateNewsRequest
from .base import BaseRepository


class NewsRepository(BaseRepository):
    """资讯数据访问层"""
    
    async def create_news(self, news_data: CreateNewsRequest) -> NewsModel:
        """创建资讯"""
        news_id = str(uuid.uuid4())
        now = datetime.now(UTC)
        
        news = NewsModel(
            id=news_id,
            title=news_data.title,
            summary=news_data.summary,
            content=news_data.content,
            author=news_data.author,
            tags=news_data.tags,
            category=news_data.category,
            source=news_data.source,
            publish_time=now,
            cover_image=news_data.cover_image,
            view_count=0,
            external_url=news_data.external_url,
            comments=[]
        )
        
        await self._create_news_internal(news)
        return news
    
    async def _create_news_internal(self, news: NewsModel):
        """内部创建资讯方法"""
        # 序列化评论数据
        comments_data = []
        for comment in news.comments:
            comment_dict = comment.dict()
            if 'time' in comment_dict and isinstance(comment_dict['time'], datetime):
                comment_dict['time'] = comment_dict['time'].isoformat()
            comments_data.append(comment_dict)
        
        query = '''
            INSERT INTO news (
                id, title, summary, content, author, tags, category,
                source, publish_time, cover_image, view_count, external_url, comments
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        params = (
            news.id, news.title, news.summary, news.content,
            news.author, json.dumps(news.tags), news.category,
            news.source, news.publish_time.isoformat(),
            news.cover_image, news.view_count, news.external_url, json.dumps(comments_data)
        )
        
        await self.execute_insert_update(query, params)
    
    async def get_news_by_id(self, news_id: str) -> Optional[NewsModel]:
        """根据ID获取资讯"""
        query = "SELECT * FROM news WHERE id = ?"
        result = await self.execute_single_query(query, (news_id,))
        
        if not result:
            return None
        
        return self._build_news_from_result(result)
    
    async def get_news_list(self, 
                           tag: Optional[str] = None,
                           category: Optional[str] = None,
                           sort: str = "newest",
                           date_range: Optional[str] = None,
                           search: Optional[str] = None,
                           page: int = 1,
                           page_size: int = 10) -> Tuple[List[NewsModel], int]:
        """获取资讯列表"""
        
        # 构建查询条件
        where_conditions = []
        params = []
        
        if tag:
            # 支持JSON数组中的标签搜索，包括Unicode转义和普通格式
            where_conditions.append("(tags LIKE ? OR tags LIKE ?)")
            # 搜索普通格式和Unicode转义格式
            params.extend([f'%"{tag}"%', f'%{json.dumps(tag, ensure_ascii=True)}%'])
        
        if category:
            where_conditions.append("category = ?")
            params.append(category)
        
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
        count_query = f"SELECT COUNT(*) FROM news WHERE {where_clause}"
        total = await self.execute_count(count_query, tuple(params))
        
        # 获取分页数据
        offset = (page - 1) * page_size
        query = f'''
            SELECT * FROM news WHERE {where_clause} {order_clause}
            LIMIT ? OFFSET ?
        '''
        results = await self.execute_query(query, tuple(params + [page_size, offset]))
        
        news_list = [self._build_news_from_result(result) for result in results]
        
        return news_list, total
    
    async def update_news(self, news_id: str, news_data: UpdateNewsRequest) -> Optional[NewsModel]:
        """更新资讯"""
        # 检查资讯是否存在
        existing_news = await self.get_news_by_id(news_id)
        if not existing_news:
            return None
        
        # 构建更新参数
        set_clauses = []
        params = []
        
        if news_data.title is not None:
            set_clauses.append("title = ?")
            params.append(news_data.title)
        
        if news_data.summary is not None:
            set_clauses.append("summary = ?")
            params.append(news_data.summary)
        
        if news_data.content is not None:
            set_clauses.append("content = ?")
            params.append(news_data.content)
        
        if news_data.author is not None:
            set_clauses.append("author = ?")
            params.append(news_data.author)
        
        if news_data.tags is not None:
            set_clauses.append("tags = ?")
            params.append(json.dumps(news_data.tags))
        
        if news_data.category is not None:
            set_clauses.append("category = ?")
            params.append(news_data.category)
        
        if news_data.source is not None:
            set_clauses.append("source = ?")
            params.append(news_data.source)
        
        if news_data.cover_image is not None:
            set_clauses.append("cover_image = ?")
            params.append(news_data.cover_image)
        
        if news_data.external_url is not None:
            set_clauses.append("external_url = ?")
            params.append(news_data.external_url)
        
        if not set_clauses:
            return existing_news  # 没有要更新的内容
        
        query = f"UPDATE news SET {', '.join(set_clauses)} WHERE id = ?"
        params.append(news_id)
        
        success = await self.execute_insert_update(query, tuple(params))
        if success:
            return await self.get_news_by_id(news_id)
        return None
    
    async def delete_news(self, news_id: str) -> bool:
        """删除资讯"""
        query = "DELETE FROM news WHERE id = ?"
        return await self.execute_insert_update(query, (news_id,))
    
    async def increment_view_count(self, news_id: str) -> bool:
        """增加浏览次数"""
        query = "UPDATE news SET view_count = view_count + 1 WHERE id = ?"
        return await self.execute_insert_update(query, (news_id,))
    
    async def get_all_tags(self) -> List[str]:
        """获取所有标签"""
        query = "SELECT DISTINCT tags FROM news"
        results = await self.execute_query(query)
        
        all_tags = set()
        for result in results:
            if result['tags']:
                tags = json.loads(result['tags'])
                all_tags.update(tags)
        
        return sorted(list(all_tags))
    
    async def get_all_categories(self) -> List[str]:
        """获取所有分类"""
        query = "SELECT DISTINCT category FROM news WHERE category IS NOT NULL AND category != ''"
        results = await self.execute_query(query)
        return [result['category'] for result in results]
    
    def _build_news_from_result(self, result: dict) -> NewsModel:
        """从查询结果构建资讯模型"""
        comments_data = json.loads(result['comments']) if result['comments'] else []
        comments = []
        for comment_data in comments_data:
            if 'time' in comment_data and isinstance(comment_data['time'], str):
                comment_data['time'] = datetime.fromisoformat(comment_data['time'])
            comments.append(CommentModel(**comment_data))
        
        return NewsModel(
            id=result['id'],
            title=result['title'],
            summary=result['summary'],
            content=result['content'],
            author=result['author'],
            tags=json.loads(result['tags']),
            category=result['category'],
            source=result['source'],
            publish_time=datetime.fromisoformat(result['publish_time']),
            cover_image=result['cover_image'],
            view_count=result.get('view_count', 0),
            external_url=result['external_url'],
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
            return "ORDER BY view_count DESC, publish_time DESC"
        elif sort == "popular":
            return "ORDER BY LENGTH(comments) - LENGTH(REPLACE(comments, '},{', '')) DESC"
        else:
            return "ORDER BY publish_time DESC" 