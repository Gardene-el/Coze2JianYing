"""
Add Images Tool Handler

Adds image segments to an existing draft by creating a new image track.
Each call creates a new track containing all the specified images.
"""

import os
import json
import uuid
from typing import NamedTuple, List, Dict, Any, Optional, Union
from runtime import Args


# Input/Output type definitions (required for each Coze tool)
class Input(NamedTuple):
    """Input parameters for add_images tool"""
    draft_id: str                # UUID of the existing draft
    image_infos: Union[str, List[Dict[str, Any]]]  # JSON string or list containing image information


class Output(NamedTuple):
    """Output for add_images tool"""
    segment_ids: List[str]       # List of generated segment UUIDs
    segment_infos: List[Dict[str, Any]]  # List of segment info (id, start, end)
    success: bool = True         # Operation success status
    message: str = "图片添加成功"  # Status message


# Data models (duplicated here for Coze tool independence)
class TimeRange:
    """Time range in milliseconds"""
    def __init__(self, start: int = 0, end: int = 0):
        self.start = start
        self.end = end
    
    @property
    def duration(self) -> int:
        return self.end - self.start


class ImageSegmentConfig:
    """Configuration for an image segment"""
    def __init__(self, material_url: str, time_range: TimeRange, **kwargs):
        self.material_url = material_url
        self.time_range = time_range
        
        # Transform properties
        self.position_x = kwargs.get('position_x', 0.0)
        self.position_y = kwargs.get('position_y', 0.0) 
        self.scale_x = kwargs.get('scale_x', 1.0)
        self.scale_y = kwargs.get('scale_y', 1.0)
        self.rotation = kwargs.get('rotation', 0.0)
        self.opacity = kwargs.get('opacity', 1.0)
        
        # Image dimensions
        self.width = kwargs.get('width')
        self.height = kwargs.get('height')
        
        # Crop settings
        self.crop_enabled = kwargs.get('crop_enabled', False)
        self.crop_left = kwargs.get('crop_left', 0.0)
        self.crop_top = kwargs.get('crop_top', 0.0)
        self.crop_right = kwargs.get('crop_right', 1.0)
        self.crop_bottom = kwargs.get('crop_bottom', 1.0)
        
        # Effects
        self.filter_type = kwargs.get('filter_type')
        self.filter_intensity = kwargs.get('filter_intensity', 1.0)
        self.transition_type = kwargs.get('transition_type')
        self.transition_duration = kwargs.get('transition_duration', 500)
        
        # Background
        self.background_blur = kwargs.get('background_blur', False)
        self.background_color = kwargs.get('background_color')
        self.fit_mode = kwargs.get('fit_mode', 'fit')
        
        # Animations
        self.intro_animation = kwargs.get('in_animation')  # Maps to intro_animation
        self.intro_animation_duration = kwargs.get('in_animation_duration', 500)
        self.outro_animation = kwargs.get('outro_animation')
        self.outro_animation_duration = kwargs.get('outro_animation_duration', 500)
        
        # Keyframes (empty by default)
        self.position_keyframes = []
        self.scale_keyframes = []
        self.rotation_keyframes = []
        self.opacity_keyframes = []


def validate_uuid_format(uuid_str: str) -> bool:
    """Validate UUID string format"""
    try:
        uuid.UUID(uuid_str)
        return True
    except (ValueError, TypeError):
        return False


