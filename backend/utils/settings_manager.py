import json
import os
from typing import Any, Dict, Optional
from backend.config import get_config
from backend.utils.logger import get_logger

class SettingsManager:
    """全局设置管理器"""
    
    _instance = None
    
    # 默认剪映草稿路径
    DEFAULT_DRAFT_PATHS = [
        r"C:\Users\{username}\AppData\Local\JianyingPro\User Data\Projects\com.lveditor.draft",
        r"C:\Users\{username}\AppData\Roaming\JianyingPro\User Data\Projects\com.lveditor.draft",
    ]
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SettingsManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.logger = get_logger(__name__)
        self.config = get_config()
        self.settings_file = os.path.join(self.config.data_root, "settings.json")
        self._settings = self._load_settings()
        self._initialized = True
        
    def _load_settings(self) -> Dict[str, Any]:
        """加载设置"""
        if not os.path.exists(self.settings_file):
            return self._get_default_settings()
            
        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return self._get_default_settings()
            
    def _get_default_settings(self) -> Dict[str, Any]:
        """获取默认设置"""
        return {
            "draft_folder": "",
            "api_port": "8000",
            "ngrok_auth_token": "",
            "ngrok_region": "us",
            "theme_mode": "System",  # System, Dark, Light
            "color_theme": "blue",   # blue, green, dark-blue
            "transfer_enabled": False
        }
        
    def save_settings(self):
        """保存设置"""
        try:
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, indent=4, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Error saving settings: {e}")
            
    def reload(self):
        """重新加载设置"""
        self._settings = self._load_settings()
        self.logger.info("设置已重新加载")
        
    def get(self, key: str, default: Any = None) -> Any:
        """获取设置值"""
        return self._settings.get(key, default)
        
    def set(self, key: str, value: Any):
        """设置值"""
        self._settings[key] = value
        self.save_settings()
        
    def get_all(self) -> Dict[str, Any]:
        """获取所有设置"""
        return self._settings.copy()

    def get_effective_output_path(self) -> str:
        """
        获取实际的输出路径
        
        根据当前设置返回实际应该使用的输出路径：
        - 如果启用传输且设置了草稿文件夹，返回草稿文件夹路径
        - 否则返回本地数据目录（config.drafts_dir）
        
        Returns:
            实际的输出路径
        """
        transfer_enabled = self.get("transfer_enabled", False)
        draft_folder = self.get("draft_folder", "")
        
        if transfer_enabled and draft_folder:
            # 验证路径有效性
            if os.path.exists(draft_folder) and os.path.isdir(draft_folder):
                self.logger.info(f"使用指定的草稿文件夹: {draft_folder}")
                return draft_folder
            else:
                self.logger.warning(f"指定的草稿文件夹无效: {draft_folder}，使用本地数据目录")
        
        # 使用本地数据目录
        local_path = self.config.drafts_dir
        self.logger.info(f"使用本地数据目录: {local_path}")
        return local_path
    
    def get_effective_assets_path(self, draft_id: Optional[str] = None) -> str:
        """
        获取实际的素材存储路径
        
        根据当前设置返回实际应该使用的素材存储路径：
        - 如果启用传输且设置了草稿文件夹，返回草稿文件夹下的CozeJianYingAssistantAssets目录
        - 否则返回本地数据目录下的assets/{draft_id}目录
        
        Args:
            draft_id: 草稿ID，用于本地存储时创建子目录
            
        Returns:
            实际的素材存储路径
        """
        transfer_enabled = self.get("transfer_enabled", False)
        draft_folder = self.get("draft_folder", "")

        if transfer_enabled and draft_folder:
            # 验证路径有效性
            if os.path.exists(draft_folder) and os.path.isdir(draft_folder):
                # 使用草稿文件夹下的CozeJianYingAssistantAssets目录
                assets_path = os.path.join(
                    os.path.dirname(draft_folder),
                    "CozeJianYingAssistantAssets"
                )
                os.makedirs(assets_path, exist_ok=True)
                self.logger.info(f"使用草稿文件夹的素材目录: {assets_path}")
                return assets_path
        
        # 使用本地数据目录
        if draft_id:
            assets_path = os.path.join(self.config.assets_dir, draft_id)
        else:
            assets_path = self.config.assets_dir
        
        os.makedirs(assets_path, exist_ok=True)
        self.logger.info(f"使用本地素材目录: {assets_path}")
        return assets_path
    
    def detect_default_draft_folder(self) -> Optional[str]:
        """
        自动检测剪映草稿文件夹
        
        Returns:
            检测到的文件夹路径，如果未检测到则返回None
        """
        username = os.getenv('USERNAME') or os.getenv('USER')
        
        for path_template in self.DEFAULT_DRAFT_PATHS:
            path = path_template.format(username=username)
            if os.path.exists(path) and os.path.isdir(path):
                self.logger.info(f"检测到剪映草稿文件夹: {path}")
                return path
        
        self.logger.warning("未能检测到剪映草稿文件夹")
        return None

def get_settings_manager() -> SettingsManager:
    """获取设置管理器实例"""
    return SettingsManager()

