"""
数据库连接工具类
"""
import sqlite3
import aiosqlite
from src.web.config.settings import DATABASE_PATH


class DatabaseConnection:
    """数据库连接管理"""
    
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
    
    async def get_connection(self):
        """获取异步数据库连接"""
        return aiosqlite.connect(self.db_path)
    
    async def initialize_tables(self):
        """初始化数据库表结构"""
        async with aiosqlite.connect(self.db_path) as db:
            # 创建用户表
            await db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    email TEXT NOT NULL,
                    hashed_password TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'user',
                    created_at TEXT NOT NULL
                )
            ''')
            
            # 创建论文表
            await db.execute('''
                CREATE TABLE IF NOT EXISTS papers (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    content TEXT,
                    author TEXT NOT NULL,
                    tags TEXT NOT NULL,  -- JSON array
                    domain TEXT NOT NULL,
                    source TEXT NOT NULL,
                    publish_time TEXT NOT NULL,
                    cover_image TEXT,
                    comments TEXT DEFAULT '[]'  -- JSON array
                )
            ''')
            
            # 创建资讯表
            await db.execute('''
                CREATE TABLE IF NOT EXISTS news (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    content TEXT,
                    author TEXT NOT NULL,
                    tags TEXT NOT NULL,  -- JSON array
                    category TEXT NOT NULL,
                    source TEXT NOT NULL,
                    publish_time TEXT NOT NULL,
                    cover_image TEXT,
                    view_count INTEGER DEFAULT 0,
                    external_url TEXT,
                    comments TEXT DEFAULT '[]'  -- JSON array
                )
            ''')
            
            # 创建论文库表
            await db.execute('''
                CREATE TABLE IF NOT EXISTS libraries (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    username TEXT NOT NULL,
                    is_public INTEGER DEFAULT 0,  -- 0: 私有, 1: 公开
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (username) REFERENCES users (username) ON DELETE CASCADE
                )
            ''')
            
            # 创建论文库-论文关联表（保留兼容性）
            await db.execute('''
                CREATE TABLE IF NOT EXISTS library_papers (
                    library_id TEXT NOT NULL,
                    paper_id TEXT NOT NULL,
                    added_at TEXT NOT NULL,
                    PRIMARY KEY (library_id, paper_id),
                    FOREIGN KEY (library_id) REFERENCES libraries (id) ON DELETE CASCADE,
                    FOREIGN KEY (paper_id) REFERENCES papers (id) ON DELETE CASCADE
                )
            ''')
            
            # 创建收藏库-内容关联表（新的通用表）
            await db.execute('''
                CREATE TABLE IF NOT EXISTS library_items (
                    library_id TEXT NOT NULL,
                    item_id TEXT NOT NULL,
                    item_type TEXT NOT NULL,  -- 'paper' or 'news'
                    added_at TEXT NOT NULL,
                    PRIMARY KEY (library_id, item_id, item_type),
                    FOREIGN KEY (library_id) REFERENCES libraries (id) ON DELETE CASCADE
                )
            ''')
            
            # 为论文库表创建索引
            await db.execute('CREATE INDEX IF NOT EXISTS idx_libraries_username ON libraries (username)')
            await db.execute('CREATE INDEX IF NOT EXISTS idx_libraries_public ON libraries (is_public)')
            
            # 为关联表创建索引
            await db.execute('CREATE INDEX IF NOT EXISTS idx_library_papers_library ON library_papers (library_id)')
            await db.execute('CREATE INDEX IF NOT EXISTS idx_library_papers_paper ON library_papers (paper_id)')
            
            # 为新的通用关联表创建索引
            await db.execute('CREATE INDEX IF NOT EXISTS idx_library_items_library ON library_items (library_id)')
            await db.execute('CREATE INDEX IF NOT EXISTS idx_library_items_item ON library_items (item_id, item_type)')
            await db.execute('CREATE INDEX IF NOT EXISTS idx_library_items_type ON library_items (item_type)')
            
            await db.commit()


# 全局数据库连接实例
db_connection = DatabaseConnection() 