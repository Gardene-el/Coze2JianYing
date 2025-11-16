"""
全局存储设置管理器

用于在 GUI 和 API 之间共享草稿存储配置
"""
from typing import Optional
from threading import Lock


class StorageSettings:
    """
    全局存储设置单例
    
    GUI 标签页可以设置存储模式，API 在保存草稿时读取这些设置
    """
    
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
        
        # 默认使用本地存储模式
        self._enable_transfer = False
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
    
    def get_output_folder(self) -> Optional[str]:
        """
        获取输出文件夹
        
        Returns:
            如果启用传输，返回 target_folder
            否则返回 None（表示使用默认的 config.drafts_dir）
        """
        if self._enable_transfer:
            return self._target_folder
        return None


# 全局实例
_storage_settings = StorageSettings()


def get_storage_settings() -> StorageSettings:
    """获取全局存储设置实例"""
    return _storage_settings
