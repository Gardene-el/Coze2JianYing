"""
草稿保存器
将 DraftStateManager 和 SegmentManager 的数据转换为 pyJianYingDraft 调用并保存
"""
import os
import tempfile
import requests
from pathlib import Path
from typing import Dict, Any, Optional
import pyJianYingDraft as draft
from pyJianYingDraft import IntroType, TransitionType, trange, tim, TextOutro

from app.utils.logger import get_logger
from app.utils.draft_state_manager import get_draft_state_manager
from app.utils.segment_manager import get_segment_manager
from app.utils.storage_settings import get_storage_settings
from app.config import get_config


class DraftSaver:
    """将 DraftStateManager/SegmentManager 数据转换为 pyJianYingDraft 并保存"""
    
    def __init__(self, output_dir: str = None):
        """
        初始化草稿保存器
        
        Args:
            output_dir: 输出目录，如果为None则使用配置系统的drafts目录
        """
        self.logger = get_logger(__name__)
        
        # 如果没有指定输出目录，使用配置系统的drafts目录
        if output_dir is None:
            config = get_config()
            self.output_dir = config.drafts_dir
        else:
            self.output_dir = output_dir
            
        os.makedirs(self.output_dir, exist_ok=True)
        self.draft_manager = get_draft_state_manager()
        self.segment_manager = get_segment_manager()
        
    def download_material(self, url: str, save_dir: str) -> str:
        """
        下载素材文件
        
        Args:
            url: 素材URL
            save_dir: 保存目录
            
        Returns:
            本地文件路径
        """
        filename = url.split('/')[-1]
        save_path = os.path.join(save_dir, filename)
        
        if os.path.exists(save_path):
            self.logger.info(f"素材已存在: {filename}")
            return save_path
        
        self.logger.info(f"下载素材: {filename}")
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            self.logger.info(f"素材下载完成: {save_path}")
            return save_path
        except Exception as e:
            self.logger.error(f"下载素材失败 {url}: {e}")
            raise
    
    def save_draft(self, draft_id: str) -> str:
        """
        保存草稿为 pyJianYingDraft 格式
        
        Args:
            draft_id: 草稿UUID
            
        Returns:
            草稿文件夹路径
        """
        self.logger.info(f"开始保存草稿: {draft_id}")
        
        # 获取草稿配置
        config = self.draft_manager.get_draft_config(draft_id)
        if not config:
            raise ValueError(f"草稿不存在: {draft_id}")
        
        # 提取项目信息
        project = config.get("project", {})
        draft_name = project.get("name", "Untitled")
        width = project.get("width", 1920)
        height = project.get("height", 1080)
        fps = project.get("fps", 30)
        
        self.logger.info(f"项目: {draft_name}, {width}x{height}@{fps}fps")
        
        # 读取全局存储设置
        storage_settings = get_storage_settings()
        use_local_storage = storage_settings.get_use_local_storage()
        
        self.logger.info(f"存储模式: {'本地数据目录' if use_local_storage else '指定文件夹+CozeJianYingAssistantAssets'}")
        
        # 根据存储模式选择输出目录和素材目录
        app_config = get_config()
        
        if use_local_storage:
            # 本地存储模式：使用 config.drafts_dir 和 config.assets_dir
            draft_output_dir = self.output_dir or app_config.drafts_dir
            temp_assets_dir = os.path.join(app_config.assets_dir, draft_id)
            os.makedirs(temp_assets_dir, exist_ok=True)
            self.logger.info(f"本地存储 - 草稿: {draft_output_dir}, 素材: {temp_assets_dir}")
        else:
            # 传输模式：使用指定文件夹 + CozeJianYingAssistantAssets
            target_folder = storage_settings.get_output_folder()
            if target_folder:
                draft_output_dir = target_folder
                # 素材将通过 MaterialManager 存储到 CozeJianYingAssistantAssets
                temp_assets_dir = None  # 标记使用 CozeJianYingAssistantAssets 模式
                self.logger.info(f"传输存储 - 草稿: {draft_output_dir}, 素材: CozeJianYingAssistantAssets")
            else:
                # 如果没有设置目标文件夹，回退到本地存储
                self.logger.warning("传输模式但未设置目标文件夹，回退到本地存储")
                draft_output_dir = self.output_dir or app_config.drafts_dir
                temp_assets_dir = os.path.join(app_config.assets_dir, draft_id)
                os.makedirs(temp_assets_dir, exist_ok=True)
        
        # 创建 DraftFolder 和 Script
        draft_folder = draft.DraftFolder(draft_output_dir)
        script = draft_folder.create_draft(draft_name, width, height, fps, allow_replace=True)
        
        # 处理轨道
        tracks = config.get("tracks", [])
        track_type_map = {
            "audio": draft.TrackType.audio,
            "video": draft.TrackType.video,
            "text": draft.TrackType.text,
            "sticker": draft.TrackType.sticker
        }
        
        # 添加轨道
        for track in tracks:
            track_type = track.get("track_type")
            if track_type in track_type_map:
                script.add_track(track_type_map[track_type])
                self.logger.info(f"添加轨道: {track_type}")
        
        # 处理所有片段
        for track in tracks:
            track_type = track.get("track_type")
            segments = track.get("segments", [])
            
            for segment_id in segments:
                segment = self.segment_manager.get_segment(segment_id)
                if not segment:
                    self.logger.warning(f"片段不存在: {segment_id}")
                    continue
                
                segment_type = segment.get("segment_type")
                config_data = segment.get("config", {})
                operations = segment.get("operations", [])
                
                # 创建片段 - 传递素材目录和存储模式信息
                seg = self._create_segment(
                    segment_type, 
                    config_data, 
                    temp_assets_dir,
                    draft_folder=draft_folder if temp_assets_dir is None else None,
                    draft_id=draft_id
                )
                if seg:
                    # 应用操作
                    self._apply_operations(seg, operations)
                    # 添加到脚本
                    script.add_segment(seg)
                    self.logger.info(f"添加片段: {segment_type} ({segment_id})")
        
        # 保存草稿
        script.save()
        draft_path = os.path.join(draft_output_dir, draft_name)
        
        self.logger.info(f"草稿保存成功: {draft_path}")
        return draft_path
    
    def _create_segment(self, segment_type: str, config: Dict[str, Any], assets_dir: Optional[str], 
                       draft_folder=None, draft_id: str = None):
        """
        创建片段对象
        
        Args:
            segment_type: 片段类型
            config: 片段配置
            assets_dir: 本地存储模式的素材目录，如果为 None 则使用 CozeJianYingAssistantAssets 模式
            draft_folder: DraftFolder 对象（CozeJianYingAssistantAssets 模式需要）
            draft_id: 草稿ID（CozeJianYingAssistantAssets 模式需要）
        """
        try:
            material_url = config.get("material_url")
            target_timerange = config.get("target_timerange", {})
            start = target_timerange.get("start", 0)
            duration = target_timerange.get("duration", 1000000)
            
            # 转换微秒到秒字符串
            start_sec = start / 1000000
            duration_sec = duration / 1000000
            
            # 处理需要下载素材的片段类型
            if segment_type in ["audio", "video"] and material_url:
                # 根据存储模式选择下载位置
                if assets_dir is not None:
                    # 本地存储模式：下载到 assets_dir
                    local_path = self.download_material(material_url, assets_dir)
                else:
                    # CozeJianYingAssistantAssets 模式：使用 MaterialManager
                    from app.utils.material_manager import create_material_manager
                    material_manager = create_material_manager(
                        draft_folder=draft_folder,
                        draft_name=draft_folder.folder_path.name if draft_folder else "",
                        project_id=draft_id
                    )
                    # 下载并获取 Material 对象
                    if segment_type == "video":
                        material = material_manager.get_video_material(material_url)
                        local_path = material.path
                    else:  # audio
                        material = material_manager.get_audio_material(material_url)
                        local_path = material.path
                
                if segment_type == "audio":
                    volume = config.get("volume", 1.0)
                    seg = draft.AudioSegment(
                        local_path,
                        trange(f"{start_sec}s", f"{duration_sec}s"),
                        volume=volume
                    )
                    return seg
                    
                elif segment_type == "video":
                    seg = draft.VideoSegment(
                        local_path,
                        trange(f"{start_sec}s", f"{duration_sec}s")
                    )
                    return seg
                
            elif segment_type == "text":
                # 文本片段
                text_content = config.get("text_content", "")
                font_family = config.get("font_family", "黑体")
                color = config.get("color", "#FFFFFF")
                position = config.get("position", {})
                
                # 转换颜色
                hex_color = color.lstrip('#')
                r = int(hex_color[0:2], 16) / 255.0
                g = int(hex_color[2:4], 16) / 255.0
                b = int(hex_color[4:6], 16) / 255.0
                
                # 创建文本片段
                text_timerange = trange(f"{start_sec}s", f"{duration_sec}s")
                
                # 获取字体类型
                try:
                    font_type = getattr(draft.FontType, font_family, None)
                    if not font_type:
                        font_type = draft.FontType.黑体
                except:
                    font_type = draft.FontType.黑体
                
                seg = draft.TextSegment(
                    text_content,
                    text_timerange,
                    font=font_type,
                    style=draft.TextStyle(color=(r, g, b)),
                    clip_settings=draft.ClipSettings(
                        transform_y=position.get("y", 0.0)
                    )
                )
                return seg
                
            else:
                self.logger.warning(f"不支持的片段类型: {segment_type}")
                return None
                
        except Exception as e:
            self.logger.error(f"创建片段失败: {e}", exc_info=True)
            return None
    
    def _apply_operations(self, seg, operations):
        """应用操作到片段"""
        for op in operations:
            op_type = op.get("operation_type")
            op_data = op.get("data", {})
            
            try:
                if op_type == "add_fade":
                    # 淡入淡出
                    fade_in = op_data.get("in_duration", "0s")
                    fade_out = op_data.get("out_duration", "0s")
                    seg.add_fade(fade_in, fade_out)
                    self.logger.info(f"应用淡入淡出: {fade_in}, {fade_out}")
                    
                elif op_type == "add_animation":
                    # 动画
                    animation_type = op_data.get("animation_type", "")
                    duration = op_data.get("duration", "1s")
                    
                    # 尝试获取动画类型
                    try:
                        if hasattr(seg, "add_animation"):
                            # 视频或文本动画
                            if "IntroType" in str(type(seg)):
                                anim = getattr(IntroType, animation_type, None)
                            else:
                                anim = getattr(TextOutro, animation_type, None)
                            
                            if anim:
                                if duration:
                                    seg.add_animation(anim, duration=tim(duration))
                                else:
                                    seg.add_animation(anim)
                                self.logger.info(f"应用动画: {animation_type}")
                    except Exception as e:
                        self.logger.warning(f"应用动画失败: {e}")
                    
                elif op_type == "add_transition":
                    # 转场
                    transition_type = op_data.get("transition_type", "")
                    try:
                        trans = getattr(TransitionType, transition_type, None)
                        if trans and hasattr(seg, "add_transition"):
                            seg.add_transition(trans)
                            self.logger.info(f"应用转场: {transition_type}")
                    except Exception as e:
                        self.logger.warning(f"应用转场失败: {e}")
                    
                elif op_type == "add_background_filling":
                    # 背景填充
                    fill_type = op_data.get("fill_type", "blur")
                    blur = op_data.get("blur", 0.0625)
                    if hasattr(seg, "add_background_filling"):
                        seg.add_background_filling(fill_type, blur)
                        self.logger.info(f"应用背景填充: {fill_type}")
                    
                elif op_type == "add_bubble":
                    # 气泡效果
                    effect_id = op_data.get("effect_id", "")
                    resource_id = op_data.get("resource_id", "")
                    if hasattr(seg, "add_bubble"):
                        seg.add_bubble(effect_id, resource_id)
                        self.logger.info(f"应用气泡效果")
                    
                elif op_type == "add_effect":
                    # 特效
                    effect_id = op_data.get("effect_id", "")
                    if hasattr(seg, "add_effect"):
                        seg.add_effect(effect_id)
                        self.logger.info(f"应用特效: {effect_id}")
                    
            except Exception as e:
                self.logger.error(f"应用操作失败 {op_type}: {e}")


def get_draft_saver(output_dir: str = None) -> DraftSaver:
    """获取草稿保存器实例"""
    return DraftSaver(output_dir)
