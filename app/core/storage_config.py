"""
集中式存储配置管理模块

提供统一的、平台无关的存储路径管理，支持：
- 自动检测操作系统和剪映安装路径
- 用户自定义存储位置
- 环境变量配置
- 配置文件持久化
"""
import os
import json
import platform
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any
from app.utils.logger import get_logger


class StorageConfig:
    """
    存储配置管理器
    
    功能：
    1. 管理所有数据存储路径（草稿、素材、临时文件等）
    2. 平台无关的路径检测（Windows/Mac/Linux）
    3. 支持用户自定义配置
    4. 配置持久化到文件
    """
    
    # 配置文件路径
    CONFIG_FILE = Path.home() / ".coze2jianying" / "storage_config.json"
    
    # 默认配置
    DEFAULT_CONFIG = {
        "drafts_base_dir": None,  # 草稿输出目录（None = 自动检测）
        "state_base_dir": None,   # 状态管理目录（None = 使用系统临时目录）
        "assets_base_dir": None,  # 素材存储目录（None = 跟随草稿目录）
        "temp_dir": None,         # 临时文件目录（None = 使用系统临时目录）
        "auto_detect_jianying": True,  # 是否自动检测剪映路径
    }
    
    def __init__(self, config_file: Optional[Path] = None):
        """
        初始化存储配置管理器
        
        Args:
            config_file: 自定义配置文件路径（可选）
        """
        self.logger = get_logger(__name__)
        
        if config_file:
            self.config_file = Path(config_file)
        else:
            self.config_file = self.CONFIG_FILE
        
        # 加载配置
        self.config = self._load_config()
        
        # 初始化路径
        self._init_paths()
        
        self.logger.info(f"存储配置已加载: {self.config_file}")
    
    def _load_config(self) -> Dict[str, Any]:
        """
        从文件加载配置
        
        Returns:
            配置字典
        """
        # 如果配置文件不存在，使用默认配置
        if not self.config_file.exists():
            self.logger.info("配置文件不存在，使用默认配置")
            return self.DEFAULT_CONFIG.copy()
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 合并默认配置（填充缺失的键）
            merged = self.DEFAULT_CONFIG.copy()
            merged.update(config)
            
            self.logger.info(f"配置已从文件加载: {self.config_file}")
            return merged
            
        except Exception as e:
            self.logger.error(f"加载配置文件失败: {e}，使用默认配置")
            return self.DEFAULT_CONFIG.copy()
    
    def _save_config(self) -> bool:
        """
        保存配置到文件
        
        Returns:
            是否成功保存
        """
        try:
            # 确保配置目录存在
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"配置已保存到: {self.config_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"保存配置文件失败: {e}")
            return False
    
    def _init_paths(self):
        """初始化所有路径"""
        # 1. 草稿输出目录
        if self.config.get("auto_detect_jianying", True):
            detected_path = self.detect_jianying_draft_folder()
            if detected_path:
                self._drafts_base_dir = Path(detected_path)
                self.logger.info(f"自动检测到剪映草稿目录: {self._drafts_base_dir}")
            else:
                # 未检测到，使用默认目录
                self._drafts_base_dir = self._get_default_drafts_dir()
                self.logger.info(f"未检测到剪映，使用默认草稿目录: {self._drafts_base_dir}")
        else:
            custom_path = self.config.get("drafts_base_dir")
            if custom_path:
                self._drafts_base_dir = Path(custom_path)
            else:
                self._drafts_base_dir = self._get_default_drafts_dir()
        
        # 2. 状态管理目录
        state_dir = self.config.get("state_base_dir")
        if state_dir:
            self._state_base_dir = Path(state_dir)
        else:
            self._state_base_dir = self._get_default_state_dir()
        
        # 3. 素材存储目录（跟随草稿目录）
        assets_dir = self.config.get("assets_base_dir")
        if assets_dir:
            self._assets_base_dir = Path(assets_dir)
        else:
            # 默认：在草稿目录下创建统一的素材文件夹
            self._assets_base_dir = self._drafts_base_dir / "CozeJianYingAssistantAssets"
        
        # 4. 临时文件目录
        temp_dir = self.config.get("temp_dir")
        if temp_dir:
            self._temp_dir = Path(temp_dir)
        else:
            self._temp_dir = self._get_default_temp_dir()
        
        # 确保所有目录存在
        self._ensure_directories()
    
    def _get_default_drafts_dir(self) -> Path:
        """
        获取默认草稿目录
        
        Returns:
            默认草稿目录路径
        """
        # 使用用户主目录下的 JianyingProjects
        return Path.home() / "JianyingProjects"
    
    def _get_default_state_dir(self) -> Path:
        """
        获取默认状态管理目录
        
        Returns:
            默认状态目录路径
        """
        system = platform.system()
        
        if system == "Windows":
            # Windows: 使用 LOCALAPPDATA
            base = os.getenv("LOCALAPPDATA", Path.home() / "AppData" / "Local")
            return Path(base) / "Coze2JianYing" / "drafts"
        elif system == "Darwin":
            # macOS: 使用 Application Support
            return Path.home() / "Library" / "Application Support" / "Coze2JianYing" / "drafts"
        else:
            # Linux: 使用 .local/share
            return Path.home() / ".local" / "share" / "coze2jianying" / "drafts"
    
    def _get_default_temp_dir(self) -> Path:
        """
        获取默认临时目录
        
        Returns:
            默认临时目录路径
        """
        return Path(tempfile.gettempdir()) / "coze2jianying"
    
    def _ensure_directories(self):
        """确保所有目录存在"""
        dirs = [
            self._drafts_base_dir,
            self._state_base_dir,
            self._assets_base_dir,
            self._temp_dir
        ]
        
        for dir_path in dirs:
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                self.logger.debug(f"目录已准备: {dir_path}")
            except Exception as e:
                self.logger.warning(f"创建目录失败 {dir_path}: {e}")
    
    def detect_jianying_draft_folder(self) -> Optional[str]:
        """
        自动检测剪映草稿文件夹
        
        支持：
        - Windows: LocalAppData 和 Roaming
        - macOS: Application Support
        - Linux: 不支持（返回 None）
        
        Returns:
            检测到的文件夹路径，如果未检测到则返回 None
        """
        system = platform.system()
        
        # Windows 路径
        if system == "Windows":
            windows_paths = [
                Path.home() / "AppData" / "Local" / "JianyingPro" / "User Data" / "Projects" / "com.lveditor.draft",
                Path.home() / "AppData" / "Roaming" / "JianyingPro" / "User Data" / "Projects" / "com.lveditor.draft",
            ]
            
            for path in windows_paths:
                if path.exists() and path.is_dir():
                    self.logger.info(f"检测到剪映草稿文件夹 (Windows): {path}")
                    return str(path)
        
        # macOS 路径
        elif system == "Darwin":
            mac_paths = [
                Path.home() / "Library" / "Containers" / "com.lemon.lvpro" / "Data" / "Library" / "Application Support" / "JianyingPro" / "User Data" / "Projects" / "com.lveditor.draft",
                Path.home() / "Movies" / "JianyingPro" / "User Data" / "Projects" / "com.lveditor.draft",
            ]
            
            for path in mac_paths:
                if path.exists() and path.is_dir():
                    self.logger.info(f"检测到剪映草稿文件夹 (macOS): {path}")
                    return str(path)
        
        # Linux 不支持剪映
        self.logger.warning(f"未能检测到剪映草稿文件夹 ({system})")
        return None
    
    # === 公共 API ===
    
    @property
    def drafts_base_dir(self) -> Path:
        """草稿输出根目录"""
        return self._drafts_base_dir
    
    @property
    def state_base_dir(self) -> Path:
        """状态管理根目录"""
        return self._state_base_dir
    
    @property
    def assets_base_dir(self) -> Path:
        """素材存储根目录"""
        return self._assets_base_dir
    
    @property
    def temp_dir(self) -> Path:
        """临时文件目录"""
        return self._temp_dir
    
    def set_drafts_dir(self, path: str) -> bool:
        """
        设置草稿输出目录
        
        Args:
            path: 新的草稿目录路径
            
        Returns:
            是否成功设置
        """
        try:
            new_path = Path(path)
            new_path.mkdir(parents=True, exist_ok=True)
            
            self._drafts_base_dir = new_path
            self.config["drafts_base_dir"] = str(new_path)
            self.config["auto_detect_jianying"] = False  # 禁用自动检测
            
            # 更新素材目录（如果未自定义）
            if not self.config.get("assets_base_dir"):
                self._assets_base_dir = new_path / "CozeJianYingAssistantAssets"
                self._assets_base_dir.mkdir(parents=True, exist_ok=True)
            
            self._save_config()
            self.logger.info(f"草稿目录已更新: {new_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"设置草稿目录失败: {e}")
            return False
    
    def set_state_dir(self, path: str) -> bool:
        """
        设置状态管理目录
        
        Args:
            path: 新的状态目录路径
            
        Returns:
            是否成功设置
        """
        try:
            new_path = Path(path)
            new_path.mkdir(parents=True, exist_ok=True)
            
            self._state_base_dir = new_path
            self.config["state_base_dir"] = str(new_path)
            
            self._save_config()
            self.logger.info(f"状态目录已更新: {new_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"设置状态目录失败: {e}")
            return False
    
    def set_assets_dir(self, path: str) -> bool:
        """
        设置素材存储目录
        
        Args:
            path: 新的素材目录路径
            
        Returns:
            是否成功设置
        """
        try:
            new_path = Path(path)
            new_path.mkdir(parents=True, exist_ok=True)
            
            self._assets_base_dir = new_path
            self.config["assets_base_dir"] = str(new_path)
            
            self._save_config()
            self.logger.info(f"素材目录已更新: {new_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"设置素材目录失败: {e}")
            return False
    
    def enable_auto_detect(self, enable: bool = True) -> bool:
        """
        启用/禁用剪映路径自动检测
        
        Args:
            enable: 是否启用
            
        Returns:
            是否成功更新
        """
        try:
            self.config["auto_detect_jianying"] = enable
            self._save_config()
            
            if enable:
                # 重新检测
                self._init_paths()
            
            self.logger.info(f"自动检测已{'启用' if enable else '禁用'}")
            return True
            
        except Exception as e:
            self.logger.error(f"更新自动检测设置失败: {e}")
            return False
    
    def reset_to_defaults(self) -> bool:
        """
        重置为默认配置
        
        Returns:
            是否成功重置
        """
        try:
            self.config = self.DEFAULT_CONFIG.copy()
            self._init_paths()
            self._save_config()
            
            self.logger.info("配置已重置为默认值")
            return True
            
        except Exception as e:
            self.logger.error(f"重置配置失败: {e}")
            return False
    
    def get_config_summary(self) -> Dict[str, str]:
        """
        获取配置摘要（用于显示）
        
        Returns:
            配置摘要字典
        """
        return {
            "草稿目录": str(self._drafts_base_dir),
            "状态目录": str(self._state_base_dir),
            "素材目录": str(self._assets_base_dir),
            "临时目录": str(self._temp_dir),
            "自动检测": "启用" if self.config.get("auto_detect_jianying") else "禁用",
            "配置文件": str(self.config_file)
        }


# 全局单例实例
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
    """重置全局存储配置实例（主要用于测试）"""
    global _storage_config
    _storage_config = None
