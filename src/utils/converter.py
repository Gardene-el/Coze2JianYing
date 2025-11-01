"""
数据结构转换器
将 Draft Generator Interface 的数据结构转换为 pyJianYingDraft 的数据结构
"""
import pyJianYingDraft as draft
from pyJianYingDraft import (
    Timerange, ClipSettings, CropSettings, TextStyle,
    VideoSegment, AudioSegment, TextSegment, IntroType, TransitionType, trange, tim
)

from typing import Dict, Any, Optional
from utils.logger import get_logger


class DraftInterfaceConverter:
    """Draft Generator Interface 到 pyJianYingDraft 的转换器"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    # ========== 基础转换函数 ==========
    
    def hex_to_rgb(self, hex_color: str) -> tuple:
        """
        将十六进制颜色转换为RGB元组
        
        Args:
            hex_color: 十六进制颜色字符串，如 "#FFFFFF" 或 "FFFFFF"
            
        Returns:
            RGB元组，取值范围为[0, 1]，如 (1.0, 1.0, 1.0)
        """
        # 移除开头的 # 号
        hex_color = hex_color.lstrip('#')
        
        # 转换为 RGB (0-255)
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        # 归一化到 [0, 1]
        rgb_tuple = (r / 255.0, g / 255.0, b / 255.0)
        
        self.logger.debug(f"颜色转换: {hex_color} -> {rgb_tuple}")
        return rgb_tuple
    
    def convert_timerange(self, time_range_dict: Dict[str, int]) -> Timerange:
        """
        转换时间范围格式
        Draft Generator Interface: {"start": ms, "end": ms}
        pyJianYingDraft: Timerange(start, duration)
        
        Args:
            time_range_dict: {"start": int, "end": int}
            
        Returns:
            Timerange对象
        """
        start = time_range_dict["start"]
        end = time_range_dict["end"]
        duration = end - start
        
        self.logger.info(f"转换时间范围: start={start}ms, end={end}ms -> duration={duration}ms")
        return Timerange(start=start, duration=duration)
    
    def convert_crop_settings(self, crop_dict: Dict[str, Any]) -> Optional[CropSettings]:
        """
        转换裁剪设置
        Draft Generator Interface: {left, top, right, bottom}
        pyJianYingDraft: CropSettings(四角点坐标)
        
        Args:
            crop_dict: {"enabled": bool, "left": float, "top": float, 
                        "right": float, "bottom": float}
        
        Returns:
            CropSettings对象或None
        """
        if not crop_dict.get("enabled", False):
            return None
        
        left = crop_dict.get("left", 0.0)
        top = crop_dict.get("top", 0.0)
        right = crop_dict.get("right", 1.0)
        bottom = crop_dict.get("bottom", 1.0)
        
        self.logger.debug(f"转换裁剪设置: L={left}, T={top}, R={right}, B={bottom}")
        
        return CropSettings(
            upper_left_x=left,
            upper_left_y=top,
            upper_right_x=right,
            upper_right_y=top,
            lower_left_x=left,
            lower_left_y=bottom,
            lower_right_x=right,
            lower_right_y=bottom
        )
    
    def convert_clip_settings(self, transform_dict: Dict[str, Any]) -> ClipSettings:
        """
        转换变换设置
        Draft Generator Interface: {position_x, position_y, scale_x, scale_y, rotation, opacity}
        pyJianYingDraft: ClipSettings(alpha, rotation, scale_x, scale_y, transform_x, transform_y)
        
        Args:
            transform_dict: 变换字典
            
        Returns:
            ClipSettings对象
        """
        # 处理null值，使用默认值替代
        def get_value_or_default(key: str, default: float) -> float:
            value = transform_dict.get(key)
            return default if value is None else value
        
        settings = ClipSettings(
            alpha=get_value_or_default("opacity", 1.0),
            rotation=get_value_or_default("rotation", 0.0),
            scale_x=get_value_or_default("scale_x", 1.0),
            scale_y=get_value_or_default("scale_y", 1.0),
            transform_x=get_value_or_default("position_x", 0.0),
            transform_y=get_value_or_default("position_y", 0.0)
        )
        
        self.logger.debug(f"转换变换设置: alpha={settings.alpha}, rotation={settings.rotation}")
        return settings
    
    def convert_filter_intensity(self, intensity_0_1: float) -> float:
        """
        转换滤镜强度
        Draft Generator Interface: 0.0-1.0
        pyJianYingDraft: 0-100
        
        Args:
            intensity_0_1: 0到1之间的强度值
            
        Returns:
            0到100之间的强度值
        """
        result = intensity_0_1 * 100.0
        self.logger.debug(f"转换滤镜强度: {intensity_0_1} -> {result}")
        return result
    
    # ========== Segment转换函数 ==========

    def convert_image_segment_config(
        self, 
        segment_config: Dict[str, Any],
        image_file_path: str
    ) -> VideoSegment:
        """
        转换图片段配置到 VideoSegment
        
        Args:
            segment_config: Draft Generator Interface 的 VideoSegmentConfig 字典
            image_file_path: 图片文件的具体地址
            
        Returns:
            VideoSegment 实例
        """
        self.logger.info("转换图片段配置")
        
        # 1. 时间范围（必须）
        target_timerange = self.convert_timerange(segment_config["time_range"])
        
        # 2. 变换设置（可选）
        clip_settings = None
        transform_config = segment_config.get("transform")
        if transform_config and any(v is not None for v in transform_config.values()):
            clip_settings = self.convert_clip_settings(transform_config)
        
        # 3. 创建 VideoSegment，直接传入素材路径和时间范围
        # 使用便捷构造，直接传入素材路径
        if clip_settings is not None:
            image_segment = VideoSegment(
                material=image_file_path,
                target_timerange=target_timerange,
                clip_settings=clip_settings
            )
        else:
            image_segment = VideoSegment(
                material=image_file_path,
                target_timerange=target_timerange
            )
        
        self.logger.info(f"图片段创建完成: {target_timerange.start}ms - {target_timerange.end}ms")
        return image_segment

    def convert_video_segment_config(
        self, 
        segment_config: Dict[str, Any],
        video_material: draft.VideoMaterial
    ) -> VideoSegment:
        """
        转换视频段配置到 VideoSegment
        
        Args:
            segment_config: Draft Generator Interface 的 VideoSegmentConfig 字典
            video_material: pyJianYingDraft 的 VideoMaterial 实例
            
        Returns:
            VideoSegment 实例
        """
        self.logger.info("转换视频段配置")
        
        # 1. 时间范围（必须）
        target_timerange = self.convert_timerange(segment_config["time_range"])
        
        # 2. 素材裁剪范围（可选）
        source_timerange = None
        if segment_config.get("material_range"):
            source_timerange = self.convert_timerange(segment_config["material_range"])
        
        # 3. 变换设置（可选）
        clip_settings = None
        transform_config = segment_config.get("transform")
        if transform_config and any(v is not None for v in transform_config.values()):
            clip_settings = self.convert_clip_settings(transform_config)
        
        # 4. 速度控制（可选）
        speed = None
        speed_config = segment_config.get("speed")
        if speed_config and speed_config.get("speed") is not None:
            speed = speed_config["speed"]
        
        # 5. 创建 VideoSegment，只传入非空参数
        kwargs = {
            "material": video_material,
            "target_timerange": target_timerange
        }
        
        if source_timerange is not None:
            kwargs["source_timerange"] = source_timerange
        if speed is not None:
            kwargs["speed"] = speed
        if clip_settings is not None:
            kwargs["clip_settings"] = clip_settings
        
        video_segment = VideoSegment(**kwargs)
        
        self.logger.info(f"视频段创建完成: {target_timerange.start}ms - {target_timerange.end}ms")
        return video_segment
    
    def convert_audio_segment_config(
        self,
        segment_config: Dict[str, Any],
        audio_material: draft.AudioMaterial
    ) -> AudioSegment:
        """
        转换音频段配置到 AudioSegment
        
        Args:
            segment_config: Draft Generator Interface 的 AudioSegmentConfig 字典
            audio_material: pyJianYingDraft 的 AudioMaterial 实例
            
        Returns:
            AudioSegment 实例
        """
        self.logger.info("转换音频段配置")
        
        # 1. 时间范围
        target_timerange = self.convert_timerange(segment_config["time_range"])
        
        # 2. 素材裁剪范围（可选）
        source_timerange = None
        if segment_config.get("material_range"):
            source_timerange = self.convert_timerange(segment_config["material_range"])
        
        # 3. 音频属性（可选）
        volume = None
        speed = None
        audio_config = segment_config.get("audio")
        if audio_config:
            if audio_config.get("volume") is not None:
                volume = audio_config["volume"]
            if audio_config.get("speed") is not None:
                speed = audio_config["speed"]
        
        # 4. 创建 AudioSegment，只传入非空参数
        kwargs = {
            "material": audio_material,
            "target_timerange": target_timerange
        }
        
        if source_timerange is not None:
            kwargs["source_timerange"] = source_timerange
        if volume is not None:
            kwargs["volume"] = volume
        if speed is not None:
            kwargs["speed"] = speed
        
        audio_segment = AudioSegment(**kwargs)
        
        self.logger.info(f"音频段创建完成: {target_timerange.start}ms - {target_timerange.end}ms")
        return audio_segment
    
    def convert_text_segment_config(
        self,
        segment_config: Dict[str, Any]
    ) -> TextSegment:
        """
        转换文本段配置到 TextSegment
        
        Args:
            segment_config: Draft Generator Interface 的 TextSegmentConfig 字典
            
        Returns:
            TextSegment 实例
        """
        self.logger.info("转换文本段配置")
        
        # 1. 基本信息
        text_content = segment_config["content"]
        timerange = self.convert_timerange(segment_config["time_range"])
        
        # 2. 变换设置（可选）
        clip_settings = None
        transform_config = segment_config.get("transform")
        if transform_config and any(v is not None for v in transform_config.values()):
            # 文本使用相同的scale值处理
            def get_value_or_default(key: str, default: float) -> float:
                value = transform_config.get(key)
                return default if value is None else value
            
            # 处理scale特殊情况（文本通常使用统一缩放）
            scale = get_value_or_default("scale", 1.0)
            
            clip_settings = ClipSettings(
                alpha=get_value_or_default("opacity", 1.0),
                rotation=get_value_or_default("rotation", 0.0),
                scale_x=scale,
                scale_y=scale,
                transform_x=get_value_or_default("position_x", 0.5),
                transform_y=get_value_or_default("position_y", 0.0)
            )
        
        # 3. 文本样式（可选）
        text_style = None
        style_config = segment_config.get("style")
        if style_config and any(v is not None for v in style_config.values()):
            def get_style_value_or_default(key: str, default: Any) -> Any:
                value = style_config.get(key)
                return default if value is None else value
            
            # 获取颜色并转换为RGB元组
            color_hex = get_style_value_or_default("color", "#FFFFFF")
            color_rgb = self.hex_to_rgb(color_hex)
            
            # 获取字体大小，注意pyJianYingDraft的默认值是8.0
            # 如果输入是像素值（如48），需要转换到合理范围
            font_size_input = get_style_value_or_default("font_size", None)
            if font_size_input is None:
                font_size = 8.0  # 使用库的默认值
            elif font_size_input > 20:
                # 假设输入是像素值，转换为pyJianYingDraft的范围（通常<20）
                font_size = font_size_input / 6.0  # 48px -> 8.0
                self.logger.warning(f"字体大小从像素值{font_size_input}转换为{font_size}")
            else:
                font_size = font_size_input
            
            text_style = TextStyle(
                size=font_size,
                color=color_rgb  # 使用转换后的RGB元组
            )
        
        # 4. 创建 TextSegment，只传入非空参数
        kwargs = {
            "text": text_content,
            "timerange": timerange
        }
        
        if text_style is not None:
            kwargs["style"] = text_style
        if clip_settings is not None:
            kwargs["clip_settings"] = clip_settings
        
        text_segment = TextSegment(**kwargs)
        
        # 先切片，再放入 f-string，避免解析问题
        text_preview = text_content[:20] if len(text_content) > 20 else text_content
        self.logger.info(f"文本段创建完成: '{text_preview}...' at {timerange.start}ms")
        return text_segment