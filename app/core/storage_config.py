r"""
Windows 专用存储配置模块

统一管理 Coze2JianYing 的所有数据存储路径
所有数据存储在 C:\Users\{username}\AppData\Local\coze2jianying\ 下
"""
import os
from pathlib import Path
from typing import Optional
from app.utils.logger import get_logger


class StorageConfig:
    r"""
    Windows 专用存储配置管理器
    
    目录结构:
    C:\Users\{username}\AppData\Local\coze2jianying\
    ├── cache\      # 临时数据 (替代 /tmp/jianying_assistant)
    ├── drafts\     # 生成的草稿 (替代临时目录)
    └── assets\     # 下载的素材 (替代临时目录)
    """
    
    def __init__(self):
        """初始化存储配置"""
        self.logger = get_logger(__name__)
        
        # 获取 Windows LocalAppData 路径
        localappdata = os.getenv('LOCALAPPDATA')
        if not localappdata:
            # 如果环境变量不存在，构造默认路径
            username = os.getenv('USERNAME', 'User')
            localappdata = f"C:\\Users\\{username}\\AppData\\Local"
        
        # 基础目录
        self.base_dir = Path(localappdata) / "coze2jianying"
        
        # 三个子目录
        self.cache_dir = self.base_dir / "cache"      # 临时数据
        self.drafts_dir = self.base_dir / "drafts"    # 生成的草稿
        self.assets_dir = self.base_dir / "assets"    # 下载的素材
        
        # 确保所有目录存在
        self._ensure_directories()
        
        self.logger.info(f"存储配置初始化完成: {self.base_dir}")
    
    def _ensure_directories(self):
        """确保所有目录存在"""
        for directory in [self.cache_dir, self.drafts_dir, self.assets_dir]:
            directory.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"目录已准备: {directory}")
    
    def get_cache_dir(self) -> Path:
        """
        获取缓存目录
        用于存储临时数据，替代 /tmp/jianying_assistant/drafts
        
        Returns:
            缓存目录路径
        """
        return self.cache_dir
    
    def get_drafts_dir(self) -> Path:
        """
        获取草稿目录
        用于存储生成的草稿，替代 tempfile.mkdtemp() 创建的临时目录
        
        Returns:
            草稿目录路径
        """
        return self.drafts_dir
    
    def get_assets_dir(self) -> Path:
        """
        获取素材目录
        用于存储下载的素材文件，替代 tempfile.mkdtemp() 创建的临时目录
        
        Returns:
            素材目录路径
        """
        return self.assets_dir
    
    def get_summary(self) -> dict:
        """
        获取配置摘要
        
        Returns:
            配置信息字典
        """
        return {
            "基础目录": str(self.base_dir),
            "缓存目录": str(self.cache_dir),
            "草稿目录": str(self.drafts_dir),
            "素材目录": str(self.assets_dir),
        }


# 全局单例
_storage_config: Optional[StorageConfig] = None


def get_storage_config() -> StorageConfig:
    """
    获取全局存储配置实例（单例模式）
    
    Returns:
        StorageConfig 实例
    """
    global _storage_config
    
    if _storage_config is None:
        _storage_config = StorageConfig()
    
    return _storage_config


def reset_storage_config():
    """重置全局存储配置（主要用于测试）"""
    global _storage_config
    _storage_config = None
