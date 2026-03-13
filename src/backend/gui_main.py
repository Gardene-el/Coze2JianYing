"""
GUI 管理服务入口

在端口 20210 启动独立的 FastAPI 应用，供 Electron 前端管理：
  - Coze API 服务的启停
  - ngrok 隧道
  - 设置读写
  - 日志 SSE 流
  - 草稿生成 / 脚本执行

用法：
    python -m src.backend.gui_main [--host 127.0.0.1] [--port 20210]
"""
import argparse
import asyncio
import logging

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.backend.routers.gui_router import gui_router
from src.backend.utils import sse_log
from src.backend.utils.logger import setup_logger


def create_gui_app() -> FastAPI:
    """构造并返回 GUI 管理 FastAPI 应用。"""
    app = FastAPI(
        title="Coze2JianYing GUI 管理 API",
        description="Electron 前端与 Python 后端的通信桥梁",
        version="1.0.0",
        docs_url="/gui/docs",
        redoc_url=None,
        openapi_url="/gui/openapi.json",
    )

    # 仅允许本地来源（Electron 加载 localhost 页面）
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",   # Vite dev server
            "http://localhost:20210",  # 自身（防止某些代理场景）
            "app://.",                 # Electron production 协议
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(gui_router, prefix="/gui")
    return app


gui_app = create_gui_app()


@gui_app.on_event("startup")
async def _on_startup() -> None:
    """将当前事件循环注入 SSE 日志模块，使跨线程日志推送成功。"""
    loop = asyncio.get_running_loop()
    sse_log.set_event_loop(loop)
    sse_log.install(level=logging.INFO)


def run(host: str = "127.0.0.1", port: int = 20210) -> None:
    """启动 GUI 管理服务器（阻塞调用）。"""
    uvicorn.run(
        "src.backend.gui_main:gui_app",
        host=host,
        port=port,
        log_level="info",
        reload=False,
    )


if __name__ == "__main__":
    import os
    from pathlib import Path

    log_dir = Path(__file__).parent.parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    setup_logger(log_dir / "gui.log")

    parser = argparse.ArgumentParser(description="Coze2JianYing GUI 管理服务")
    parser.add_argument("--host", default="127.0.0.1", help="监听地址")
    parser.add_argument("--port", type=int, default=20210, help="监听端口")
    args = parser.parse_args()

    run(host=args.host, port=args.port)
