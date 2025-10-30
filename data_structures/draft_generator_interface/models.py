"""
Draft Generator Interface Data Models

Data structures for passing complete draft configuration to the draft generator.
These models contain all parameters that pyJianYingDraft supports, but with URLs
instead of local file paths for media resources.

IMPORTANT: Segment Type Mapping to pyJianYingDraft
===================================================
This module defines segment configuration classes that correspond to pyJianYingDraft's actual segment types:

pyJianYingDraft Hierarchy:
- BaseSegment (基类)
  - MediaSegment (媒体片段基类 - 不是直接使用的段类型)
    - AudioSegment (音频片段)
    - VisualSegment (视觉片段基类 - 不是直接使用的段类型)
      - VideoSegment (视频片段 - 也用于图片!)
      - TextSegment (文本/字幕片段)
      - StickerSegment (贴纸片段)
  - EffectSegment (特效片段)
  - FilterSegment (滤镜片段)

本模块的配置类映射:
- VideoSegmentConfig -> pyJianYingDraft.VideoSegment
- AudioSegmentConfig -> pyJianYingDraft.AudioSegment
- ImageSegmentConfig -> pyJianYingDraft.VideoSegment (图片在剪映中作为静态视频处理!)
- TextSegmentConfig -> pyJianYingDraft.TextSegment
- StickerSegmentConfig -> pyJianYingDraft.StickerSegment
- EffectSegmentConfig -> pyJianYingDraft.EffectSegment
- FilterSegmentConfig -> pyJianYingDraft.FilterSegment

注意: 媒体资源通过各个 segment 的 material_url 字段直接引用。
在草稿生成器中，这些 URL 会被下载为本地文件，然后传递给 pyJianYingDraft 的 Material 类。
"""

from typing import List, Dict, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import uuid


def _omit_if_default(value: Any, default: Any, include_defaults: bool) -> bool:
    """Helper to determine if a field should be omitted from serialization
    
    Args:
        value: Current value
        default: Default value
        include_defaults: If True, never omit; if False, omit if value equals default
    
    Returns:
        True if field should be omitted
    """
    if include_defaults:
        return False
    
    # Handle None specially - only omit if default is also None
    if value is None:
        return default is None
    
    # Handle empty lists - only omit if default is also an empty list
    if isinstance(value, list) and not value:
        return isinstance(default, list) and not default
    
    # Compare values
    return value == default


def _build_dict_omitting_defaults(fields: Dict[str, Any], defaults: Dict[str, Any], 
                                   include_defaults: bool) -> Dict[str, Any]:
    """Build dictionary, optionally omitting fields with default values
    
    Args:
        fields: Dictionary of field_name: value pairs
        defaults: Dictionary of field_name: default_value pairs
        include_defaults: If False, omit fields matching defaults
    
    Returns:
        Dictionary with optionally filtered fields
    """
    if include_defaults:
        return fields
    
    result = {}
    for key, value in fields.items():
        default = defaults.get(key, None)
        if not _omit_if_default(value, default, include_defaults):
            result[key] = value
    
    return result


@dataclass
class ProjectSettings:
    """Basic project configuration
    
    对应 pyJianYingDraft 的项目设置参数
    """
    name: str = "Coze剪映项目"
    width: int = 1920
    height: int = 1080
    fps: int = 30


@dataclass
class TimeRange:
    """Time range in milliseconds"""
    start: int = 0
    end: int = 0
    
    @property
    def duration(self) -> int:
        return self.end - self.start


@dataclass
class KeyframeProperty:
    """Keyframe property for animations"""
    time: int  # Time in milliseconds
    value: Any  # Property value (position, scale, rotation, etc.)
    ease_in: bool = False
    ease_out: bool = False


