"""认证服务
处理用户认证、注册、权限验证等业务逻辑.
"""  # noqa: D205
from datetime import UTC, datetime, timedelta
from typing import Optional

from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext

from src.web.config.settings import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
from src.web.models import (
    AuthResponse,
    LoginRequest,
    RegisterRequest,
    UserInfoResponse,
    UserModel,
    UserRole,
)
from src.web.repositories import UserRepository


class AuthService:
    """认证服务"""
    
    def __init__(self):
        self.user_repo = UserRepository()
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    async def authenticate_user(self, username: str, password: str) -> Optional[UserModel]:
        """验证用户身份"""
        user = await self.user_repo.get_user_by_username(username)
        if not user:
            return None
        
        if not self.verify_password(password, user.hashed_password):
            return None
        
        return user
    
    async def login(self, login_data: LoginRequest) -> AuthResponse:
        """用户登录"""
        user = await self.authenticate_user(login_data.username, login_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )
        
        access_token = self.create_access_token(data={"sub": user.username})
        
        return AuthResponse(
            token=access_token,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # 转换为秒
            user_role=user.role
        )
    
    async def register(self, register_data: RegisterRequest) -> UserInfoResponse:
        """用户注册"""
        # 验证密码确认
        if register_data.password != register_data.confirmPassword:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="两次输入的密码不一致"
            )
        
        # 检查用户名是否已存在
        if await self.user_repo.user_exists(register_data.username.strip()):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在，请选择其他用户名"
            )
        
        # 检查邮箱是否已存在
        if await self.user_repo.email_exists(register_data.email.strip()):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被使用，请选择其他邮箱"
            )
        
        # 创建新用户
        hashed_password = self.get_password_hash(register_data.password)
        user = UserModel(
            username=register_data.username.strip(),
            email=register_data.email.strip(),
            hashed_password=hashed_password,
            role=UserRole.USER,
            created_at=datetime.now(UTC)
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
    
    async def get_user_info(self, username: str) -> Optional[UserInfoResponse]:
        """获取用户信息"""
        user = await self.user_repo.get_user_by_username(username)
        if not user:
            return None
        
        return UserInfoResponse(
            username=user.username,
            email=user.email,
            role=user.role,
            created_at=user.created_at
        )
    
    async def update_user_profile(self, username: str, email: Optional[str] = None, 
                                 current_password: Optional[str] = None,
                                 new_password: Optional[str] = None) -> UserInfoResponse:
        """更新用户资料"""
        user = await self.user_repo.get_user_by_username(username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 如果要修改密码，验证当前密码
        hashed_password = None
        if new_password:
            if not current_password:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="修改密码时需要提供当前密码"
                )
            
            if not self.verify_password(current_password, user.hashed_password):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="当前密码不正确"
                )
            
            hashed_password = self.get_password_hash(new_password)
        
        # 检查邮箱是否被其他用户使用
        if email and await self.user_repo.email_exists(email.strip(), username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被其他用户使用"
            )
        
        # 更新用户信息
        update_email = email.strip() if email else None
        success = await self.user_repo.update_user_info(username, update_email, hashed_password)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="更新用户信息失败，请稍后重试"
            )
        
        # 返回更新后的用户信息
        updated_user = await self.user_repo.get_user_by_username(username)
        return UserInfoResponse(
            username=updated_user.username,
            email=updated_user.email,
            role=updated_user.role,
            created_at=updated_user.created_at
        )
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """创建访问令牌"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(UTC) + expires_delta
        else:
            expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> dict:
        """验证JWT令牌"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="无效的令牌",
                )
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的令牌",
            )
    
    async def get_current_user_info(self, token: str) -> dict:
        """根据token获取当前用户信息"""
        payload = self.verify_token(token)
        username = payload.get("sub")
        
        user = await self.user_repo.get_user_by_username(username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在",
            )
        
        return {
            "username": username,
            "role": user.role
        }
    
    async def verify_admin_permission(self, token: str, required_role: UserRole = UserRole.PAPER_ADMIN) -> str:
        """验证管理员权限"""
        user_info = await self.get_current_user_info(token)
        
        if required_role == UserRole.SUPER_ADMIN:
            if user_info["role"] != UserRole.SUPER_ADMIN:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="需要超级管理员权限",
                )
        elif required_role == UserRole.PAPER_ADMIN:
            if user_info["role"] not in [UserRole.SUPER_ADMIN, UserRole.PAPER_ADMIN]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="需要管理员权限",
                )
        
        return user_info["username"]
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """获取密码哈希"""
        return self.pwd_context.hash(password) 