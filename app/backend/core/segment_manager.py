"""
片段状态管理器

归属：core/ — 核心领域状态管理，
负责基于 UUID 的片段配置 CRUD 及操作记录追踪（持久化到文件系统）。
"""
import os
import json
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from app.backend.utils.logger import get_logger
from app.backend.config import get_config


class SegmentManager:
    """
    片段状态管理器

    功能:
    1. 创建和管理基于 UUID 的片段配置
    2. 存储片段状态到文件系统
    3. 支持片段的增删改查操作
    4. 追踪片段的下载和处理状态
    """

    def __init__(self, base_dir: Optional[str] = None):
        """
        初始化片段状态管理器

        Args:
            base_dir: 片段存储的基础目录，如果为 None 则使用配置系统的默认路径
        """
        self.logger = get_logger(__name__)

        # 如果没有指定 base_dir，使用配置系统的默认路径
        if base_dir is None:
            config = get_config()
            base_dir = config.segments_dir

        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

        # 内存中的片段状态存储
        self.segments: Dict[str, Dict[str, Any]] = {}

        self.logger.info(f"片段状态管理器已初始化: {self.base_dir}")

    def create_segment(self, segment_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建新的片段

        Args:
            segment_type: 片段类型 (audio/video/text/sticker/effect/filter)
            config: 片段配置

        Returns:
            包含 segment_id 和成功状态的字典
        """
        try:
            # 生成 UUID
            segment_id = str(uuid.uuid4())

            # 创建片段配置
            timestamp = datetime.now().timestamp()
            segment_data = {
                "segment_id": segment_id,
                "segment_type": segment_type,
                "config": config,
                "status": "created",
                "download_status": "pending" if config.get("material_url") else "none",
                "local_path": None,
                "created_timestamp": timestamp,
                "last_modified": timestamp,
                "operations": []  # 记录对片段的操作
            }

            # 保存到内存
            self.segments[segment_id] = segment_data

            # 保存配置文件
            segment_file = self.base_dir / f"{segment_id}.json"
            with open(segment_file, 'w', encoding='utf-8') as f:
                json.dump(segment_data, f, ensure_ascii=False, indent=2)

            self.logger.info(f"片段创建成功: {segment_id} (类型: {segment_type})")

            return {
                "segment_id": segment_id,
                "success": True,
                "message": f"{segment_type} 片段创建成功"
            }

        except Exception as e:
            self.logger.error(f"创建片段失败: {str(e)}")
            return {
                "segment_id": "",
                "success": False,
                "message": f"创建片段失败: {str(e)}"
            }

    def get_segment(self, segment_id: str) -> Optional[Dict[str, Any]]:
        """
        获取片段配置

        Args:
            segment_id: 片段 UUID

        Returns:
            片段配置字典，如果不存在返回 None
        """
        if segment_id in self.segments:
            return self.segments[segment_id]

        # 尝试从文件加载
        segment_file = self.base_dir / f"{segment_id}.json"
        if segment_file.exists():
            try:
                with open(segment_file, 'r', encoding='utf-8') as f:
                    segment_data = json.load(f)
                    self.segments[segment_id] = segment_data
                    return segment_data
            except Exception as e:
                self.logger.error(f"加载片段配置失败: {str(e)}")
                return None

        return None

    def add_operation(self, segment_id: str, operation_type: str, operation_data: Dict[str, Any]) -> bool:
        """
        添加片段操作记录

        Args:
            segment_id: 片段 UUID
            operation_type: 操作类型 (add_effect/add_fade/add_keyframe等)
            operation_data: 操作数据

        Returns:
            是否成功
        """
        segment = self.get_segment(segment_id)
        if not segment:
            self.logger.error(f"片段不存在: {segment_id}")
            return False

        try:
            # 生成操作 ID
            operation_id = str(uuid.uuid4())

            # 添加操作记录
            operation = {
                "operation_id": operation_id,
                "operation_type": operation_type,
                "data": operation_data,
                "timestamp": datetime.now().timestamp()
            }

            segment["operations"].append(operation)
            segment["last_modified"] = datetime.now().timestamp()

            # 保存到文件
            segment_file = self.base_dir / f"{segment_id}.json"
            with open(segment_file, 'w', encoding='utf-8') as f:
                json.dump(segment, f, ensure_ascii=False, indent=2)

            self.logger.info(f"为片段 {segment_id} 添加操作: {operation_type}")
            return True

        except Exception as e:
            self.logger.error(f"添加操作失败: {str(e)}")
            return False

    def update_download_status(self, segment_id: str, status: str, local_path: Optional[str] = None) -> bool:
        """
        更新片段的下载状态

        Args:
            segment_id: 片段 UUID
            status: 下载状态 (pending/downloading/completed/failed)
            local_path: 本地文件路径

        Returns:
            是否成功
        """
        segment = self.get_segment(segment_id)
        if not segment:
            self.logger.error(f"片段不存在: {segment_id}")
            return False

        try:
            segment["download_status"] = status
            if local_path:
                segment["local_path"] = local_path
            segment["last_modified"] = datetime.now().timestamp()

            # 保存到文件
            segment_file = self.base_dir / f"{segment_id}.json"
            with open(segment_file, 'w', encoding='utf-8') as f:
                json.dump(segment, f, ensure_ascii=False, indent=2)

            self.logger.info(f"更新片段 {segment_id} 下载状态: {status}")
            return True

        except Exception as e:
            self.logger.error(f"更新下载状态失败: {str(e)}")
            return False

    def list_segments(self, segment_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        列出所有片段

        Args:
            segment_type: 可选的片段类型过滤

        Returns:
            片段列表
        """
        segments = []
        for segment_id, segment_data in self.segments.items():
            if segment_type is None or segment_data["segment_type"] == segment_type:
                segments.append({
                    "segment_id": segment_id,
                    "segment_type": segment_data["segment_type"],
                    "status": segment_data["status"],
                    "download_status": segment_data["download_status"],
                    "created_timestamp": segment_data["created_timestamp"]
                })

        # 按创建时间倒序排序
        segments.sort(key=lambda x: x["created_timestamp"], reverse=True)
        return segments

    def delete_segment(self, segment_id: str) -> bool:
        """
        删除片段

        Args:
            segment_id: 片段 UUID

        Returns:
            是否成功
        """
        try:
            # 从内存中删除
            if segment_id in self.segments:
                del self.segments[segment_id]

            # 删除文件
            segment_file = self.base_dir / f"{segment_id}.json"
            if segment_file.exists():
                segment_file.unlink()

            self.logger.info(f"片段删除成功: {segment_id}")
            return True

        except Exception as e:
            self.logger.error(f"删除片段失败: {str(e)}")
            return False


# 全局片段管理器实例
_segment_manager = None


def get_segment_manager() -> SegmentManager:
    """获取全局片段管理器实例（单例）"""
    global _segment_manager
    if _segment_manager is None:
        _segment_manager = SegmentManager()
    return _segment_manager
