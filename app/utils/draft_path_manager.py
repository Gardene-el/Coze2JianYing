"""
草稿路径管理器模块

提供全局的草稿文件夹路径管理，统一管理所有草稿生成场景的输出路径
"""
import os
from typing import Optional
from app.utils.logger import get_logger
from app.config import get_config


class DraftPathManager:
    """草稿路径管理器 - 单例模式"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """初始化路径管理器"""
        if self._initialized:
            return
        
        self.logger = get_logger(__name__)
        self.config = get_config()
        
        # 草稿文件夹路径（剪映草稿文件夹）
        self._draft_folder_path: Optional[str] = None
        
        # 是否传输草稿到指定文件夹
        self._transfer_to_jianying: bool = False
        
        # 默认剪映草稿路径
        self.DEFAULT_DRAFT_PATHS = [
            r"C:\Users\{username}\AppData\Local\JianyingPro\User Data\Projects\com.lveditor.draft",
            r"C:\Users\{username}\AppData\Roaming\JianyingPro\User Data\Projects\com.lveditor.draft",
        ]
        
        self._initialized = True
        self.logger.info("草稿路径管理器已初始化")
    
    def set_draft_folder(self, path: Optional[str]):
        """
        设置草稿文件夹路径
        
        Args:
            path: 草稿文件夹路径，如果为None则清除设置
        """
        if path:
            path = os.path.abspath(path)
            if not os.path.exists(path):
                self.logger.warning(f"路径不存在: {path}")
            elif not os.path.isdir(path):
                self.logger.warning(f"路径不是文件夹: {path}")
        
        self._draft_folder_path = path
        self.logger.info(f"草稿文件夹路径已设置: {path}")
    
    def get_draft_folder(self) -> Optional[str]:
        """
        获取草稿文件夹路径
        
        Returns:
            草稿文件夹路径，如果未设置则返回None
        """
        return self._draft_folder_path
    
    def set_transfer_enabled(self, enabled: bool):
        """
        设置是否传输草稿到指定文件夹
        
        Args:
            enabled: True表示传输到指定文件夹，False表示使用本地数据目录
        """
        self._transfer_to_jianying = enabled
        self.logger.info(f"传输草稿到指定文件夹: {'启用' if enabled else '禁用'}")
    
    def is_transfer_enabled(self) -> bool:
        """
        获取是否传输草稿到指定文件夹
        
        Returns:
            True表示传输到指定文件夹，False表示使用本地数据目录
        """
        return self._transfer_to_jianying
    
    def get_effective_output_path(self) -> str:
        """
        获取实际的输出路径
        
        根据当前设置返回实际应该使用的输出路径：
        - 如果启用传输且设置了草稿文件夹，返回草稿文件夹路径
        - 否则返回本地数据目录（config.drafts_dir）
        
        Returns:
            实际的输出路径
        """
        if self._transfer_to_jianying and self._draft_folder_path:
            # 验证路径有效性
            if os.path.exists(self._draft_folder_path) and os.path.isdir(self._draft_folder_path):
                self.logger.info(f"使用指定的草稿文件夹: {self._draft_folder_path}")
                return self._draft_folder_path
            else:
                self.logger.warning(f"指定的草稿文件夹无效: {self._draft_folder_path}，使用本地数据目录")
        
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
        if self._transfer_to_jianying and self._draft_folder_path:
            # 验证路径有效性
            if os.path.exists(self._draft_folder_path) and os.path.isdir(self._draft_folder_path):
                # 使用草稿文件夹下的CozeJianYingAssistantAssets目录
                assets_path = os.path.join(
                    os.path.dirname(self._draft_folder_path),
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
    
    def get_status_text(self) -> str:
        """
        获取当前状态的描述文本
        
        Returns:
            状态描述文本
        """
        if self._transfer_to_jianying:
            if self._draft_folder_path:
                return f"传输至剪映: {self._draft_folder_path}"
            else:
                return "传输至剪映: 未设置路径"
        else:
            return f"本地数据: {self.config.drafts_dir}"


# 全局单例访问函数
_draft_path_manager_instance: Optional[DraftPathManager] = None


def get_draft_path_manager() -> DraftPathManager:
    """
    获取全局草稿路径管理器实例（单例模式）
    
    Returns:
        DraftPathManager 实例
    """
    global _draft_path_manager_instance
    
    if _draft_path_manager_instance is None:
        _draft_path_manager_instance = DraftPathManager()
    
    return _draft_path_manager_instance
