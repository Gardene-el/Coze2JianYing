"""
剪映草稿元信息管理器
用于扫描草稿文件夹并生成 root_meta_info.json
"""
import os
import json
import time
import uuid
from pathlib import Path
from typing import Dict, List, Any, Optional
from src.utils.logger import get_logger


class DraftMetaManager:
    """剪映草稿元信息管理器"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def scan_and_generate_meta_info(self, draft_root_path: str) -> Dict[str, Any]:
        """
        扫描草稿文件夹并生成 root_meta_info.json 的内容
        
        Args:
            draft_root_path: 草稿根目录路径
            
        Returns:
            root_meta_info.json 的完整内容
        """
        self.logger.info(f"开始扫描草稿文件夹: {draft_root_path}")
        
        # 确保路径存在
        if not os.path.exists(draft_root_path):
            self.logger.error(f"草稿根目录不存在: {draft_root_path}")
            raise FileNotFoundError(f"草稿根目录不存在: {draft_root_path}")
        
        # 扫描所有草稿文件夹
        draft_stores = []
        draft_count = 0
        
        for item in os.listdir(draft_root_path):
            item_path = os.path.join(draft_root_path, item)
            
            # 跳过文件，只处理文件夹
            if not os.path.isdir(item_path):
                continue
            
            # 检查是否为有效的草稿文件夹
            draft_content_path = os.path.join(item_path, "draft_content.json")
            draft_meta_path = os.path.join(item_path, "draft_meta_info.json")
            
            if os.path.exists(draft_content_path) and os.path.exists(draft_meta_path):
                try:
                    draft_info = self._generate_draft_store_info(
                        draft_folder_name=item,
                        draft_folder_path=item_path,
                        draft_root_path=draft_root_path
                    )
                    
                    if draft_info:
                        draft_stores.append(draft_info)
                        draft_count += 1
                        self.logger.info(f"  ✅ 找到草稿: {item}")
                    
                except Exception as e:
                    self.logger.error(f"  ❌ 处理草稿 {item} 失败: {e}")
                    continue
        
        # 生成完整的 root_meta_info 结构
        root_meta_info = {
            "all_draft_store": draft_stores,
            "draft_ids": draft_count,
            "root_path": draft_root_path.replace("\\", "/")  # 统一使用正斜杠
        }
        
        self.logger.info(f"扫描完成，共找到 {draft_count} 个草稿")
        return root_meta_info
    
    def _generate_draft_store_info(
        self,
        draft_folder_name: str,
        draft_folder_path: str,
        draft_root_path: str
    ) -> Optional[Dict[str, Any]]:
        """
        为单个草稿生成 draft_store 信息
        
        Args:
            draft_folder_name: 草稿文件夹名称
            draft_folder_path: 草稿文件夹完整路径
            draft_root_path: 草稿根目录路径
            
        Returns:
            单个草稿的 draft_store 信息
        """
        try:
            # 读取 draft_meta_info.json
            draft_meta_path = os.path.join(draft_folder_path, "draft_meta_info.json")
            with open(draft_meta_path, 'r', encoding='utf-8') as f:
                draft_meta = json.load(f)
            
            # 读取 draft_content.json 获取时长信息
            draft_content_path = os.path.join(draft_folder_path, "draft_content.json")
            duration = self._calculate_draft_duration(draft_content_path)
            
            # 计算素材文件夹大小
            assets_size = self._calculate_assets_size(draft_folder_path)
            
            # 获取草稿封面路径（如果存在）
            draft_cover_path = self._find_draft_cover(draft_folder_path)
            
            # 生成当前时间戳（微秒）
            current_time_us = int(time.time() * 1000000)
            
            # 生成随机的云端ID（模拟）
            cloud_entry_id = int(time.time() * 1000) + hash(draft_folder_name) % 1000000
            
            # 构建 draft_store 信息
            draft_store = {
                "cloud_draft_cover": False,  # 默认本地草稿
                "cloud_draft_sync": False,   # 默认不同步
                "draft_cloud_last_action_download": False,
                "draft_cloud_purchase_info": "",
                "draft_cloud_template_id": "",
                "draft_cloud_tutorial_info": "",
                "draft_cloud_videocut_purchase_info": "",
                "draft_cover": draft_cover_path if draft_cover_path else "",
                "draft_fold_path": draft_folder_path.replace("\\", "/"),
                "draft_id": self._generate_draft_id(),
                "draft_is_ai_shorts": False,
                "draft_is_cloud_temp_draft": False,
                "draft_is_invisible": False,
                "draft_is_web_article_video": False,
                "draft_json_file": draft_content_path.replace("\\", "/"),
                "draft_name": draft_folder_name,
                "draft_new_version": "",
                "draft_root_path": draft_root_path.replace("\\", "/"),
                "draft_timeline_materials_size": assets_size,
                "draft_type": "",
                "draft_web_article_video_enter_from": "",
                "streaming_edit_draft_ready": True,
                "tm_draft_cloud_completed": str(current_time_us),
                "tm_draft_cloud_entry_id": cloud_entry_id,
                "tm_draft_cloud_modified": current_time_us,
                "tm_draft_cloud_parent_entry_id": -1,
                "tm_draft_cloud_space_id": 0,
                "tm_draft_cloud_user_id": 0,  # 默认用户ID
                "tm_draft_create": current_time_us,
                "tm_draft_modified": current_time_us,
                "tm_draft_removed": 0,
                "tm_duration": duration
            }
            
            return draft_store
            
        except Exception as e:
            self.logger.error(f"生成草稿 {draft_folder_name} 的元信息失败: {e}")
            return None
    
    def _calculate_draft_duration(self, draft_content_path: str) -> int:
        """
        从 draft_content.json 计算草稿总时长（微秒）
        
        Args:
            draft_content_path: draft_content.json 文件路径
            
        Returns:
            草稿总时长（微秒）
        """
        try:
            with open(draft_content_path, 'r', encoding='utf-8') as f:
                draft_content = json.load(f)
            
            # 查找所有轨道中的最大结束时间
            max_end_time = 0
            
            tracks = draft_content.get('tracks', [])
            for track in tracks:
                segments = track.get('segments', [])
                for segment in segments:
                    # 从时间范围获取结束时间
                    time_range = segment.get('time_range', {})
                    end_time = time_range.get('end', 0)
                    
                    # pyJianYingDraft 通常使用毫秒，需要转换为微秒
                    if isinstance(end_time, (int, float)):
                        end_time_us = int(end_time * 1000)  # 毫秒转微秒
                        max_end_time = max(max_end_time, end_time_us)
            
            return max_end_time
            
        except Exception as e:
            self.logger.error(f"计算草稿时长失败: {e}")
            return 0
    
    def _calculate_assets_size(self, draft_folder_path: str) -> int:
        """
        计算 Assets 文件夹的总大小（字节）
        
        Args:
            draft_folder_path: 草稿文件夹路径
            
        Returns:
            Assets 文件夹总大小（字节）
        """
        try:
            assets_path = os.path.join(draft_folder_path, "Assets")
            if not os.path.exists(assets_path):
                return 0
            
            total_size = 0
            for root, dirs, files in os.walk(assets_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if os.path.exists(file_path):
                        total_size += os.path.getsize(file_path)
            
            return total_size
            
        except Exception as e:
            self.logger.error(f"计算 Assets 文件夹大小失败: {e}")
            return 0
    
    def _find_draft_cover(self, draft_folder_path: str) -> Optional[str]:
        """
        查找草稿封面图片
        
        Args:
            draft_folder_path: 草稿文件夹路径
            
        Returns:
            封面图片路径，如果不存在则返回None
        """
        try:
            cover_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
            cover_names = ['draft_cover', 'cover', 'thumbnail']
            
            for name in cover_names:
                for ext in cover_extensions:
                    cover_path = os.path.join(draft_folder_path, f"{name}{ext}")
                    if os.path.exists(cover_path):
                        return cover_path.replace("\\", "/")
            
            return None
            
        except Exception as e:
            self.logger.error(f"查找草稿封面失败: {e}")
            return None
    
    def _generate_draft_id(self) -> str:
        """
        生成剪映格式的草稿ID
        
        Returns:
            格式化的草稿ID (如: FD3DD75A-5085-42DA-A47F-93A1CB9A850C)
        """
        return str(uuid.uuid4()).upper()
    
    def save_root_meta_info(self, root_meta_info: Dict[str, Any], output_path: str):
        """
        保存 root_meta_info.json 文件
        
        Args:
            root_meta_info: root_meta_info 数据
            output_path: 输出文件路径
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(root_meta_info, f, ensure_ascii=False, separators=(',', ':'))
            
            self.logger.info(f"✅ root_meta_info.json 已保存到: {output_path}")
            
        except Exception as e:
            self.logger.error(f"保存 root_meta_info.json 失败: {e}")
            raise


def create_draft_meta_manager() -> DraftMetaManager:
    """
    创建草稿元信息管理器实例
    
    Returns:
        DraftMetaManager 实例
    """
    return DraftMetaManager()