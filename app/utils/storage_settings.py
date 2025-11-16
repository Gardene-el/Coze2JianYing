"""
全局存储设置管理器

用于在 GUI 和 API 之间共享草稿存储配置
整合了文件夹管理功能，提供统一的存储设置接口
"""
import os
from typing import Optional, Tuple
from threading import Lock


class StorageSettings:
    """
    全局存储设置单例
    
    GUI 可以设置存储模式，API 在保存草稿时读取这些设置
    包含文件夹路径管理、自动检测、验证等功能
    """
    
    # 默认剪映草稿路径
    DEFAULT_DRAFT_PATHS = [
        r"C:\Users\{username}\AppData\Local\JianyingPro\User Data\Projects\com.lveditor.draft",
        r"C:\Users\{username}\AppData\Roaming\JianyingPro\User Data\Projects\com.lveditor.draft",
    ]
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        # 默认启用传输模式
        self._enable_transfer = True
        self._target_folder = None
        self._initialized = True
    
    @property
    def enable_transfer(self) -> bool:
        """是否启用传输到指定文件夹"""
        return self._enable_transfer
    
    @enable_transfer.setter
    def enable_transfer(self, value: bool):
        """设置是否启用传输"""
        self._enable_transfer = value
    
    @property
    def target_folder(self) -> Optional[str]:
        """目标文件夹路径"""
        return self._target_folder
    
    @target_folder.setter
    def target_folder(self, value: Optional[str]):
        """设置目标文件夹路径"""
        self._target_folder = value
    
    def get_use_local_storage(self) -> bool:
        """
        获取是否使用本地存储模式
        
        Returns:
            True: 使用 config.drafts_dir + config.assets_dir
            False: 使用 target_folder + CozeJianYingAssistantAssets
        """
        return not self._enable_transfer
    
    def get_output_folder(self, fallback: Optional[str] = None) -> Optional[str]:
        """
        获取输出文件夹
        
        Args:
            fallback: 备用文件夹路径（当不启用传输时使用）
            
        Returns:
            如果启用传输，返回 target_folder
            否则返回 fallback
        """
        if self._enable_transfer:
            return self._target_folder
        return fallback
    
    def detect_default_folder(self) -> Optional[str]:
        """
        自动检测剪映草稿文件夹
        
        Returns:
            检测到的文件夹路径，如果未检测到则返回None
        """
        username = os.getenv('USERNAME') or os.getenv('USER')
        
        for path_template in self.DEFAULT_DRAFT_PATHS:
            path = path_template.format(username=username)
            if os.path.exists(path) and os.path.isdir(path):
                return path
        
        return None
    
    def validate_folder(self, path: Optional[str]) -> Tuple[bool, str]:
        """
        验证文件夹路径是否有效
        
        Args:
            path: 要验证的路径
            
        Returns:
            (是否有效, 错误消息)
        """
        if not path:
            return False, "未选择文件夹"
        
        if not os.path.exists(path):
            return False, f"文件夹不存在: {path}"
        
        if not os.path.isdir(path):
            return False, f"路径不是文件夹: {path}"
        
        return True, ""


# 全局实例
_storage_settings = StorageSettings()


def get_storage_settings() -> StorageSettings:
    """获取全局存储设置实例"""
    return _storage_settings
