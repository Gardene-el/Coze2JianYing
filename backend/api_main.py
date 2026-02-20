"""
FastAPI 服务主入口
独立于 GUI，专门用于运行 API 服务
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime
import argparse
import os

from backend.api.router import api_router
from backend.utils.settings_manager import get_settings_manager

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


# 根路径
@app.get("/", tags=["根路径"])
async def root():
    """
    API 根路径
    """
    return {
        "message": "Welcome to Coze剪映草稿生成器 API",
        "docs": "/docs",
        "redoc": "/redoc",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


# 注册 API 路由
app.include_router(api_router)


# 启动服务的函数
def start_api_server(host: str = "127.0.0.1", port: int = 8000):
    """启动 FastAPI 服务器"""
    uvicorn.run(
        "backend.api_main:app",
        host=host,
        port=port,
        reload=True,  # 开发模式下自动重载
        log_level="info"
    )


if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser(
        description="Coze2JianYing API 服务 - 独立运行模式",
        epilog="示例: python backend/api_main.py --port 8000 --draft-dir \"D:\\JianYing\\Drafts\""
    )
    # 移除 required=True，改为手动检查以提供中文提示
    parser.add_argument("--port", type=int, help="[必须] API 服务监听端口 (例如: 8000)")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="API 服务监听地址 (默认: 127.0.0.1)")
    parser.add_argument("--draft-dir", type=str, help="[必须] 剪映草稿保存路径 (例如: .../JianYingPro/User Data/Projects/com.lveditor.draft)")
    
    args = parser.parse_args()

    # 手动检查必要参数
    missing_args = []
    if args.port is None:
        missing_args.append("--port")
    if args.draft_dir is None:
        missing_args.append("--draft-dir")
    
    if missing_args:
        parser.print_usage()
        print(f"\n错误: 缺少必要参数: {', '.join(missing_args)}")
        print("请使用 --help 查看详细帮助信息。")
        exit(1)

    # 验证端口范围
    if not (1 <= args.port <= 65535):
        print(f"错误: 端口号 {args.port} 无效。")
        print("端口号必须在 1 到 65535 之间。")
        exit(1)

    # 更新设置
    settings = get_settings_manager()
    
    # 验证路径是否存在
    if os.path.exists(args.draft_dir):
        print(f"配置: 使用命令行指定的草稿路径: {args.draft_dir}")
        settings.set("draft_folder", args.draft_dir)
        # 确保启用传输模式，这样 get_effective_output_path 才会使用这个路径
        settings.set("transfer_enabled", True) 
    else:
        print(f"错误: 指定的草稿路径不存在: {args.draft_dir}")
        print("请检查路径是否正确。")
        exit(1)

    print(f"启动服务: http://{args.host}:{args.port}")
    start_api_server(host=args.host, port=args.port)
