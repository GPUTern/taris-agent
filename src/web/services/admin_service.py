"""
管理员服务
处理管理员相关的业务逻辑
"""
from datetime import datetime
from typing import Dict
from fastapi import HTTPException, status

from src.web.models import (
    UserModel, UserRole, CreateUserRequest, AdminUpdateUserRequest,
    UpdateUserRoleRequest, UserInfoResponse, UserListResponse
)
from src.web.repositories import UserRepository, PaperRepository
from src.web.services.auth_service import AuthService


class AdminService:
    """管理员服务"""
    
    def __init__(self):
        self.user_repo = UserRepository()
        self.paper_repo = PaperRepository()
        self.auth_service = AuthService()
    
    async def get_users(self, page: int = 1, page_size: int = 10) -> UserListResponse:
        """获取用户列表（仅超级管理员）"""
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
            users, total = await self.user_repo.get_users_paginated(page=page, page_size=page_size)
            
            # 移除敏感信息
            for user in users:
                user.hashed_password = "***"
            
            return UserListResponse(users=users, total=total)
        except Exception as e:
            print(f"获取用户列表错误: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="获取用户列表失败，请稍后重试"
            )
    
    async def create_user(self, user_data: CreateUserRequest) -> UserInfoResponse:
        """创建用户（仅超级管理员）"""
        # 检查用户名是否已存在
        if await self.user_repo.user_exists(user_data.username.strip()):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在，请选择其他用户名"
            )
        
        # 检查邮箱是否已存在
        if await self.user_repo.email_exists(user_data.email.strip()):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被使用，请选择其他邮箱"
            )
        
        try:
            # 创建新用户
            hashed_password = self.auth_service.get_password_hash(user_data.password)
            user = UserModel(
                username=user_data.username.strip(),
                email=user_data.email.strip(),
                hashed_password=hashed_password,
                role=user_data.role,
                created_at=datetime.utcnow()
            )
            
            success = await self.user_repo.create_user(user)
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="用户创建失败，请稍后重试"
                )
            
            return UserInfoResponse(
                username=user.username,
                email=user.email,
                role=user.role,
                created_at=user.created_at
            )
        except HTTPException:
            raise
        except Exception as e:
            print(f"创建用户错误: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="创建用户失败，请稍后重试"
            )
    
    async def admin_update_user(self, username: str, update_data: AdminUpdateUserRequest) -> UserInfoResponse:
        """管理员编辑用户信息（仅超级管理员）"""
        # 检查用户是否存在
        existing_user = await self.user_repo.get_user_by_username(username)
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        try:
            # 检查邮箱是否被其他用户使用
            if update_data.email and await self.user_repo.email_exists(update_data.email.strip(), username):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="邮箱已被其他用户使用"
                )
            
            # 更新邮箱和密码
            email = update_data.email.strip() if update_data.email else None
            hashed_password = self.auth_service.get_password_hash(update_data.reset_password) if update_data.reset_password else None
            
            if email or hashed_password:
                await self.user_repo.update_user_info(username, email, hashed_password)
            
            # 更新角色
            if update_data.role and update_data.role != existing_user.role:
                await self.user_repo.update_user_role(username, update_data.role)
            
            # 获取更新后的用户信息
            updated_user = await self.user_repo.get_user_by_username(username)
            return UserInfoResponse(
                username=updated_user.username,
                email=updated_user.email,
                role=updated_user.role,
                created_at=updated_user.created_at
            )
        except HTTPException:
            raise
        except Exception as e:
            print(f"编辑用户错误: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="编辑用户失败，请稍后重试"
            )
    
    async def update_user_role(self, username: str, role_data: UpdateUserRoleRequest, 
                              current_admin: str) -> dict:
        """更新用户角色（仅超级管理员）"""
        # 防止管理员修改自己的角色
        if username == current_admin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能修改自己的角色"
            )
        
        try:
            success = await self.user_repo.update_user_role(username, role_data.role)
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="用户不存在"
                )
            
            return {"message": f"用户 {username} 角色已更新为 {role_data.role}"}
        except HTTPException:
            raise
        except Exception as e:
            print(f"更新用户角色错误: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="更新用户角色失败，请稍后重试"
            )
    
    async def delete_user(self, username: str, current_admin: str) -> dict:
        """删除用户（仅超级管理员）"""
        # 防止管理员删除自己
        if username == current_admin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能删除自己的账户"
            )
        
        try:
            success = await self.user_repo.delete_user(username)
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="用户不存在"
                )
            
            return {"message": f"用户 {username} 已删除"}
        except HTTPException:
            raise
        except Exception as e:
            print(f"删除用户错误: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="删除用户失败，请稍后重试"
            )
    
    async def get_stats(self) -> Dict:
        """获取管理员统计信息"""
        try:
            # 获取基础统计
            total_users = await self.user_repo.get_user_count()
            total_papers = await self.paper_repo.get_paper_count()
            
            # 获取角色统计
            admin_users = await self.user_repo.get_users_by_role_count(['super_admin', 'paper_admin'])
            regular_users = await self.user_repo.get_users_by_role_count(['user'])
            
            # 获取最近的论文和用户
            recent_papers = await self.paper_repo.get_recent_papers(limit=5)
            recent_users = await self.user_repo.get_recent_users(limit=5)
            
            return {
                "total_papers": total_papers,
                "total_users": total_users,
                "admin_users": admin_users,
                "regular_users": regular_users,
                "recent_papers": recent_papers,
                "recent_users": recent_users
            }
        except Exception as e:
            print(f"获取统计信息错误: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="获取统计信息失败，请稍后重试"
            ) 