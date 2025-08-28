"""
用户数据访问Repository
"""
from datetime import datetime
from typing import List, Optional, Tuple
from src.web.models.domain import UserModel, UserRole
from .base import BaseRepository


class UserRepository(BaseRepository):
    """用户数据访问层"""
    
    async def create_user(self, user: UserModel) -> bool:
        """创建用户"""
        query = '''
            INSERT INTO users (username, email, hashed_password, role, created_at)
            VALUES (?, ?, ?, ?, ?)
        '''
        params = (
            user.username,
            user.email,
            user.hashed_password,
            user.role.value,
            user.created_at.isoformat()
        )
        return await self.execute_insert_update(query, params)
    
    async def get_user_by_username(self, username: str) -> Optional[UserModel]:
        """根据用户名获取用户"""
        query = "SELECT * FROM users WHERE username = ?"
        result = await self.execute_single_query(query, (username,))
        
        if not result:
            return None
        
        return UserModel(
            username=result['username'],
            email=result['email'],
            hashed_password=result['hashed_password'],
            role=UserRole(result['role']),
            created_at=datetime.fromisoformat(result['created_at'])
        )
    
    async def user_exists(self, username: str) -> bool:
        """检查用户是否存在"""
        query = "SELECT COUNT(*) FROM users WHERE username = ?"
        count = await self.execute_count(query, (username,))
        return count > 0
    
    async def email_exists(self, email: str, exclude_username: Optional[str] = None) -> bool:
        """检查邮箱是否已存在"""
        if exclude_username:
            query = "SELECT COUNT(*) FROM users WHERE email = ? AND username != ?"
            count = await self.execute_count(query, (email, exclude_username))
        else:
            query = "SELECT COUNT(*) FROM users WHERE email = ?"
            count = await self.execute_count(query, (email,))
        return count > 0
    
    async def get_users_paginated(self, page: int = 1, page_size: int = 10) -> Tuple[List[UserModel], int]:
        """分页获取用户列表"""
        # 获取总数
        total = await self.execute_count("SELECT COUNT(*) FROM users")
        
        # 获取分页数据
        offset = (page - 1) * page_size
        query = "SELECT * FROM users ORDER BY created_at DESC LIMIT ? OFFSET ?"
        results = await self.execute_query(query, (page_size, offset))
        
        users = []
        for result in results:
            user = UserModel(
                username=result['username'],
                email=result['email'],
                hashed_password=result['hashed_password'],
                role=UserRole(result['role']),
                created_at=datetime.fromisoformat(result['created_at'])
            )
            users.append(user)
        
        return users, total
    
    async def update_user_role(self, username: str, role: UserRole) -> bool:
        """更新用户角色"""
        query = "UPDATE users SET role = ? WHERE username = ?"
        return await self.execute_insert_update(query, (role.value, username))
    
    async def update_user_info(self, username: str, email: Optional[str] = None, 
                              hashed_password: Optional[str] = None) -> bool:
        """更新用户信息"""
        set_clauses = []
        params = []
        
        if email:
            set_clauses.append("email = ?")
            params.append(email)
        
        if hashed_password:
            set_clauses.append("hashed_password = ?")
            params.append(hashed_password)
        
        if not set_clauses:
            return True  # 没有要更新的内容
        
        query = f"UPDATE users SET {', '.join(set_clauses)} WHERE username = ?"
        params.append(username)
        
        return await self.execute_insert_update(query, tuple(params))
    
    async def delete_user(self, username: str) -> bool:
        """删除用户"""
        query = "DELETE FROM users WHERE username = ?"
        return await self.execute_insert_update(query, (username,))
    
    async def get_user_count(self) -> int:
        """获取用户总数"""
        return await self.execute_count("SELECT COUNT(*) FROM users")
    
    async def get_users_by_role_count(self, roles: List[str]) -> int:
        """获取指定角色的用户数量"""
        placeholders = ','.join(['?' for _ in roles])
        query = f"SELECT COUNT(*) FROM users WHERE role IN ({placeholders})"
        return await self.execute_count(query, tuple(roles))
    
    async def get_recent_users(self, limit: int = 5) -> List[dict]:
        """获取最近的用户"""
        query = "SELECT username, email, role, created_at FROM users ORDER BY created_at DESC LIMIT ?"
        results = await self.execute_query(query, (limit,))
        
        users = []
        for result in results:
            users.append({
                'username': result['username'],
                'email': result['email'],
                'role': result['role'],
                'created_at': result['created_at']
            })
        
        return users 