@dataclass
class VideoSegmentConfig:
    """Configuration for a video segment
    
    对应 pyJianYingDraft.VideoSegment (继承自 VisualSegment -> MediaSegment -> BaseSegment)
    
    pyJianYingDraft 参数映射:
    - material: VideoMaterial(本地路径) <- material_url 需下载
    - target_timerange: Timerange(start, duration) <- time_range (start, end)
    - source_timerange: Timerange(start, duration) <- material_range (start, end)
    - speed: float
    - volume: float
    - change_pitch: bool
    - clip_settings: ClipSettings (alpha, flip_horizontal, flip_vertical, rotation, scale_x, scale_y, transform_x, transform_y)
    """
    material_url: str
    time_range: TimeRange
    material_range: Optional[TimeRange] = None
    
    # Transform properties
    position_x: float = 0.0
    position_y: float = 0.0
    scale_x: float = 1.0
    scale_y: float = 1.0
    rotation: float = 0.0
    opacity: float = 1.0
    
    # Crop settings
    crop_enabled: bool = False
    crop_left: float = 0.0
    crop_top: float = 0.0
    crop_right: float = 1.0
    crop_bottom: float = 1.0
    
    # Effects and filters
    filter_type: Optional[str] = None
    filter_intensity: float = 1.0
    transition_type: Optional[str] = None
    transition_duration: int = 500  # milliseconds
    
    # Speed control
    speed: float = 1.0
    reverse: bool = False
    
    # Audio control (video can have audio)
    volume: float = 1.0
    change_pitch: bool = False  # Whether to preserve pitch when changing speed
    
    # Background filling
    background_blur: bool = False
    background_color: Optional[str] = None
    
    # Keyframes for animations
    position_keyframes: List[KeyframeProperty] = field(default_factory=list)
    scale_keyframes: List[KeyframeProperty] = field(default_factory=list)
    rotation_keyframes: List[KeyframeProperty] = field(default_factory=list)
    opacity_keyframes: List[KeyframeProperty] = field(default_factory=list)


@dataclass
class AudioSegmentConfig:
    """Configuration for an audio segment
    
    对应 pyJianYingDraft.AudioSegment (继承自 MediaSegment -> BaseSegment)
    
    pyJianYingDraft 参数映射:
    - material: AudioMaterial(本地路径) <- material_url 需下载
    - target_timerange: Timerange(start, duration) <- time_range (start, end)
    - source_timerange: Timerange(start, duration) <- material_range (start, end)
    - speed: float
    - volume: float
    - change_pitch: bool
    - fade: AudioFade (in_duration, out_duration) <- fade_in, fade_out
    - effects: List[AudioEffect]
    """
    material_url: str
    time_range: TimeRange
    material_range: Optional[TimeRange] = None
    
    # Audio properties
    volume: float = 1.0
    fade_in: int = 0  # milliseconds
    fade_out: int = 0  # milliseconds
    
    # Audio effects
    effect_type: Optional[str] = None
    effect_intensity: float = 1.0
    
    # Speed control
    speed: float = 1.0
    change_pitch: bool = False  # Whether to preserve pitch when changing speed
    
    # Volume keyframes
    volume_keyframes: List[KeyframeProperty] = field(default_factory=list)


@dataclass
class ImageSegmentConfig:
    """Configuration for an image segment
    
    ⚠️ 重要: 图片在 pyJianYingDraft 中没有独立的 ImageSegment 类!
    图片实际上是作为 VideoSegment 处理的（静态视频）。
    
    对应 pyJianYingDraft.VideoSegment:
    - material: VideoMaterial(图片本地路径) <- material_url 需下载
    - target_timerange: Timerange(start, duration) <- time_range (start, end)
    - source_timerange: None (图片没有素材裁剪范围)
    - speed: 1.0 (图片不支持速度控制)
    - volume: 1.0 (图片没有音频)
    - change_pitch: False
    - clip_settings: ClipSettings (控制位置、缩放、旋转、透明度等)
    
    本配置类移除了不适用于静态图片的参数（material_range, speed, reverse, volume），
    但添加了图片特有的参数（fit_mode, intro_animation, outro_animation）。
    """
    material_url: str
    time_range: TimeRange
    
    # Transform properties
    position_x: float = 0.0
    position_y: float = 0.0
    scale_x: float = 1.0
    scale_y: float = 1.0
    rotation: float = 0.0
    opacity: float = 1.0
    
    # Image dimensions (original or desired)
    width: Optional[int] = None
    height: Optional[int] = None
    
    # Crop settings
    crop_enabled: bool = False
    crop_left: float = 0.0
    crop_top: float = 0.0
    crop_right: float = 1.0
    crop_bottom: float = 1.0
    
    # Effects and filters
    filter_type: Optional[str] = None
    filter_intensity: float = 1.0
    transition_type: Optional[str] = None
    transition_duration: int = 500  # milliseconds
    
    # Background filling (for aspect ratio mismatch)
    background_blur: bool = False
    background_color: Optional[str] = None
    fit_mode: str = "fit"  # "fit", "fill", "stretch"
    
    # Animation properties
    intro_animation: Optional[str] = None  # "轻微放大", etc.
    intro_animation_duration: int = 500  # milliseconds
    outro_animation: Optional[str] = None
    outro_animation_duration: int = 500  # milliseconds
    
    # Keyframes for animations
    position_keyframes: List[KeyframeProperty] = field(default_factory=list)
    scale_keyframes: List[KeyframeProperty] = field(default_factory=list)
    rotation_keyframes: List[KeyframeProperty] = field(default_factory=list)
    opacity_keyframes: List[KeyframeProperty] = field(default_factory=list)


