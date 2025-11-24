"""
草稿保存器
将 DraftStateManager 和 SegmentManager 的数据转换为 pyJianYingDraft 调用并保存
"""

import os
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional

import pyJianYingDraft as draft
import requests
from pyJianYingDraft import (
    ClipSettings,
    CropSettings,
    FilterType,
    IntroType,
    OutroType,
    GroupAnimationType,
    TextIntro,
    TextOutro,
    TextLoopAnim,
    TransitionType,
    VideoSceneEffectType,
    tim,
    trange,
    VideoSegment,
    TextSegment
)

from app.config import get_config
from app.utils.draft_path_manager import get_draft_path_manager
from app.utils.draft_state_manager import get_draft_state_manager
from app.utils.logger import get_logger
from app.utils.segment_manager import get_segment_manager


class DraftSaver:
    """将 DraftStateManager/SegmentManager 数据转换为 pyJianYingDraft 并保存"""

    def __init__(self, output_dir: str = None):
        """
        初始化草稿保存器

        Args:
            output_dir: 输出目录，如果为None则使用全局路径管理器的配置
        """
        self.logger = get_logger(__name__)

        # 如果没有指定输出目录，使用全局路径管理器的配置
        if output_dir is None:
            path_manager = get_draft_path_manager()
            self.output_dir = path_manager.get_effective_output_path()
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
        filename = url.split("/")[-1]
        save_path = os.path.join(save_dir, filename)

        if os.path.exists(save_path):
            self.logger.info(f"素材已存在: {filename}")
            return save_path

        self.logger.info(f"下载素材: {filename}")
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            with open(save_path, "wb") as f:
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

        # 创建素材目录 - 使用全局路径管理器的素材路径配置
        path_manager = get_draft_path_manager()
        temp_assets_dir = path_manager.get_effective_assets_path(draft_id)
        os.makedirs(temp_assets_dir, exist_ok=True)

        # 创建 DraftFolder 和 Script
        draft_folder = draft.DraftFolder(self.output_dir)
        script = draft_folder.create_draft(
            draft_name, width, height, fps, allow_replace=True
        )

        # 处理轨道
        tracks = config.get("tracks", [])
        track_type_map = {
            "audio": draft.TrackType.audio,
            "video": draft.TrackType.video,
            "text": draft.TrackType.text,
            "sticker": draft.TrackType.sticker,
        }

        # 添加轨道
        for track in tracks:
            track_type = track.get("track_type")
            if track_type in track_type_map:
                script.add_track(track_type_map[track_type])
                self.logger.info(f"添加轨道: {track_type}")
            elif track_type in ["effect", "filter"]:
                # effect 和 filter 轨道通过不同方式添加
                self.logger.info(f"跳过轨道添加（将在片段添加时处理）: {track_type}")

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

                # 创建片段
                seg = self._create_segment(segment_type, config_data, temp_assets_dir)
                if seg:
                    # 应用操作
                    self._apply_operations(seg, operations)
                    # 添加到脚本
                    script.add_segment(seg)
                    self.logger.info(f"添加片段: {segment_type} ({segment_id})")

        # 保存草稿
        script.save()
        draft_path = os.path.join(self.output_dir, draft_name)

        self.logger.info(f"草稿保存成功: {draft_path}")
        return draft_path

    def _create_segment(
        self, segment_type: str, config: Dict[str, Any], assets_dir: str
    ):
        """创建片段对象"""
        try:
            material_url = config.get("material_url")
            target_timerange = config.get("target_timerange", {})
            start = target_timerange.get("start", 0)
            duration = target_timerange.get("duration", 1000000)

            # 转换微秒到秒字符串
            start_sec = start / 1000000
            duration_sec = duration / 1000000

            if segment_type == "audio":
                # 下载音频
                local_path = self.download_material(material_url, assets_dir)
                volume = config.get("volume", 1.0)
                seg = draft.AudioSegment(
                    local_path,
                    trange(f"{start_sec}s", f"{duration_sec}s"),
                    volume=volume,
                )
                return seg

            elif segment_type == "video" or segment_type == "image":
                # 下载视频/图片
                local_path = self.download_material(material_url, assets_dir)
                
                # 获取 ClipSettings
                clip_config = config.get("clip_settings")
                clip_settings = None
                if clip_config:
                    clip_settings = draft.ClipSettings(
                        alpha=clip_config.get("alpha", 1.0),
                        rotation=clip_config.get("rotation", 0.0),
                        scale_x=clip_config.get("scale_x", 1.0),
                        scale_y=clip_config.get("scale_y", 1.0),
                        transform_x=clip_config.get("transform_x", 0.0),
                        transform_y=clip_config.get("transform_y", 0.0)
                    )

                # 获取 CropSettings
                crop_config = config.get("crop_settings")
                crop_settings = None
                if crop_config:
                    crop_settings = draft.CropSettings(
                        upper_left_x=crop_config.get("upper_left_x", 0.0),
                        upper_left_y=crop_config.get("upper_left_y", 0.0),
                        upper_right_x=crop_config.get("upper_right_x", 1.0),
                        upper_right_y=crop_config.get("upper_right_y", 0.0),
                        lower_left_x=crop_config.get("lower_left_x", 0.0),
                        lower_left_y=crop_config.get("lower_left_y", 1.0),
                        lower_right_x=crop_config.get("lower_right_x", 1.0),
                        lower_right_y=crop_config.get("lower_right_y", 1.0)
                    )

                # 如果有 crop_settings，需要先创建 VideoMaterial
                if crop_settings:
                    material = draft.VideoMaterial(local_path, crop_settings=crop_settings)
                    seg = draft.VideoSegment(
                        material, 
                        trange(f"{start_sec}s", f"{duration_sec}s"),
                        clip_settings=clip_settings
                    )
                else:
                    seg = draft.VideoSegment(
                        local_path, 
                        trange(f"{start_sec}s", f"{duration_sec}s"),
                        clip_settings=clip_settings
                    )
                return seg

            elif segment_type == "text":
                # 文本片段
                text_content = config.get("text_content", "")
                font_family = config.get("font_family", "文轩体")
                color = config.get("color", "#FFFFFF")
                position = config.get("position", {})

                # 转换颜色
                hex_color = color.lstrip("#")
                r = int(hex_color[0:2], 16) / 255.0
                g = int(hex_color[2:4], 16) / 255.0
                b = int(hex_color[4:6], 16) / 255.0

                # 创建文本片段
                text_timerange = trange(f"{start_sec}s", f"{duration_sec}s")

                # 获取字体类型
                try:
                    font_type = getattr(draft.FontType, font_family, None)
                    if not font_type:
                        font_type = draft.FontType.文轩体
                except:
                    font_type = draft.FontType.文轩体

                seg = draft.TextSegment(
                    text_content,
                    text_timerange,
                    font=font_type,
                    style=draft.TextStyle(color=(r, g, b)),
                    clip_settings=draft.ClipSettings(
                        transform_y=position.get("y", 0.0)
                    ),
                )
                return seg

            elif segment_type == "sticker":
                # 贴纸片段
                resource_id = config.get("resource_id", "")
                if not resource_id:
                    self.logger.error("贴纸片段缺少 resource_id")
                    return None

                # 创建贴纸片段
                position_x = config.get("position_x", 0.0)
                position_y = config.get("position_y", 0.0)
                scale_x = config.get("scale_x", 1.0)
                scale_y = config.get("scale_y", 1.0)
                rotation = config.get("rotation", 0.0)
                opacity = config.get("opacity", 1.0)
                flip_horizontal = config.get("flip_horizontal", False)
                flip_vertical = config.get("flip_vertical", False)

                seg = draft.StickerSegment(
                    resource_id,
                    trange(f"{start_sec}s", f"{duration_sec}s"),
                    clip_settings=draft.ClipSettings(
                        transform_x=position_x,
                        transform_y=position_y,
                        scale_x=scale_x,
                        scale_y=scale_y,
                        rotation=rotation,
                        alpha=opacity,
                        flip_horizontal=flip_horizontal,
                        flip_vertical=flip_vertical,
                    ),
                )
                return seg

            elif segment_type == "effect":
                # 特效片段
                effect_type = config.get("effect_type", "")
                if not effect_type:
                    self.logger.error("特效片段缺少 effect_type")
                    return None

                # 尝试从 VideoSceneEffectType 获取特效
                try:
                    effect = getattr(VideoSceneEffectType, effect_type, None)
                    if not effect:
                        self.logger.warning(f"未知的特效类型: {effect_type}")
                        return None

                    # 获取特效参数
                    intensity = config.get("intensity", 1.0)
                    properties = config.get("properties", {})

                    # 创建特效片段
                    seg = draft.EffectSegment(
                        effect, trange(f"{start_sec}s", f"{duration_sec}s")
                    )
                    return seg
                except Exception as e:
                    self.logger.error(f"创建特效片段失败: {e}")
                    return None

            elif segment_type == "filter":
                # 滤镜片段
                filter_type = config.get("filter_type", "")
                if not filter_type:
                    self.logger.error("滤镜片段缺少 filter_type")
                    return None

                # 尝试从 FilterType 获取滤镜
                try:
                    filter_enum = getattr(FilterType, filter_type, None)
                    if not filter_enum:
                        self.logger.warning(f"未知的滤镜类型: {filter_type}")
                        return None

                    # 获取滤镜强度
                    intensity = config.get("intensity", 1.0)

                    # 创建滤镜片段 - FilterSegment(FilterType, timerange, intensity)
                    seg = draft.FilterSegment(
                        filter_enum,
                        trange(f"{start_sec}s", f"{duration_sec}s"),
                        intensity=intensity,
                    )
                    return seg
                except Exception as e:
                    self.logger.error(f"创建滤镜片段失败: {e}")
                    return None

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
                    
                    # 处理 "None" 字符串
                    if duration == "None":
                        duration = None

                    # 尝试获取动画类型
                    try:
                        anim = None
                        
                        # 1. 尝试解析带前缀的类型 (e.g. "OutroType.斜切")
                        if "." in animation_type:
                            type_name, anim_name = animation_type.split(".", 1)
                            # 视频动画类型
                            if type_name == "IntroType":
                                anim = getattr(IntroType, anim_name, None)
                            elif type_name == "OutroType":
                                anim = getattr(OutroType, anim_name, None)
                            elif type_name == "GroupAnimationType":
                                anim = getattr(GroupAnimationType, anim_name, None)
                            # 文本动画类型
                            elif type_name == "TextIntro":
                                anim = getattr(TextIntro, anim_name, None)
                            elif type_name == "TextOutro":
                                anim = getattr(TextOutro, anim_name, None)
                            elif type_name == "TextLoopAnim":
                                anim = getattr(TextLoopAnim, anim_name, None)
                        
                        # 2. 如果没有前缀或解析失败，且没有找到anim，则进行模糊查找
                        if not anim:
                            # 如果输入包含点但没匹配到（可能是错误的前缀），尝试只用后半部分
                            clean_anim_name = animation_type.split(".")[-1] if "." in animation_type else animation_type
                            
                            if isinstance(seg, VideoSegment):
                                # 视频动画: 依次查找 IntroType, OutroType, GroupAnimationType
                                # 注意：这里存在优先级，如果有重名且未指定前缀，IntroType 优先
                                anim = getattr(IntroType, clean_anim_name, None)
                                if not anim:
                                    anim = getattr(OutroType, clean_anim_name, None)
                                if not anim:
                                    anim = getattr(GroupAnimationType, clean_anim_name, None)
                            
                            elif isinstance(seg, TextSegment):
                                # 文本动画: 依次查找 TextIntro, TextOutro, TextLoopAnim
                                anim = getattr(TextIntro, clean_anim_name, None)
                                if not anim:
                                    anim = getattr(TextOutro, clean_anim_name, None)
                                if not anim:
                                    anim = getattr(TextLoopAnim, clean_anim_name, None)

                        if anim:
                            if duration:
                                seg.add_animation(anim, duration=tim(duration))
                            else:
                                seg.add_animation(anim)
                            self.logger.info(f"应用动画: {animation_type}")
                        else:
                            self.logger.warning(f"未找到动画类型: {animation_type}")
                            
                    except Exception as e:
                        self.logger.warning(f"应用动画失败: {e}")

                elif op_type == "add_transition":
                    # 转场
                    transition_type = op_data.get("transition_type", "")
                    
                    # 处理 "TransitionType." 前缀
                    if transition_type.startswith("TransitionType."):
                        transition_type = transition_type.replace("TransitionType.", "")
                    
                    try:
                        trans = getattr(TransitionType, transition_type, None)
                        if trans and hasattr(seg, "add_transition"):
                            seg.add_transition(trans)
                            self.logger.info(f"应用转场: {transition_type}")
                        else:
                            self.logger.warning(f"未找到转场类型: {transition_type}")
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
