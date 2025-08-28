"""
基础Repository类
提供通用的数据访问方法
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, Dict, Any
from src.web.utils.database import db_connection



class BaseRepository(ABC):
    """Repository基类"""
    
    def __init__(self):
        self.db_connection = db_connection
    
    async def get_connection(self):
        """获取数据库连接"""
        return await self.db_connection.get_connection()
    
    async def execute_query(self, query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        """执行查询，返回字典列表"""
        async with await self.get_connection() as db:
            cursor = await db.execute(query, params)
            rows = await cursor.fetchall()
            
            # 获取列名
            columns = [description[0] for description in cursor.description]
            
            # 转换为字典列表
            result = []
            for row in rows:
                result.append(dict(zip(columns, row)))
            
            return result
    
    async def execute_single_query(self, query: str, params: Tuple = ()) -> Optional[Dict[str, Any]]:
        """执行查询，返回单个结果"""
        results = await self.execute_query(query, params)
        return results[0] if results else None
    
    async def execute_insert_update(self, query: str, params: Tuple = ()) -> bool:
        """执行插入或更新操作"""
        try:
            async with await self.get_connection() as db:
                await db.execute(query, params)
                await db.commit()
                return True
        except Exception as e:
            print(f"数据库操作错误: {e}")
            return False
    
    async def execute_count(self, query: str, params: Tuple = ()) -> int:
        """执行计数查询"""
        async with await self.get_connection() as db:
            cursor = await db.execute(query, params)
            result = await cursor.fetchone()
            return result[0] if result else 0 