"""
草稿状态管理器
管理基于 UUID 的草稿配置、状态和素材下载
"""
import os
import json
import uuid
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from app.utils.logger import get_logger
from app.config import get_config


class DraftStateManager:
    """
    草稿状态管理器
    
    功能:
    1. 创建和管理基于 UUID 的草稿配置
    2. 存储草稿状态到文件系统（/tmp 或指定目录）
    3. 支持草稿的增删改查操作
    4. 追踪素材下载状态
    """
    
    def __init__(self, base_dir: Optional[str] = None):
        """
        初始化草稿状态管理器
        
        Args:
            base_dir: 草稿存储的基础目录，如果为 None 则使用配置系统的 cache 目录
        """
        self.logger = get_logger(__name__)
        
        # 如果没有指定 base_dir，使用配置系统的 cache 目录
        # draft_config.json 是内部状态管理文件，应该存储在 cache 中
        if base_dir is None:
            config = get_config()
            base_dir = config.cache_dir
        
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.logger.info(f"草稿状态管理器已初始化: {self.base_dir}")
    
    def create_draft(self, draft_name: str, width: int, height: int, fps: int) -> Dict[str, Any]:
        """
        创建新的草稿
        
        Args:
            draft_name: 项目名称
            width: 视频宽度
            height: 视频高度
            fps: 帧率
            
        Returns:
            包含 draft_id 和成功状态的字典
        """
        try:
            # 生成 UUID
            draft_id = str(uuid.uuid4())
            
            # 创建草稿文件夹
            draft_folder = self.base_dir / draft_id
            draft_folder.mkdir(parents=True, exist_ok=True)
            
            # 创建初始配置
            timestamp = datetime.now().timestamp()
            config = {
                "draft_id": draft_id,
                "project": {
                    "name": draft_name,
                    "width": width,
                    "height": height,
                    "fps": fps
                },
                "media_resources": [],
                "tracks": [],
                "created_timestamp": timestamp,
                "last_modified": timestamp,
                "status": "created"
            }
            
            # 保存配置文件
            config_path = draft_folder / "draft_config.json"
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"草稿创建成功: {draft_id}")
            
            return {
                "draft_id": draft_id,
                "success": True,
                "message": f"草稿创建成功，ID: {draft_id}"
            }
            
        except Exception as e:
            self.logger.error(f"创建草稿失败: {str(e)}")
            return {
                "draft_id": "",
                "success": False,
                "message": f"创建草稿失败: {str(e)}"
            }
    
    def get_draft_config(self, draft_id: str) -> Optional[Dict[str, Any]]:
        """
        获取草稿配置
        
        Args:
            draft_id: 草稿 UUID
            
        Returns:
            草稿配置字典，如果不存在则返回 None
        """
        try:
            config_path = self.base_dir / draft_id / "draft_config.json"
            
            if not config_path.exists():
                self.logger.warning(f"草稿配置不存在: {draft_id}")
                return None
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            return config
            
        except Exception as e:
            self.logger.error(f"读取草稿配置失败: {str(e)}")
            return None
    
    def update_draft_config(self, draft_id: str, config: Dict[str, Any]) -> bool:
        """
        更新草稿配置
        
        Args:
            draft_id: 草稿 UUID
            config: 新的配置字典
            
        Returns:
            是否成功更新
        """
        try:
            config_path = self.base_dir / draft_id / "draft_config.json"
            
            # 更新最后修改时间
            config["last_modified"] = datetime.now().timestamp()
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"草稿配置已更新: {draft_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"更新草稿配置失败: {str(e)}")
            return False
    
    def add_track(self, draft_id: str, track_type: str, segments: List[Dict[str, Any]]) -> bool:
        """
        向草稿添加轨道
        
        Args:
            draft_id: 草稿 UUID
            track_type: 轨道类型 (video, audio, text, image 等)
            segments: 片段配置列表
            
        Returns:
            是否成功添加
        """
        try:
            config = self.get_draft_config(draft_id)
            if config is None:
                self.logger.error(f"草稿不存在: {draft_id}")
                return False
            
            # 添加新轨道
            track = {
                "type": track_type,
                "segments": segments,
                "created_at": datetime.now().timestamp()
            }
            
            config["tracks"].append(track)
            
            # 记录素材资源
            for segment in segments:
                if "material_url" in segment:
                    material_entry = {
                        "url": segment["material_url"],
                        "type": track_type,
                        "download_status": "pending",
                        "added_at": datetime.now().timestamp()
                    }
                    config["media_resources"].append(material_entry)
            
            # 更新配置
            return self.update_draft_config(draft_id, config)
            
        except Exception as e:
            self.logger.error(f"添加轨道失败: {str(e)}")
            return False
    
    def update_material_status(self, draft_id: str, material_url: str, status: str, local_path: Optional[str] = None) -> bool:
        """
        更新素材下载状态
        
        Args:
            draft_id: 草稿 UUID
            material_url: 素材 URL
            status: 下载状态 (pending, downloading, completed, failed)
            local_path: 本地文件路径（下载完成后）
            
        Returns:
            是否成功更新
        """
        try:
            config = self.get_draft_config(draft_id)
            if config is None:
                return False
            
            # 查找并更新素材状态
            for resource in config["media_resources"]:
                if resource["url"] == material_url:
                    resource["download_status"] = status
                    resource["updated_at"] = datetime.now().timestamp()
                    if local_path:
                        resource["local_path"] = local_path
                    break
            
            return self.update_draft_config(draft_id, config)
            
        except Exception as e:
            self.logger.error(f"更新素材状态失败: {str(e)}")
            return False
    
    def get_download_status(self, draft_id: str) -> Dict[str, int]:
        """
        获取草稿的素材下载状态统计
        
        Args:
            draft_id: 草稿 UUID
            
        Returns:
            包含 total, completed, failed, pending 的字典
        """
        config = self.get_draft_config(draft_id)
        if config is None:
            return {
                "total": 0,
                "completed": 0,
                "failed": 0,
                "pending": 0
            }
        
        resources = config.get("media_resources", [])
        
        status_counts = {
            "total": len(resources),
            "completed": 0,
            "failed": 0,
            "pending": 0
        }
        
        for resource in resources:
            status = resource.get("download_status", "pending")
            if status == "completed":
                status_counts["completed"] += 1
            elif status == "failed":
                status_counts["failed"] += 1
            elif status in ["pending", "downloading"]:
                status_counts["pending"] += 1
        
        return status_counts
    
    def list_all_drafts(self) -> List[str]:
        """
        列出所有草稿的 UUID
        
        Returns:
            草稿 UUID 列表
        """
        try:
            draft_ids = []
            
            if not self.base_dir.exists():
                return draft_ids
            
            for item in self.base_dir.iterdir():
                if item.is_dir():
                    config_path = item / "draft_config.json"
                    if config_path.exists():
                        draft_ids.append(item.name)
            
            self.logger.info(f"找到 {len(draft_ids)} 个草稿")
            return draft_ids
            
        except Exception as e:
            self.logger.error(f"列出草稿失败: {str(e)}")
            return []
    
    def delete_draft(self, draft_id: str) -> bool:
        """
        删除草稿
        
        Args:
            draft_id: 草稿 UUID
            
        Returns:
            是否成功删除
        """
        try:
            draft_folder = self.base_dir / draft_id
            
            if not draft_folder.exists():
                self.logger.warning(f"草稿不存在: {draft_id}")
                return False
            
            import shutil
            shutil.rmtree(draft_folder)
            
            self.logger.info(f"草稿已删除: {draft_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"删除草稿失败: {str(e)}")
            return False
    
    def export_draft(self, draft_id: str) -> Optional[Dict[str, Any]]:
        """
        导出草稿配置（用于草稿生成器）
        
        Args:
            draft_id: 草稿 UUID
            
        Returns:
            完整的草稿配置，如果不存在则返回 None
        """
        config = self.get_draft_config(draft_id)
        
        if config is None:
            self.logger.error(f"无法导出草稿，配置不存在: {draft_id}")
            return None
        
        # 检查所有素材是否已下载
        download_status = self.get_download_status(draft_id)
        if download_status["pending"] > 0 or download_status["failed"] > 0:
            self.logger.warning(
                f"草稿 {draft_id} 有未完成的下载: "
                f"pending={download_status['pending']}, failed={download_status['failed']}"
            )
        
        self.logger.info(f"草稿已导出: {draft_id}")
        return config
    
    def export_all_drafts(self) -> List[Dict[str, Any]]:
        """
        导出所有草稿配置
        
        Returns:
            草稿配置列表
        """
        draft_ids = self.list_all_drafts()
        
        configs = []
        for draft_id in draft_ids:
            config = self.export_draft(draft_id)
            if config:
                configs.append(config)
        
        self.logger.info(f"已导出 {len(configs)} 个草稿")
        return configs


# 全局单例实例
_draft_state_manager: Optional[DraftStateManager] = None


def get_draft_state_manager(base_dir: Optional[str] = None) -> DraftStateManager:
    """
    获取全局草稿状态管理器实例（单例模式）
    
    Args:
        base_dir: 草稿存储的基础目录，如果为 None 则使用配置系统的默认路径
        
    Returns:
        DraftStateManager 实例
    """
    global _draft_state_manager
    
    if _draft_state_manager is None:
        _draft_state_manager = DraftStateManager(base_dir)
    
    return _draft_state_manager
