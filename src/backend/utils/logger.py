"""
日志系统模块
提供统一的日志记录功能，支持文件和GUI显示
"""
import logging
import sys
from pathlib import Path
from typing import Optional


logger = logging.getLogger(__name__)


class LogHandler:
    """日志处理器，用于将日志发送到GUI"""
    
    _instance = None
    _gui_callback = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def set_gui_callback(cls, callback):
        """设置GUI回调函数，用于在GUI中显示日志"""
        cls._gui_callback = callback
    
    @classmethod
    def emit_to_gui(cls, message: str):
        """发送日志消息到GUI"""
        if cls._gui_callback:
            cls._gui_callback(message)


class GUIHandler(logging.Handler):
    """自定义日志处理器，将日志发送到GUI"""
    
    def emit(self, record):
        """处理日志记录"""
        try:
            msg = self.format(record)
            LogHandler.emit_to_gui(msg)
            # 强制刷新，确保日志立即显示
            sys.stdout.flush()
        except Exception:
            self.handleError(record)


def setup_logger(log_file: Optional[Path] = None, level=logging.INFO):
    """
    设置日志系统
    
    Args:
        log_file: 日志文件路径，如果为None则只输出到控制台
        level: 日志级别
    """
    # 创建根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # 清除现有的处理器
    root_logger.handlers.clear()
    
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # 文件处理器
    if log_file:
        file_handler = logging.FileHandler(
            log_file,
            encoding='utf-8',
            mode='a'
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # GUI处理器
    gui_handler = GUIHandler()
    gui_handler.setLevel(level)
    gui_handler.setFormatter(formatter)
    root_logger.addHandler(gui_handler)
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    获取日志记录器
    
    Args:
        name: 日志记录器名称，通常使用 __name__
        
    Returns:
        日志记录器实例
    """
    return logging.getLogger(name)


def set_gui_log_callback(callback):
    """
    设置GUI日志回调函数
    
    Args:
        callback: 回调函数，接收一个字符串参数（日志消息）
    """
    LogHandler.set_gui_callback(callback)