def parse_image_infos(image_infos_input: Union[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """Parse image_infos JSON string or list and validate format"""
    try:
        # Handle both string and list inputs
        if isinstance(image_infos_input, str):
            # Parse JSON string
            image_infos = json.loads(image_infos_input)
        elif isinstance(image_infos_input, list):
            # Use list directly
            image_infos = image_infos_input
        else:
            raise ValueError(f"image_infos must be a JSON string or list, got {type(image_infos_input)}")
        
        if not isinstance(image_infos, list):
            raise ValueError("image_infos must be a list")
        
        for i, info in enumerate(image_infos):
            if not isinstance(info, dict):
                raise ValueError(f"image_infos[{i}] must be a dictionary")
            
            # Validate required fields
            required_fields = ['image_url', 'start', 'end']
            for field in required_fields:
                if field not in info:
                    raise ValueError(f"Missing required field '{field}' in image_infos[{i}]")
            
            # Map image_url to material_url for consistency
            if 'image_url' in info:
                info['material_url'] = info['image_url']
        
        return image_infos
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format in image_infos: {str(e)}")


def load_draft_config(draft_id: str) -> Dict[str, Any]:
    """Load existing draft configuration"""
    draft_folder = f"/tmp/{draft_id}"
    config_file = os.path.join(draft_folder, "draft_config.json")
    
    if not os.path.exists(draft_folder):
        raise FileNotFoundError(f"Draft with ID {draft_id} not found")
    
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Draft config file not found for ID {draft_id}")
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        raise Exception(f"Failed to load draft config: {str(e)}")


def save_draft_config(draft_id: str, config: Dict[str, Any]) -> None:
    """Save updated draft configuration"""
    draft_folder = f"/tmp/{draft_id}"
    config_file = os.path.join(draft_folder, "draft_config.json")
    
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except Exception as e:
        raise Exception(f"Failed to save draft config: {str(e)}")


def create_image_segments(image_infos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Create image segment configurations from image_infos"""
    segments = []
    
    for info in image_infos:
        segment_id = str(uuid.uuid4())
        
        # Create time range
        time_range = TimeRange(start=info['start'], end=info['end'])
        
        # Create segment config
        segment_config = ImageSegmentConfig(
            material_url=info['material_url'],
            time_range=time_range,
            **info
        )
        
        # Convert to serializable dictionary format
        segment_dict = {
            "id": segment_id,
            "type": "image",
            "material_url": segment_config.material_url,
            "time_range": {"start": segment_config.time_range.start, "end": segment_config.time_range.end},
            "transform": {
                "position_x": segment_config.position_x,
                "position_y": segment_config.position_y,
                "scale_x": segment_config.scale_x,
                "scale_y": segment_config.scale_y,
                "rotation": segment_config.rotation,
                "opacity": segment_config.opacity
            },
            "dimensions": {
                "width": segment_config.width,
                "height": segment_config.height
            },
            "crop": {
                "enabled": segment_config.crop_enabled,
                "left": segment_config.crop_left,
                "top": segment_config.crop_top,
                "right": segment_config.crop_right,
                "bottom": segment_config.crop_bottom
            },
            "effects": {
                "filter_type": segment_config.filter_type,
                "filter_intensity": segment_config.filter_intensity,
                "transition_type": segment_config.transition_type,
                "transition_duration": segment_config.transition_duration
            },
            "background": {
                "blur": segment_config.background_blur,
                "color": segment_config.background_color,
                "fit_mode": segment_config.fit_mode
            },
            "animations": {
                "intro": segment_config.intro_animation,
                "intro_duration": segment_config.intro_animation_duration,
                "outro": segment_config.outro_animation,
                "outro_duration": segment_config.outro_animation_duration
            },
            "keyframes": {
                "position": segment_config.position_keyframes,
                "scale": segment_config.scale_keyframes,
                "rotation": segment_config.rotation_keyframes,
                "opacity": segment_config.opacity_keyframes
            }
        }
        
        segments.append(segment_dict)
    
    return segments


def handler(args: Args[Input]) -> Output:
    """
    Main handler function for adding images to a draft
    
    Args:
        args: Input arguments containing draft_id and image_infos
        
    Returns:
        Output containing segment_ids and segment_infos
    """
    logger = getattr(args, 'logger', None)
    
    if logger:
        logger.info(f"Adding images to draft: {args.input.draft_id}")
    
    try:
        # Validate input parameters
        if not args.input.draft_id:
            return Output(
                segment_ids=[],
                segment_infos=[],
                success=False,
                message="缺少必需的 draft_id 参数"
            )
        
        if not validate_uuid_format(args.input.draft_id):
            return Output(
                segment_ids=[],
                segment_infos=[],
                success=False,
                message="无效的 draft_id 格式"
            )
        
        if not args.input.image_infos:
            return Output(
                segment_ids=[],
                segment_infos=[],
                success=False,
                message="缺少必需的 image_infos 参数"
            )
        
        # Parse image information
        try:
            image_infos = parse_image_infos(args.input.image_infos)
        except ValueError as e:
            return Output(
                segment_ids=[],
                segment_infos=[],
                success=False,
                message=f"解析 image_infos 失败: {str(e)}"
            )
        
        if not image_infos:
            return Output(
                segment_ids=[],
                segment_infos=[],
                success=False,
                message="image_infos 不能为空"
            )
        
        # Load existing draft configuration
        try:
            draft_config = load_draft_config(args.input.draft_id)
        except (FileNotFoundError, Exception) as e:
            return Output(
                segment_ids=[],
                segment_infos=[],
                success=False,
                message=f"加载草稿配置失败: {str(e)}"
            )
        
        # Create image segments
        image_segments = create_image_segments(image_infos)
        
        # Create new image track
        image_track = {
            "track_type": "image",
            "muted": False,
            "volume": 1.0,
            "segments": image_segments
        }
        
        # Add track to draft configuration
        if "tracks" not in draft_config:
            draft_config["tracks"] = []
        
        draft_config["tracks"].append(image_track)
        
        # Update timestamp
        import time
        draft_config["last_modified"] = time.time()
        
        # Save updated configuration
        try:
            save_draft_config(args.input.draft_id, draft_config)
        except Exception as e:
            return Output(
                segment_ids=[],
                segment_infos=[],
                success=False,
                message=f"保存草稿配置失败: {str(e)}"
            )
        
        # Prepare output
        segment_ids = [segment["id"] for segment in image_segments]
        segment_infos = [
            {
                "id": segment["id"],
                "start": segment["time_range"]["start"],
                "end": segment["time_range"]["end"]
            }
            for segment in image_segments
        ]
        
        if logger:
            logger.info(f"Successfully added {len(image_segments)} images to draft {args.input.draft_id}")
        
        return Output(
            segment_ids=segment_ids,
            segment_infos=segment_infos,
            success=True,
            message=f"成功添加 {len(image_segments)} 张图片到草稿"
        )
        
    except Exception as e:
        error_msg = f"添加图片时发生错误: {str(e)}"
        if logger:
            logger.error(error_msg)
        
        return Output(
            segment_ids=[],
            segment_infos=[],
            success=False,
            message=error_msg
        )