@dataclass
class TextStyle:
    """Text styling configuration"""
    font_family: str = "默认"
    font_size: int = 48
    font_weight: str = "normal"  # "normal", "bold"
    font_style: str = "normal"  # "normal", "italic"
    color: str = "#FFFFFF"
    
    # Text effects
    stroke_enabled: bool = False
    stroke_color: str = "#000000"
    stroke_width: int = 2
    
    shadow_enabled: bool = False
    shadow_color: str = "#000000"
    shadow_offset_x: int = 2
    shadow_offset_y: int = 2
    shadow_blur: int = 4
    
    background_enabled: bool = False
    background_color: str = "#000000"
    background_opacity: float = 0.5


@dataclass
class TextSegmentConfig:
    """Configuration for a text/subtitle segment
    
    对应 pyJianYingDraft.TextSegment (继承自 VisualSegment -> MediaSegment -> BaseSegment)
    
    pyJianYingDraft 参数映射:
    - text: str <- content
    - target_timerange: Timerange(start, duration) <- time_range (start, end)
    - style: TextStyle (size, bold, italic, underline, color, alpha, align, vertical, letter_spacing, line_spacing, auto_wrapping, max_line_width)
    - clip_settings: ClipSettings (控制位置、缩放、旋转、透明度)
    - border: TextBorder (alpha, color, width)
    - shadow: TextShadow
    - background: TextBackground
    - animations_instance: SegmentAnimations (intro, outro, loop)
    """
    content: str
    time_range: TimeRange
    
    # Position and transform
    # Note: position_x/position_y map to transform_x/transform_y in pyJianYingDraft's ClipSettings
    # Values are in units of half canvas size: 0.0 = center, positive = up/right, negative = down/left
    # Range: -1.0 to 1.0
    position_x: float = 0.5  # Default: 0.5 (center-right)
    position_y: float = -0.9  # Default: -0.9 (near bottom)
    scale: float = 1.0
    rotation: float = 0.0
    opacity: float = 1.0
    
    # Text styling
    style: TextStyle = field(default_factory=TextStyle)
    
    # Alignment
    alignment: str = "center"  # "left", "center", "right"
    
    # Animations
    intro_animation: Optional[str] = None
    outro_animation: Optional[str] = None
    loop_animation: Optional[str] = None
    
    # Keyframes for animations
    position_keyframes: List[KeyframeProperty] = field(default_factory=list)
    scale_keyframes: List[KeyframeProperty] = field(default_factory=list)
    rotation_keyframes: List[KeyframeProperty] = field(default_factory=list)
    opacity_keyframes: List[KeyframeProperty] = field(default_factory=list)


@dataclass
class EffectSegmentConfig:
    """Configuration for effect segments
    
    对应 pyJianYingDraft.EffectSegment (继承自 BaseSegment)
    
    pyJianYingDraft 参数映射:
    - effect_inst: VideoEffect (VideoSceneEffectType 或 VideoCharacterEffectType)
    - target_timerange: Timerange(start, duration) <- time_range (start, end)
    - params: List[Optional[float]] (0-100 范围的参数值)
    
    注意: EffectSegment 在 pyJianYingDraft 中放置在独立的特效轨道上，作用域为全局(apply_target_type=2)
    """
    effect_type: str
    time_range: TimeRange
    
    # Effect properties
    intensity: float = 1.0
    properties: Dict[str, Any] = field(default_factory=dict)
    
    # Position (for localized effects)
    position_x: Optional[float] = None
    position_y: Optional[float] = None
    scale: float = 1.0


@dataclass
class FilterSegmentConfig:
    """Configuration for filter segments
    
    对应 pyJianYingDraft.FilterSegment (继承自 BaseSegment)
    
    pyJianYingDraft 参数映射:
    - material: Filter (FilterType, intensity)
    - target_timerange: Timerange(start, duration) <- time_range (start, end)
    - intensity: float (0-1 范围，对应剪映中的 0-100)
    
    注意: FilterSegment 在 pyJianYingDraft 中放置在独立的滤镜轨道上
    """
    filter_type: str
    time_range: TimeRange
    intensity: float = 1.0  # 0-1 range


