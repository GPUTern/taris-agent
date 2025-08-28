import os
from dotenv import load_dotenv  # noqa: D100

# 加载环境变量
load_dotenv()

# 获取环境变量或使用默认值的辅助函数
def get_env(key, default=None):
    """获取环境变量，如果不存在则返回默认值"""
    return os.getenv(key, default)

# JWT 配置
SECRET_KEY = get_env("SECRET_KEY", "your-super-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 24 * 60  # 24 小时

# 应用配置
APP_NAME = "医工前沿社区 API"
APP_VERSION = "1.0.0"
API_PREFIX = "/api"

# 分页配置
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 50

# 速率限制
RATE_LIMIT = 100  # 每分钟请求数

# 数据库配置
DATABASE_TYPE = get_env("DATABASE_TYPE", "memory")  # "memory" 或 "sqlite"
DATABASE_URL = get_env("DATABASE_URL", "sqlite:///./bioeng.db")
DATABASE_PATH = "./bioeng.db"