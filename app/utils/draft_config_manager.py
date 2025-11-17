"""
草稿配置管理器
管理全局草稿文件夹路径和传输选项
"""
import os
from typing import Optional
from pathlib import Path
from app.utils.logger import get_logger
from app.config import get_config


class DraftConfigManager:
    """
    草稿配置管理器 - 单例模式
    
    管理全局的草稿文件夹路径和是否传输到草稿文件夹的选项
    """
    
    _instance: Optional['DraftConfigManager'] = None
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super(DraftConfigManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """初始化配置管理器"""
        if self._initialized:
            return
            
        self.logger = get_logger(__name__)
        
        # 草稿文件夹路径（用户指定的剪映草稿文件夹）
        self._draft_folder_path: Optional[str] = None
        
        # 是否传输到草稿文件夹（True=传输到指定文件夹，False=存储到本地数据目录）
        self._transfer_to_draft_folder: bool = False
        
        # 应用配置
        self._app_config = get_config()
        
        self._initialized = True
        self.logger.info("草稿配置管理器已初始化")
    
    @property
    def draft_folder_path(self) -> Optional[str]:
        """获取草稿文件夹路径"""
        return self._draft_folder_path
    
    @draft_folder_path.setter
    def draft_folder_path(self, path: Optional[str]):
        """设置草稿文件夹路径"""
        if path:
            path = os.path.abspath(path)
        self._draft_folder_path = path
        self.logger.info(f"草稿文件夹路径已更新: {path}")
    
    @property
    def transfer_to_draft_folder(self) -> bool:
        """获取是否传输到草稿文件夹"""
        return self._transfer_to_draft_folder
    
    @transfer_to_draft_folder.setter
    def transfer_to_draft_folder(self, value: bool):
        """设置是否传输到草稿文件夹"""
        self._transfer_to_draft_folder = value
        self.logger.info(f"传输到草稿文件夹选项已更新: {value}")
    
    def get_effective_output_path(self) -> str:
        """
        获取有效的输出路径
        
        根据配置决定使用哪个路径：
        - 如果勾选传输且指定了路径：使用指定的草稿文件夹
        - 否则：使用本地数据目录
        
        Returns:
            有效的输出路径
        """
        if self._transfer_to_draft_folder and self._draft_folder_path:
            # 使用指定的草稿文件夹
            path = self._draft_folder_path
            self.logger.info(f"使用指定草稿文件夹: {path}")
            return path
        else:
            # 使用本地数据目录
            path = self._app_config.drafts_dir
            self.logger.info(f"使用本地数据目录: {path}")
            return path
    
    def get_assets_base_path(self) -> str:
        """
        获取素材基础路径
        
        Returns:
            素材基础路径
        """
        if self._transfer_to_draft_folder and self._draft_folder_path:
            # 使用手动草稿生成方案：CozeJianYingAssistantAssets
            return self._draft_folder_path
        else:
            # 使用云端服务/脚本执行方案：本地数据的assets目录
            return self._app_config.assets_dir
    
    def validate_draft_folder_path(self) -> tuple[bool, str]:
        """
        验证草稿文件夹路径是否有效
        
        Returns:
            (是否有效, 错误消息)
        """
        if not self._draft_folder_path:
            return False, "未指定草稿文件夹路径"
        
        if not os.path.exists(self._draft_folder_path):
            return False, f"路径不存在: {self._draft_folder_path}"
        
        if not os.path.isdir(self._draft_folder_path):
            return False, f"路径不是文件夹: {self._draft_folder_path}"
        
        return True, ""
    
    def reset(self):
        """重置配置为默认值"""
        self._draft_folder_path = None
        self._transfer_to_draft_folder = False
        self.logger.info("草稿配置已重置")


# 全局访问函数
def get_draft_config_manager() -> DraftConfigManager:
    """
    获取草稿配置管理器实例（单例）
    
    Returns:
        DraftConfigManager 实例
    """
    return DraftConfigManager()
