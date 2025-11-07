"""
应用配置管理模块

提供统一的配置管理，支持：
1. 环境变量配置
2. 跨平台路径处理
3. 云端部署和本地开发模式
"""
import os
import platform
import tempfile
from pathlib import Path
from typing import Optional


class AppConfig:
    """应用配置类"""
    
    def __init__(self):
        """初始化配置"""
        self._load_config()
    
    def _load_config(self):
        """加载配置"""
        # 检测运行环境
        self.is_windows = platform.system() == "Windows"
        self.is_linux = platform.system() == "Linux"
        self.is_mac = platform.system() == "Darwin"
        
        # 数据存储根目录 - 从环境变量读取，如果没有则使用默认值
        self.data_root = self._get_data_root()
        
        # 草稿存储目录
        self.drafts_dir = self._get_path_from_env(
            "JIANYING_DRAFTS_DIR",
            os.path.join(self.data_root, "drafts")
        )
        
        # 片段存储目录
        self.segments_dir = self._get_path_from_env(
            "JIANYING_SEGMENTS_DIR",
            os.path.join(self.data_root, "segments")
        )
        
        # 素材缓存目录
        self.materials_cache_dir = self._get_path_from_env(
            "JIANYING_MATERIALS_CACHE_DIR",
            os.path.join(self.data_root, "materials_cache")
        )
        
        # 输出目录（生成的草稿项目）
        self.output_dir = self._get_path_from_env(
            "JIANYING_OUTPUT_DIR",
            os.path.join(self.data_root, "output")
        )
        
        # 日志目录
        self.log_dir = self._get_path_from_env(
            "JIANYING_LOG_DIR",
            os.path.join(self.data_root, "logs")
        )
        
        # 确保所有目录存在
        self._ensure_directories()
    
    def _get_data_root(self) -> str:
        """
        获取数据存储根目录
        
        优先级：
        1. 环境变量 JIANYING_DATA_ROOT
        2. 云端环境：使用 /app/data （适合 Docker 等容器环境）
        3. Windows: %APPDATA%/JianyingAssistant 或 %LOCALAPPDATA%/JianyingAssistant
        4. Linux/Mac: ~/.local/share/jianying_assistant
        5. 最后备选：临时目录下的 jianying_assistant
        """
        # 1. 环境变量
        env_root = os.getenv("JIANYING_DATA_ROOT")
        if env_root:
            return env_root
        
        # 2. 云端环境标识（通过环境变量检测）
        is_cloud = os.getenv("JIANYING_CLOUD_MODE", "").lower() in ("true", "1", "yes")
        if is_cloud:
            # 云端环境使用 /app/data
            return "/app/data"
        
        # 3. Windows 环境
        if self.is_windows:
            appdata = os.getenv("APPDATA") or os.getenv("LOCALAPPDATA")
            if appdata:
                return os.path.join(appdata, "JianyingAssistant")
        
        # 4. Linux/Mac 环境
        if self.is_linux or self.is_mac:
            home = os.path.expanduser("~")
            return os.path.join(home, ".local", "share", "jianying_assistant")
        
        # 5. 最后备选 - 临时目录
        return os.path.join(tempfile.gettempdir(), "jianying_assistant")
    
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
            self.drafts_dir,
            self.segments_dir,
            self.materials_cache_dir,
            self.output_dir,
            self.log_dir,
        ]
        
        for directory in directories:
            try:
                os.makedirs(directory, exist_ok=True)
            except PermissionError:
                # 如果没有权限创建目录，尝试使用临时目录
                temp_base = os.path.join(tempfile.gettempdir(), "jianying_assistant")
                
                # 重新设置所有路径到临时目录
                self.data_root = temp_base
                self.drafts_dir = os.path.join(temp_base, "drafts")
                self.segments_dir = os.path.join(temp_base, "segments")
                self.materials_cache_dir = os.path.join(temp_base, "materials_cache")
                self.output_dir = os.path.join(temp_base, "output")
                self.log_dir = os.path.join(temp_base, "logs")
                
                # 重新尝试创建目录
                for temp_dir in [self.data_root, self.drafts_dir, self.segments_dir, 
                                 self.materials_cache_dir, self.output_dir, self.log_dir]:
                    os.makedirs(temp_dir, exist_ok=True)
                break
    
    def get_default_jianying_draft_paths(self) -> list:
        """
        获取剪映默认草稿路径列表
        
        Returns:
            可能的剪映草稿路径列表
        """
        paths = []
        
        if self.is_windows:
            username = os.getenv("USERNAME", "")
            if username:
                paths.extend([
                    os.path.join(
                        "C:", "Users", username, "AppData", "Local",
                        "JianyingPro", "User Data", "Projects", "com.lveditor.draft"
                    ),
                    os.path.join(
                        "C:", "Users", username, "AppData", "Roaming",
                        "JianyingPro", "User Data", "Projects", "com.lveditor.draft"
                    ),
                ])
        elif self.is_mac:
            home = os.path.expanduser("~")
            paths.extend([
                os.path.join(
                    home, "Library", "Containers", "com.lveditor.jianyingpro",
                    "Data", "Library", "Application Support", "JianyingPro",
                    "User Data", "Projects", "com.lveditor.draft"
                ),
            ])
        
        return paths
    
    def to_dict(self) -> dict:
        """
        将配置转换为字典
        
        Returns:
            配置字典
        """
        return {
            "platform": platform.system(),
            "data_root": self.data_root,
            "drafts_dir": self.drafts_dir,
            "segments_dir": self.segments_dir,
            "materials_cache_dir": self.materials_cache_dir,
            "output_dir": self.output_dir,
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
