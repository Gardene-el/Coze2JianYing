"""
SSE 日志广播

将 Python 标准 logging 条目推送给所有已注册的 SSE 订阅者队列。
"""
import asyncio
import logging
from typing import List, Optional

# 所有已连接的 SSE 客户端队列
_subscribers: List[asyncio.Queue] = []

# GUI 管理服务的事件循环（由 gui_main.py 在启动后注入）
_loop: Optional[asyncio.AbstractEventLoop] = None


def set_event_loop(loop: asyncio.AbstractEventLoop) -> None:
    """注入事件循环引用，使日志处理器能跨线程投递消息。"""
    global _loop
    _loop = loop


def register_subscriber(q: asyncio.Queue) -> None:
    """注册 SSE 客户端队列。"""
    _subscribers.append(q)


def unregister_subscriber(q: asyncio.Queue) -> None:
    """注销 SSE 客户端队列。"""
    try:
        _subscribers.remove(q)
    except ValueError:
        pass


async def _broadcast(msg: str) -> None:
    """向所有订阅者广播一条日志消息（在事件循环内调用）。"""
    for q in _subscribers[:]:
        try:
            q.put_nowait(msg)
        except asyncio.QueueFull:
            # 丢弃最旧的条目以腾出空间
            try:
                q.get_nowait()
                q.put_nowait(msg)
            except Exception:
                pass


class SSELogHandler(logging.Handler):
    """将日志记录跨线程推送到所有 SSE 订阅者的处理器。"""

    def emit(self, record: logging.LogRecord) -> None:
        global _loop
        if _loop is None or not _loop.is_running():
            return
        try:
            msg = self.format(record)
            asyncio.run_coroutine_threadsafe(_broadcast(msg), _loop)
        except Exception:
            pass


def install(level: int = logging.INFO) -> SSELogHandler:
    """
    在根 logger 上安装 SSELogHandler。

    Returns:
        安装的处理器实例（可用于后续卸载）。
    """
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler = SSELogHandler(level)
    handler.setFormatter(formatter)
    logging.getLogger().addHandler(handler)
    return handler
