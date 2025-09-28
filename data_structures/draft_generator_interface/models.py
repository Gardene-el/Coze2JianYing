"""
Draft Generator Interface Data Models

Data structures for passing complete draft configuration to the draft generator.
These models contain all parameters that pyJianYingDraft supports, but with URLs
instead of local file paths for media resources.
"""

from typing import List, Dict, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import uuid


class VideoQuality(Enum):
    """Video quality settings"""
    SD_480P = "480p"
    HD_720P = "720p"
    FHD_1080P = "1080p"
    QHD_1440P = "1440p"
    UHD_4K = "4k"


class AudioQuality(Enum):
    """Audio quality settings"""
    LOW_128K = "128k"
    MEDIUM_192K = "192k"
    HIGH_320K = "320k"
    LOSSLESS = "lossless"


@dataclass
class ProjectSettings:
    """Basic project configuration"""
    name: str = "Coze剪映项目"
    width: int = 1920
    height: int = 1080
    fps: int = 30
    video_quality: VideoQuality = VideoQuality.FHD_1080P
    audio_quality: AudioQuality = AudioQuality.HIGH_320K
    background_color: str = "#000000"


@dataclass
class MediaResource:
    """Represents a media resource with URL and metadata"""
    url: str
    resource_type: str  # "video", "audio", "image"
    duration_ms: Optional[int] = None
    file_size: Optional[int] = None
    format: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    filename: Optional[str] = None


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
    """Configuration for a video segment"""
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
    """Configuration for an audio segment"""
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
    
    # Volume keyframes
    volume_keyframes: List[KeyframeProperty] = field(default_factory=list)


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
    """Configuration for a text/subtitle segment"""
    content: str
    time_range: TimeRange
    
    # Position and transform
    position_x: float = 0.5  # Normalized (0-1)
    position_y: float = 0.9  # Normalized (0-1)
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
    """Configuration for effect segments"""
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
class TrackConfig:
    """Configuration for a single track"""
    track_type: str  # "video", "audio", "text", "effect"
    segments: List[Union[VideoSegmentConfig, AudioSegmentConfig, TextSegmentConfig, EffectSegmentConfig]] = field(default_factory=list)
    muted: bool = False
    volume: float = 1.0  # For audio tracks


