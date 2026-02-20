"""
应用配置管理模块

应用仅在 Windows 系统上运行。
数据存储在: C:\\Users\\<username>\\AppData\\Local\\coze2jianying_data\\
- cache/: 缓存文件 (替代 C:\\tmp\\jianying_assistant)
- drafts/: 草稿文件 (替代 C:\\Users\\<username>\\AppData\\Local\\Temp\\jianying_draft_*)
- assets/: 素材文件 (替代 C:\\Users\\<username>\\AppData\\Local\\Temp\\jianying_assets_*)
"""
import os
import tempfile
from pathlib import Path
from typing import Optional


class AppConfig:
    """应用配置类 - 仅支持 Windows"""
    
    def __init__(self):
        """初始化配置"""
        self._load_config()
    
    def _load_config(self):
        """加载配置"""
        # 数据存储根目录
        self.data_root = self._get_data_root()
        
        # cache 目录 - 替代 C:\tmp\jianying_assistant
        self.cache_dir = self._get_path_from_env(
            "JIANYING_CACHE_DIR",
            os.path.join(self.data_root, "cache")
        )
        
        # drafts 目录 - 替代 Temp\jianying_draft_*
        self.drafts_dir = self._get_path_from_env(
            "JIANYING_DRAFTS_DIR",
            os.path.join(self.data_root, "drafts")
        )
        
        # assets 目录 - 替代 Temp\jianying_assets_*
        self.assets_dir = self._get_path_from_env(
            "JIANYING_ASSETS_DIR",
            os.path.join(self.data_root, "assets")
        )
        
        # 保持旧的属性名以兼容现有代码
        self.segments_dir = self.cache_dir  # segments 使用 cache
        self.materials_cache_dir = self.assets_dir  # materials 使用 assets
        self.output_dir = self.drafts_dir  # output 使用 drafts
        self.log_dir = os.path.join(self.data_root, "logs")
        
        # 确保所有目录存在
        self._ensure_directories()
    
    def _get_data_root(self) -> str:
        """
        获取数据存储根目录
        
        Windows: C:\\Users\\<username>\\AppData\\Local\\coze2jianying_data
        
        优先级：
        1. 环境变量 JIANYING_DATA_ROOT
        2. Windows: %LOCALAPPDATA%\\coze2jianying_data
        """
        # 1. 环境变量
        env_root = os.getenv("JIANYING_DATA_ROOT")
        if env_root:
            return env_root
        
        # 2. Windows 环境（应用仅在 Windows 运行）
        localappdata = os.getenv("LOCALAPPDATA")
        if localappdata:
            return os.path.join(localappdata, "coze2jianying_data")
        
        # 备选：如果 LOCALAPPDATA 不存在，使用 APPDATA
        appdata = os.getenv("APPDATA")
        if appdata:
            # APPDATA 是 Roaming，向上一级到 Local
            local_path = os.path.join(os.path.dirname(appdata), "Local", "coze2jianying_data")
            return local_path
        
        # 最后备选 - 临时目录
        return os.path.join(tempfile.gettempdir(), "coze2jianying_data")
    
    def _get_path_from_env(self, env_var: str, default_path: str) -> str:
        """
        从环境变量获取路径，如果不存在则使用默认路径
        
        Args:
            env_var: 环境变量名
            default_path: 默认路径
            
        Returns:
            路径字符串
        """
        path = os.getenv(env_var)
        if path:
            return path
        return default_path
    
    def _ensure_directories(self):
        """确保所有必要的目录存在"""
        directories = [
            self.data_root,
            self.cache_dir,
            self.drafts_dir,
            self.assets_dir,
            self.log_dir,
        ]
        
        for directory in directories:
            try:
                os.makedirs(directory, exist_ok=True)
            except PermissionError:
                # 如果没有权限创建目录，尝试使用临时目录
                temp_base = os.path.join(tempfile.gettempdir(), "coze2jianying_data")
                
                # 重新设置所有路径到临时目录
                self.data_root = temp_base
                self.cache_dir = os.path.join(temp_base, "cache")
                self.drafts_dir = os.path.join(temp_base, "drafts")
                self.assets_dir = os.path.join(temp_base, "assets")
                self.log_dir = os.path.join(temp_base, "logs")
                
                # 更新兼容属性
                self.segments_dir = self.cache_dir
                self.materials_cache_dir = self.assets_dir
                self.output_dir = self.drafts_dir
                
                # 重新尝试创建目录
                for temp_dir in [self.data_root, self.cache_dir, self.drafts_dir, 
                                 self.assets_dir, self.log_dir]:
                    os.makedirs(temp_dir, exist_ok=True)
                break
    
    def to_dict(self) -> dict:
        """
        将配置转换为字典
        
        Returns:
            配置字典
        """
        return {
            "platform": "Windows",
            "data_root": self.data_root,
            "cache_dir": self.cache_dir,
            "drafts_dir": self.drafts_dir,
            "assets_dir": self.assets_dir,
            "log_dir": self.log_dir,
        }


# 全局配置实例
_config: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """
    获取全局配置实例（单例模式）
    
    Returns:
        AppConfig 实例
    """
    global _config
    
    if _config is None:
        _config = AppConfig()
    
    return _config


def reset_config():
    """重置配置（主要用于测试）"""
    global _config
    _config = None