@dataclass
class StickerSegmentConfig:
    """Configuration for sticker segments
    
    对应 pyJianYingDraft.StickerSegment (继承自 VisualSegment -> MediaSegment -> BaseSegment)
    
    pyJianYingDraft 参数映射:
    - resource_id: str (贴纸的resource_id，可通过ScriptFile.inspect_material从模板中获取)
    - target_timerange: Timerange(start, duration) <- time_range (start, end)
    - clip_settings: ClipSettings (控制位置、缩放、旋转、透明度)
    
    注意: 贴纸没有 source_timerange (素材裁剪范围不适用于贴纸)
    """
    resource_id: str
    time_range: TimeRange
    
    # Transform properties (via ClipSettings)
    position_x: float = 0.0
    position_y: float = 0.0
    scale_x: float = 1.0
    scale_y: float = 1.0
    rotation: float = 0.0
    opacity: float = 1.0
    
    # Flip options
    flip_horizontal: bool = False
    flip_vertical: bool = False
    
    # Keyframes for animations
    position_keyframes: List[KeyframeProperty] = field(default_factory=list)
    scale_keyframes: List[KeyframeProperty] = field(default_factory=list)
    rotation_keyframes: List[KeyframeProperty] = field(default_factory=list)
    opacity_keyframes: List[KeyframeProperty] = field(default_factory=list)


@dataclass
class TrackConfig:
    """Configuration for a single track
    
    对应 pyJianYingDraft.Track，每种轨道类型只接受特定的段类型。
    
    支持的轨道类型及其接受的段类型:
    - "video": 视频轨道 -> VideoSegmentConfig, ImageSegmentConfig (图片作为静态视频)
    - "audio": 音频轨道 -> AudioSegmentConfig
    - "text": 文本/字幕轨道 -> TextSegmentConfig
    - "sticker": 贴纸轨道 -> StickerSegmentConfig
    - "effect": 特效轨道 -> EffectSegmentConfig (独立轨道)
    - "filter": 滤镜轨道 -> FilterSegmentConfig (独立轨道)
    
    注意: 
    - 图片没有独立的轨道类型，应放在 video 轨道上
    - 每个轨道应只包含其对应类型的 segments
    - pyJianYingDraft 会在运行时验证 segment 类型与轨道类型匹配
    """
    track_type: str  # "video", "audio", "text", "sticker", "effect", "filter"
    segments: List[Union[VideoSegmentConfig, AudioSegmentConfig, ImageSegmentConfig, TextSegmentConfig, StickerSegmentConfig, EffectSegmentConfig, FilterSegmentConfig]] = field(default_factory=list)
    muted: bool = False
    volume: float = 1.0  # For audio tracks
    
    def __post_init__(self):
        """验证 track_type 和 segments 的匹配性"""
        valid_track_types = {"video", "audio", "text", "sticker", "effect", "filter"}
        if self.track_type not in valid_track_types:
            raise ValueError(f"Invalid track_type '{self.track_type}'. Must be one of: {valid_track_types}")
        
        # 验证 segments 类型与 track_type 匹配
        for segment in self.segments:
            if not self._is_valid_segment_for_track(segment):
                raise ValueError(
                    f"Segment type {type(segment).__name__} is not compatible with track_type '{self.track_type}'. "
                    f"Expected: {self._get_expected_segment_types()}"
                )
    
    def _is_valid_segment_for_track(self, segment) -> bool:
        """检查 segment 类型是否与当前 track_type 兼容"""
        type_mapping = {
            "video": (VideoSegmentConfig, ImageSegmentConfig),  # video 轨道接受视频和图片
            "audio": (AudioSegmentConfig,),
            "text": (TextSegmentConfig,),
            "sticker": (StickerSegmentConfig,),
            "effect": (EffectSegmentConfig,),
            "filter": (FilterSegmentConfig,)
        }
        expected_types = type_mapping.get(self.track_type, ())
        return isinstance(segment, expected_types)
    
    def _get_expected_segment_types(self) -> str:
        """获取当前 track_type 期望的 segment 类型说明"""
        type_mapping = {
            "video": "VideoSegmentConfig or ImageSegmentConfig",
            "audio": "AudioSegmentConfig",
            "text": "TextSegmentConfig",
            "sticker": "StickerSegmentConfig",
            "effect": "EffectSegmentConfig",
            "filter": "FilterSegmentConfig"
        }
        return type_mapping.get(self.track_type, "Unknown")