@dataclass
class DraftConfig:
    """Complete draft configuration for the draft generator"""
    # Unique identifier for this draft
    draft_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    # Project settings
    project: ProjectSettings = field(default_factory=ProjectSettings)
    
    # Media resources (all URLs)
    media_resources: List[MediaResource] = field(default_factory=list)
    
    # Track configurations
    tracks: List[TrackConfig] = field(default_factory=list)
    
    # Global settings
    total_duration_ms: int = 0
    
    # Metadata
    created_timestamp: float = 0.0
    last_modified: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "draft_id": self.draft_id,
            "project": {
                "name": self.project.name,
                "width": self.project.width,
                "height": self.project.height,
                "fps": self.project.fps,
                "video_quality": self.project.video_quality.value,
                "audio_quality": self.project.audio_quality.value,
                "background_color": self.project.background_color
            },
            "media_resources": [
                {
                    "url": res.url,
                    "resource_type": res.resource_type,
                    "duration_ms": res.duration_ms,
                    "file_size": res.file_size,
                    "format": res.format,
                    "width": res.width,
                    "height": res.height,
                    "filename": res.filename
                }
                for res in self.media_resources
            ],
            "tracks": [
                {
                    "track_type": track.track_type,
                    "muted": track.muted,
                    "volume": track.volume,
                    "segments": self._serialize_segments(track.segments)
                }
                for track in self.tracks
            ],
            "total_duration_ms": self.total_duration_ms,
            "created_timestamp": self.created_timestamp,
            "last_modified": self.last_modified
        }
    
    def _serialize_segments(self, segments: List) -> List[Dict[str, Any]]:
        """Serialize segment configurations to dictionaries"""
        result = []
        for segment in segments:
            if isinstance(segment, VideoSegmentConfig):
                result.append(self._serialize_video_segment(segment))
            elif isinstance(segment, AudioSegmentConfig):
                result.append(self._serialize_audio_segment(segment))
            elif isinstance(segment, TextSegmentConfig):
                result.append(self._serialize_text_segment(segment))
            elif isinstance(segment, EffectSegmentConfig):
                result.append(self._serialize_effect_segment(segment))
        return result
    
    def _serialize_video_segment(self, segment: VideoSegmentConfig) -> Dict[str, Any]:
        """Serialize video segment configuration"""
        return {
            "type": "video",
            "material_url": segment.material_url,
            "time_range": {"start": segment.time_range.start, "end": segment.time_range.end},
            "material_range": {"start": segment.material_range.start, "end": segment.material_range.end} if segment.material_range else None,
            "transform": {
                "position_x": segment.position_x,
                "position_y": segment.position_y,
                "scale_x": segment.scale_x,
                "scale_y": segment.scale_y,
                "rotation": segment.rotation,
                "opacity": segment.opacity
            },
            "crop": {
                "enabled": segment.crop_enabled,
                "left": segment.crop_left,
                "top": segment.crop_top,
                "right": segment.crop_right,
                "bottom": segment.crop_bottom
            },
            "effects": {
                "filter_type": segment.filter_type,
                "filter_intensity": segment.filter_intensity,
                "transition_type": segment.transition_type,
                "transition_duration": segment.transition_duration
            },
            "speed": {
                "speed": segment.speed,
                "reverse": segment.reverse
            },
            "background": {
                "blur": segment.background_blur,
                "color": segment.background_color
            },
            "keyframes": {
                "position": [{"time": kf.time, "value": kf.value} for kf in segment.position_keyframes],
                "scale": [{"time": kf.time, "value": kf.value} for kf in segment.scale_keyframes],
                "rotation": [{"time": kf.time, "value": kf.value} for kf in segment.rotation_keyframes],
                "opacity": [{"time": kf.time, "value": kf.value} for kf in segment.opacity_keyframes]
            }
        }
    
    def _serialize_audio_segment(self, segment: AudioSegmentConfig) -> Dict[str, Any]:
        """Serialize audio segment configuration"""
        return {
            "type": "audio",
            "material_url": segment.material_url,
            "time_range": {"start": segment.time_range.start, "end": segment.time_range.end},
            "material_range": {"start": segment.material_range.start, "end": segment.material_range.end} if segment.material_range else None,
            "audio": {
                "volume": segment.volume,
                "fade_in": segment.fade_in,
                "fade_out": segment.fade_out,
                "effect_type": segment.effect_type,
                "effect_intensity": segment.effect_intensity,
                "speed": segment.speed
            },
            "keyframes": {
                "volume": [{"time": kf.time, "value": kf.value} for kf in segment.volume_keyframes]
            }
        }
    
    def _serialize_text_segment(self, segment: TextSegmentConfig) -> Dict[str, Any]:
        """Serialize text segment configuration"""
        return {
            "type": "text",
            "content": segment.content,
            "time_range": {"start": segment.time_range.start, "end": segment.time_range.end},
            "transform": {
                "position_x": segment.position_x,
                "position_y": segment.position_y,
                "scale": segment.scale,
                "rotation": segment.rotation,
                "opacity": segment.opacity
            },
            "style": {
                "font_family": segment.style.font_family,
                "font_size": segment.style.font_size,
                "font_weight": segment.style.font_weight,
                "font_style": segment.style.font_style,
                "color": segment.style.color,
                "stroke": {
                    "enabled": segment.style.stroke_enabled,
                    "color": segment.style.stroke_color,
                    "width": segment.style.stroke_width
                },
                "shadow": {
                    "enabled": segment.style.shadow_enabled,
                    "color": segment.style.shadow_color,
                    "offset_x": segment.style.shadow_offset_x,
                    "offset_y": segment.style.shadow_offset_y,
                    "blur": segment.style.shadow_blur
                },
                "background": {
                    "enabled": segment.style.background_enabled,
                    "color": segment.style.background_color,
                    "opacity": segment.style.background_opacity
                }
            },
            "alignment": segment.alignment,
            "animations": {
                "intro": segment.intro_animation,
                "outro": segment.outro_animation,
                "loop": segment.loop_animation
            },
            "keyframes": {
                "position": [{"time": kf.time, "value": kf.value} for kf in segment.position_keyframes],
                "scale": [{"time": kf.time, "value": kf.value} for kf in segment.scale_keyframes],
                "rotation": [{"time": kf.time, "value": kf.value} for kf in segment.rotation_keyframes],
                "opacity": [{"time": kf.time, "value": kf.value} for kf in segment.opacity_keyframes]
            }
        }
    
    def _serialize_effect_segment(self, segment: EffectSegmentConfig) -> Dict[str, Any]:
        """Serialize effect segment configuration"""
        return {
            "type": "effect",
            "effect_type": segment.effect_type,
            "time_range": {"start": segment.time_range.start, "end": segment.time_range.end},
            "properties": {
                "intensity": segment.intensity,
                "position_x": segment.position_x,
                "position_y": segment.position_y,
                "scale": segment.scale,
                **segment.properties
            }
        }


# Input/Output types for Coze tools
@dataclass
class CreateDraftInput:
    """Input for create_draft tool"""
    project_name: str = "Coze剪映项目"
    width: int = 1920
    height: int = 1080
    fps: int = 30
    video_quality: str = "1080p"
    audio_quality: str = "320k"
    background_color: str = "#000000"


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