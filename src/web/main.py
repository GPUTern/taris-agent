from contextlib import asynccontextmanager  # noqa: D100

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.web.config.settings import API_PREFIX, APP_NAME, APP_VERSION
from src.web.controllers import (
    admin_router,
    auth_router,
    domains_router,
    library_router,
    news_router,
    paper_router,
    tags_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理."""
    # 启动时初始化数据库
    # await db_connection.initialize_tables()
    
    yield
    
    # 关闭时清理资源（如果需要）


# 创建 FastAPI 应用
app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="快速检索、浏览并评论最新 AI 论文的一站式接口",
    lifespan=lifespan
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:5173", 
        "http://localhost:5174",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://192.168.10.135:5173",
        "http://192.168.10.135:5174",
        "http://192.168.10.135:3000",
    ],  # 前端开发服务器
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(paper_router, prefix=API_PREFIX)
app.include_router(news_router, prefix=API_PREFIX)
app.include_router(admin_router, prefix=API_PREFIX)
app.include_router(tags_router, prefix=API_PREFIX)
app.include_router(domains_router, prefix=API_PREFIX)
app.include_router(library_router, prefix=API_PREFIX)


@app.get("/")
async def root():
    """根路径."""
    return {"message": "欢迎使用医工前沿社区 API", "version": APP_VERSION}


@app.get("/health")
async def health_check():
    """健康检查."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