@dataclass
class DraftConfig:
    """Complete draft configuration for the draft generator"""
    # Unique identifier for this draft
    draft_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    # Project settings
    project: ProjectSettings = field(default_factory=ProjectSettings)
    
    # Track configurations
    tracks: List[TrackConfig] = field(default_factory=list)
    
    # Metadata
    created_timestamp: float = 0.0
    last_modified: float = 0.0
    
    def to_dict(self, include_defaults: bool = True) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization
        
        Args:
            include_defaults: If True, include all fields even if they have default values.
                            If False, omit fields with default values to reduce data size.
        """
        result = {
            "draft_id": self.draft_id,
            "project": {
                "name": self.project.name,
                "width": self.project.width,
                "height": self.project.height,
                "fps": self.project.fps
            },
            "tracks": []
        }
        
        # Serialize tracks
        for track in self.tracks:
            track_dict = {
                "track_type": track.track_type,
                "segments": self._serialize_segments(track.segments, include_defaults)
            }
            
            # Add optional track fields only if non-default
            if include_defaults or track.muted != False:
                track_dict["muted"] = track.muted
            if include_defaults or track.volume != 1.0:
                track_dict["volume"] = track.volume
            
            result["tracks"].append(track_dict)
        
        result["created_timestamp"] = self.created_timestamp
        result["last_modified"] = self.last_modified
        
        return result
    
    def _serialize_segments(self, segments: List, include_defaults: bool = True) -> List[Dict[str, Any]]:
        """Serialize segment configurations to dictionaries
        
        Args:
            segments: List of segment configurations
            include_defaults: If False, omit fields with default values
        """
        result = []
        for segment in segments:
            if isinstance(segment, VideoSegmentConfig):
                result.append(self._serialize_video_segment(segment, include_defaults))
            elif isinstance(segment, AudioSegmentConfig):
                result.append(self._serialize_audio_segment(segment, include_defaults))
            elif isinstance(segment, ImageSegmentConfig):
                result.append(self._serialize_image_segment(segment, include_defaults))
            elif isinstance(segment, TextSegmentConfig):
                result.append(self._serialize_text_segment(segment, include_defaults))
            elif isinstance(segment, StickerSegmentConfig):
                result.append(self._serialize_sticker_segment(segment, include_defaults))
            elif isinstance(segment, EffectSegmentConfig):
                result.append(self._serialize_effect_segment(segment, include_defaults))
            elif isinstance(segment, FilterSegmentConfig):
                result.append(self._serialize_filter_segment(segment, include_defaults))
        return result
    
    def _serialize_video_segment(self, segment: VideoSegmentConfig, include_defaults: bool = True) -> Dict[str, Any]:
        """Serialize video segment configuration"""
        # Base fields (always include)
        result = {
            "type": "video",
            "material_url": segment.material_url,
            "time_range": {"start": segment.time_range.start, "end": segment.time_range.end}
        }
        
        # Material range (optional, only if set)
        if segment.material_range is not None:
            result["material_range"] = {
                "start": segment.material_range.start,
                "end": segment.material_range.end
            }
        elif include_defaults:
            result["material_range"] = None
        
        # Transform properties with defaults
        transform_defaults = {
            "position_x": 0.0, "position_y": 0.0, "scale_x": 1.0,
            "scale_y": 1.0, "rotation": 0.0, "opacity": 1.0
        }
        transform = _build_dict_omitting_defaults({
            "position_x": segment.position_x,
            "position_y": segment.position_y,
            "scale_x": segment.scale_x,
            "scale_y": segment.scale_y,
            "rotation": segment.rotation,
            "opacity": segment.opacity
        }, transform_defaults, include_defaults)
        if transform:
            result["transform"] = transform
        
        # Crop settings with defaults
        crop_defaults = {
            "enabled": False, "left": 0.0, "top": 0.0,
            "right": 1.0, "bottom": 1.0
        }
        crop = _build_dict_omitting_defaults({
            "enabled": segment.crop_enabled,
            "left": segment.crop_left,
            "top": segment.crop_top,
            "right": segment.crop_right,
            "bottom": segment.crop_bottom
        }, crop_defaults, include_defaults)
        if crop:
            result["crop"] = crop
        
        # Effects with defaults
        effects_defaults = {
            "filter_type": None, "filter_intensity": 1.0,
            "transition_type": None, "transition_duration": 500
        }
        effects = _build_dict_omitting_defaults({
            "filter_type": segment.filter_type,
            "filter_intensity": segment.filter_intensity,
            "transition_type": segment.transition_type,
            "transition_duration": segment.transition_duration
        }, effects_defaults, include_defaults)
        if effects:
            result["effects"] = effects
        
        # Speed settings with defaults
        speed_defaults = {"speed": 1.0, "reverse": False}
        speed = _build_dict_omitting_defaults({
            "speed": segment.speed,
            "reverse": segment.reverse
        }, speed_defaults, include_defaults)
        if speed:
            result["speed"] = speed
        
        # Audio properties with defaults
        audio_defaults = {"volume": 1.0, "change_pitch": False}
        audio = _build_dict_omitting_defaults({
            "volume": segment.volume,
            "change_pitch": segment.change_pitch
        }, audio_defaults, include_defaults)
        if audio:
            result["audio"] = audio
        
        # Background settings with defaults
        background_defaults = {"blur": False, "color": None}
        background = _build_dict_omitting_defaults({
            "blur": segment.background_blur,
            "color": segment.background_color
        }, background_defaults, include_defaults)
        if background:
            result["background"] = background
        
        # Keyframes
        keyframes_defaults = {
            "position": [], "scale": [], "rotation": [], "opacity": []
        }
        keyframes = _build_dict_omitting_defaults({
            "position": [{"time": kf.time, "value": kf.value} for kf in segment.position_keyframes],
            "scale": [{"time": kf.time, "value": kf.value} for kf in segment.scale_keyframes],
            "rotation": [{"time": kf.time, "value": kf.value} for kf in segment.rotation_keyframes],
            "opacity": [{"time": kf.time, "value": kf.value} for kf in segment.opacity_keyframes]
        }, keyframes_defaults, include_defaults)
        if keyframes:
            result["keyframes"] = keyframes
        
        return result
    
    def _serialize_audio_segment(self, segment: AudioSegmentConfig, include_defaults: bool = True) -> Dict[str, Any]:
        """Serialize audio segment configuration"""
        # Base fields (always include)
        result = {
            "type": "audio",
            "material_url": segment.material_url,
            "time_range": {"start": segment.time_range.start, "end": segment.time_range.end}
        }
        
        # Material range (optional, only if set)
        if segment.material_range is not None:
            result["material_range"] = {
                "start": segment.material_range.start,
                "end": segment.material_range.end
            }
        elif include_defaults:
            result["material_range"] = None
        
        # Audio properties with defaults
        audio_defaults = {
            "volume": 1.0, "fade_in": 0, "fade_out": 0,
            "effect_type": None, "effect_intensity": 1.0,
            "speed": 1.0, "change_pitch": False
        }
        audio = _build_dict_omitting_defaults({
            "volume": segment.volume,
            "fade_in": segment.fade_in,
            "fade_out": segment.fade_out,
            "effect_type": segment.effect_type,
            "effect_intensity": segment.effect_intensity,
            "speed": segment.speed,
            "change_pitch": segment.change_pitch
        }, audio_defaults, include_defaults)
        if audio:
            result["audio"] = audio
        
        # Keyframes
        keyframes_defaults = {"volume": []}
        keyframes = _build_dict_omitting_defaults({
            "volume": [{"time": kf.time, "value": kf.value} for kf in segment.volume_keyframes]
        }, keyframes_defaults, include_defaults)
        if keyframes:
            result["keyframes"] = keyframes
        
        return result
    
    def _serialize_image_segment(self, segment: ImageSegmentConfig, include_defaults: bool = True) -> Dict[str, Any]:
        """Serialize image segment configuration"""
        # Base fields (always include)
        result = {
            "type": "image",
            "material_url": segment.material_url,
            "time_range": {"start": segment.time_range.start, "end": segment.time_range.end}
        }
        
        # Optional field groups with defaults
        transform_defaults = {
            "position_x": 0.0, "position_y": 0.0, "scale_x": 1.0,
            "scale_y": 1.0, "rotation": 0.0, "opacity": 1.0
        }
        transform = _build_dict_omitting_defaults({
            "position_x": segment.position_x,
            "position_y": segment.position_y,
            "scale_x": segment.scale_x,
            "scale_y": segment.scale_y,
            "rotation": segment.rotation,
            "opacity": segment.opacity
        }, transform_defaults, include_defaults)
        if transform:
            result["transform"] = transform
        
        dimensions_defaults = {"width": None, "height": None}
        dimensions = _build_dict_omitting_defaults({
            "width": segment.width,
            "height": segment.height
        }, dimensions_defaults, include_defaults)
        if dimensions:
            result["dimensions"] = dimensions
        
        crop_defaults = {
            "enabled": False, "left": 0.0, "top": 0.0,
            "right": 1.0, "bottom": 1.0
        }
        crop = _build_dict_omitting_defaults({
            "enabled": segment.crop_enabled,
            "left": segment.crop_left,
            "top": segment.crop_top,
            "right": segment.crop_right,
            "bottom": segment.crop_bottom
        }, crop_defaults, include_defaults)
        if crop:
            result["crop"] = crop
        
        effects_defaults = {
            "filter_type": None, "filter_intensity": 1.0,
            "transition_type": None, "transition_duration": 500
        }
        effects = _build_dict_omitting_defaults({
            "filter_type": segment.filter_type,
            "filter_intensity": segment.filter_intensity,
            "transition_type": segment.transition_type,
            "transition_duration": segment.transition_duration
        }, effects_defaults, include_defaults)
        if effects:
            result["effects"] = effects
        
        background_defaults = {
            "blur": False, "color": None, "fit_mode": "fit"
        }
        background = _build_dict_omitting_defaults({
            "blur": segment.background_blur,
            "color": segment.background_color,
            "fit_mode": segment.fit_mode
        }, background_defaults, include_defaults)
        if background:
            result["background"] = background
        
        animations_defaults = {
            "intro": None, "intro_duration": 500,
            "outro": None, "outro_duration": 500
        }
        animations = _build_dict_omitting_defaults({
            "intro": segment.intro_animation,
            "intro_duration": segment.intro_animation_duration,
            "outro": segment.outro_animation,
            "outro_duration": segment.outro_animation_duration
        }, animations_defaults, include_defaults)
        if animations:
            result["animations"] = animations
        
        keyframes_defaults = {
            "position": [], "scale": [], "rotation": [], "opacity": []
        }
        keyframes = _build_dict_omitting_defaults({
            "position": [{"time": kf.time, "value": kf.value} for kf in segment.position_keyframes],
            "scale": [{"time": kf.time, "value": kf.value} for kf in segment.scale_keyframes],
            "rotation": [{"time": kf.time, "value": kf.value} for kf in segment.rotation_keyframes],
            "opacity": [{"time": kf.time, "value": kf.value} for kf in segment.opacity_keyframes]
        }, keyframes_defaults, include_defaults)
        if keyframes:
            result["keyframes"] = keyframes
        
        return result
    
    def _serialize_text_segment(self, segment: TextSegmentConfig, include_defaults: bool = True) -> Dict[str, Any]:
        """Serialize text segment configuration"""
        # Base fields (always include)
        result = {
            "type": "text",
            "content": segment.content,
            "time_range": {"start": segment.time_range.start, "end": segment.time_range.end}
        }
        
        # Transform properties with defaults
        transform_defaults = {
            "position_x": 0.5, "position_y": -0.9, "scale": 1.0,
            "rotation": 0.0, "opacity": 1.0
        }
        transform = _build_dict_omitting_defaults({
            "position_x": segment.position_x,
            "position_y": segment.position_y,
            "scale": segment.scale,
            "rotation": segment.rotation,
            "opacity": segment.opacity
        }, transform_defaults, include_defaults)
        if transform:
            result["transform"] = transform
        
        # Style properties with defaults
        style_defaults_main = {
            "font_family": "默认", "font_size": 48,
            "font_weight": "normal", "font_style": "normal",
            "color": "#FFFFFF"
        }
        stroke_defaults = {
            "enabled": False, "color": "#000000", "width": 2
        }
        shadow_defaults = {
            "enabled": False, "color": "#000000",
            "offset_x": 2, "offset_y": 2, "blur": 4
        }
        background_defaults = {
            "enabled": False, "color": "#000000", "opacity": 0.5
        }
        
        style_main = _build_dict_omitting_defaults({
            "font_family": segment.style.font_family,
            "font_size": segment.style.font_size,
            "font_weight": segment.style.font_weight,
            "font_style": segment.style.font_style,
            "color": segment.style.color
        }, style_defaults_main, include_defaults)
        
        stroke = _build_dict_omitting_defaults({
            "enabled": segment.style.stroke_enabled,
            "color": segment.style.stroke_color,
            "width": segment.style.stroke_width
        }, stroke_defaults, include_defaults)
        
        shadow = _build_dict_omitting_defaults({
            "enabled": segment.style.shadow_enabled,
            "color": segment.style.shadow_color,
            "offset_x": segment.style.shadow_offset_x,
            "offset_y": segment.style.shadow_offset_y,
            "blur": segment.style.shadow_blur
        }, shadow_defaults, include_defaults)
        
        background = _build_dict_omitting_defaults({
            "enabled": segment.style.background_enabled,
            "color": segment.style.background_color,
            "opacity": segment.style.background_opacity
        }, background_defaults, include_defaults)
        
        # Build style object if any fields are non-default
        if style_main or stroke or shadow or background:
            style = {}
            if style_main:
                style.update(style_main)
            if stroke:
                style["stroke"] = stroke
            if shadow:
                style["shadow"] = shadow
            if background:
                style["background"] = background
            result["style"] = style
        
        # Alignment with default
        if include_defaults or segment.alignment != "center":
            result["alignment"] = segment.alignment
        
        # Animations with defaults
        animations_defaults = {
            "intro": None, "outro": None, "loop": None
        }
        animations = _build_dict_omitting_defaults({
            "intro": segment.intro_animation,
            "outro": segment.outro_animation,
            "loop": segment.loop_animation
        }, animations_defaults, include_defaults)
        if animations:
            result["animations"] = animations
        
        # Keyframes
        keyframes_defaults = {
            "position": [], "scale": [], "rotation": [], "opacity": []
        }
        keyframes = _build_dict_omitting_defaults({
            "position": [{"time": kf.time, "value": kf.value} for kf in segment.position_keyframes],
            "scale": [{"time": kf.time, "value": kf.value} for kf in segment.scale_keyframes],
            "rotation": [{"time": kf.time, "value": kf.value} for kf in segment.rotation_keyframes],
            "opacity": [{"time": kf.time, "value": kf.value} for kf in segment.opacity_keyframes]
        }, keyframes_defaults, include_defaults)
        if keyframes:
            result["keyframes"] = keyframes
        
        return result
    
    def _serialize_effect_segment(self, segment: EffectSegmentConfig, include_defaults: bool = True) -> Dict[str, Any]:
        """Serialize effect segment configuration"""
        result = {
            "type": "effect",
            "effect_type": segment.effect_type,
            "time_range": {"start": segment.time_range.start, "end": segment.time_range.end}
        }
        
        # Properties with defaults
        properties_defaults = {
            "intensity": 1.0, "position_x": None, "position_y": None, "scale": 1.0
        }
        properties = _build_dict_omitting_defaults({
            "intensity": segment.intensity,
            "position_x": segment.position_x,
            "position_y": segment.position_y,
            "scale": segment.scale,
            **segment.properties
        }, properties_defaults, include_defaults)
        if properties:
            result["properties"] = properties
        
        return result
    
    def _serialize_filter_segment(self, segment: FilterSegmentConfig, include_defaults: bool = True) -> Dict[str, Any]:
        """Serialize filter segment configuration"""
        result = {
            "type": "filter",
            "filter_type": segment.filter_type,
            "time_range": {"start": segment.time_range.start, "end": segment.time_range.end}
        }
        
        # Intensity with default
        if include_defaults or segment.intensity != 1.0:
            result["intensity"] = segment.intensity
        
        return result
    
    def _serialize_sticker_segment(self, segment: StickerSegmentConfig, include_defaults: bool = True) -> Dict[str, Any]:
        """Serialize sticker segment configuration"""
        result = {
            "type": "sticker",
            "resource_id": segment.resource_id,
            "time_range": {"start": segment.time_range.start, "end": segment.time_range.end}
        }
        
        # Transform with defaults
        transform_defaults = {
            "position_x": 0.0, "position_y": 0.0, "scale_x": 1.0,
            "scale_y": 1.0, "rotation": 0.0, "opacity": 1.0
        }
        transform = _build_dict_omitting_defaults({
            "position_x": segment.position_x,
            "position_y": segment.position_y,
            "scale_x": segment.scale_x,
            "scale_y": segment.scale_y,
            "rotation": segment.rotation,
            "opacity": segment.opacity
        }, transform_defaults, include_defaults)
        if transform:
            result["transform"] = transform
        
        # Flip with defaults
        flip_defaults = {"horizontal": False, "vertical": False}
        flip = _build_dict_omitting_defaults({
            "horizontal": segment.flip_horizontal,
            "vertical": segment.flip_vertical
        }, flip_defaults, include_defaults)
        if flip:
            result["flip"] = flip
        
        # Keyframes
        keyframes_defaults = {
            "position": [], "scale": [], "rotation": [], "opacity": []
        }
        keyframes = _build_dict_omitting_defaults({
            "position": [{"time": kf.time, "value": kf.value} for kf in segment.position_keyframes],
            "scale": [{"time": kf.time, "value": kf.value} for kf in segment.scale_keyframes],
            "rotation": [{"time": kf.time, "value": kf.value} for kf in segment.rotation_keyframes],
            "opacity": [{"time": kf.time, "value": kf.value} for kf in segment.opacity_keyframes]
        }, keyframes_defaults, include_defaults)
        if keyframes:
            result["keyframes"] = keyframes
        
        return result


# Input/Output types for Coze tools
@dataclass
class CreateDraftInput:
    """Input for create_draft tool"""
    draft_name: str = "Coze剪映项目"
    width: int = 1920
    height: int = 1080
    fps: int = 30


@dataclass
class CreateDraftOutput:
    """Output for create_draft tool"""
    draft_id: str
    success: bool = True
    message: str = "草稿创建成功"


@dataclass
class ExportDraftsInput:
    """Input for export_drafts tool"""
    draft_ids: Union[str, List[str]]  # Single UUID or list of UUIDs
    remove_temp_files: bool = False


@dataclass
class ExportDraftsOutput:
    """Output for export_drafts tool"""
    draft_data: str  # JSON string for draft generator
    exported_count: int
    success: bool = True
    message: str = "草稿导出成功"