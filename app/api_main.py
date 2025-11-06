"""
FastAPI 服务主入口
独立于 GUI，专门用于运行 API 服务
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime
from pathlib import Path

from app.api.router import api_router

# 创建 FastAPI 应用
app = FastAPI(
    title="Coze剪映草稿生成器 API",
    description="示例 API 接口，演示 FastAPI 的各种通讯方法",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录
static_path = Path(__file__).parent / "static"
templates_path = Path(__file__).parent / "templates"

if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "message": "Internal server error",
            "detail": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )


# 根路径 - 返回网页
@app.get("/", tags=["根路径"], response_class=HTMLResponse)
async def root():
    """
    API 根路径 - 返回项目主页
    """
    index_file = templates_path / "index.html"
    if index_file.exists():
        return HTMLResponse(content=index_file.read_text(encoding="utf-8"))
    else:
        # 如果模板文件不存在，返回 JSON 信息
        return JSONResponse(content={
            "message": "Welcome to Coze剪映草稿生成器 API",
            "docs": "/docs",
            "redoc": "/redoc",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat()
        })


# API 信息端点
@app.get("/api", tags=["根路径"])
async def api_info():
    """
    API 信息端点
    """
    return {
        "message": "Welcome to Coze剪映草稿生成器 API",
        "docs": "/docs",
        "redoc": "/redoc",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


# 健康检查端点
@app.get("/api/health", tags=["根路径"])
async def health_check():
    """
    健康检查端点
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


# 注册 API 路由
app.include_router(api_router)


# 启动服务的函数
def start_api_server(host: str = "127.0.0.1", port: int = 8000):
    """启动 FastAPI 服务器"""
    uvicorn.run(
        "app.api_main:app",
        host=host,
        port=port,
        reload=True,  # 开发模式下自动重载
        log_level="info"
    )


if __name__ == "__main__":
    start_api_server()
