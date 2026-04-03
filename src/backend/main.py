"""
Backend 统一入口

在端口 20211 启动唯一 FastAPI 应用，同时提供：
  - /gui/*   管理端点（设置、健康检查、SSE 日志、草稿生成、脚本执行）
  - /drafts/* /segments/*  剪映草稿操作 API（easy + basic 路由）

用法：
    python -m src.backend.main [--host 127.0.0.1] [--port 20211]
"""
import argparse
import asyncio
import logging

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.backend.api.router import api_router
from src.backend.middlewares.response import ResponseMiddleware
from src.backend.routers.gui_router import gui_router
from src.backend.utils import sse_log
from src.backend.utils.logger import setup_logger

DEFAULT_PORT = 20211


def create_gui_app() -> FastAPI:
    """构造并返回统一 FastAPI 应用。"""
    app = FastAPI(
        title="Coze2JianYing API",
        description="剪映草稿操作 API + Electron 前端管理端点",
        version="1.0.0",
        docs_url="/docs",
        redoc_url=None,
        openapi_url="/openapi.json",
    )

    # 仅允许本地来源（Electron 加载 localhost 页面）
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",    # Vite dev server
            f"http://localhost:{DEFAULT_PORT}",  # 自身
            "app://.",                  # Electron production 协议
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 统一响应中间件：成功包装 + 错误标准化 + 强制 HTTP 200
    # SSE 端点（text/event-stream）由 _should_bypass 自动穿透
    app.add_middleware(ResponseMiddleware)

    # 管理路由（/gui/*）——仅供 Electron 前端内部使用，不暴露在 OpenAPI 文档中
    app.include_router(gui_router, prefix="/gui", include_in_schema=False)

    # 草稿操作路由（/drafts/*, /segments/*）
    app.include_router(api_router)

    return app


gui_app = create_gui_app()


@gui_app.on_event("startup")
async def _on_startup() -> None:
    """将当前事件循环注入 SSE 日志模块，使跨线程日志推送成功。"""
    loop = asyncio.get_running_loop()
    sse_log.set_event_loop(loop)
    sse_log.install(level=logging.INFO)
    _gui_logger = logging.getLogger(__name__)
    _gui_logger.info("=" * 50)
    _gui_logger.info("Coze2JianYing 服务已就绪")
    _gui_logger.info("监听地址: http://127.0.0.1:%d", DEFAULT_PORT)


def run(host: str = "127.0.0.1", port: int = DEFAULT_PORT) -> None:
    """启动服务器（阻塞调用）。"""
    uvicorn.run(
        "src.backend.main:gui_app",
        host=host,
        port=port,
        log_level="info",
        reload=False,
    )


if __name__ == "__main__":
    from pathlib import Path

    log_dir = Path(__file__).parent.parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    setup_logger(log_dir / "backend.log")

    parser = argparse.ArgumentParser(description="Coze2JianYing 后端服务")
    parser.add_argument("--host", default="127.0.0.1", help="监听地址")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="监听端口")
    args = parser.parse_args()

    run(host=args.host, port=args.port)
