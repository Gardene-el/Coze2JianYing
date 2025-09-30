"""
Add Images Tool Handler

Adds image segments to an existing draft by creating a new image track.
Each call creates a new track containing all the specified images.
"""

import os
import json
import uuid
import time
from typing import NamedTuple, List, Dict, Any
from runtime import Args


# Input/Output type definitions (required for each Coze tool)
class Input(NamedTuple):
    """Input parameters for add_images tool"""
    draft_id: str                # UUID of the existing draft
    image_infos: Any             # JSON string or list containing image information (flexible type)


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


def parse_image_infos(image_infos_input: Any) -> List[Dict[str, Any]]:
    """Parse image_infos from any input format and validate"""
    try:
        # Handle multiple input formats with extensive debugging
        if isinstance(image_infos_input, str):
            # Parse JSON string
            image_infos = json.loads(image_infos_input)
        elif isinstance(image_infos_input, list):
            # Direct list - could be list of dicts OR list of strings
            # Check if first element is a string (array of strings format)
            if image_infos_input and isinstance(image_infos_input[0], str):
                # Array of strings - parse each string as JSON
                parsed_infos = []
                for i, info_str in enumerate(image_infos_input):
                    try:
                        parsed_info = json.loads(info_str)
                        parsed_infos.append(parsed_info)
                    except json.JSONDecodeError as e:
                        raise ValueError(f"Invalid JSON in image_infos[{i}]: {str(e)}")
                image_infos = parsed_infos
            else:
                # List of objects (original behavior)
                image_infos = image_infos_input
        elif hasattr(image_infos_input, '__iter__') and not isinstance(image_infos_input, (str, bytes)):
            # Other iterable types
            image_infos = list(image_infos_input)
        else:
            # Last resort - try string conversion
            try:
                image_infos_str = str(image_infos_input)
                image_infos = json.loads(image_infos_str)
            except (json.JSONDecodeError, ValueError):
                raise ValueError(f"Cannot parse image_infos from type {type(image_infos_input)}")
        
        # Ensure it's a list
        if not isinstance(image_infos, list):
            raise ValueError(f"image_infos must resolve to a list, got {type(image_infos)}")
        
        # Process each item with very robust handling
        result = []
        for i, info in enumerate(image_infos):
            # Convert to plain dict - handle various object types
            if isinstance(info, dict):
                # Already a plain dict
                converted_info = dict(info)  # Make a copy to be safe
            else:
                # Try various conversion strategies
                converted_info = {}
                
                # Strategy 1: Try to access like a dict
                try:
                    if hasattr(info, 'keys') and hasattr(info, '__getitem__'):
                        for key in info.keys():
                            converted_info[key] = info[key]
                    else:
                        raise TypeError("Not dict-like")
                except Exception:
                    # Strategy 2: Try vars() for object attributes
                    try:
                        converted_info = vars(info)
                    except Exception:
                        # Strategy 3: Try dir() and getattr
                        try:
                            for attr in dir(info):
                                if not attr.startswith('_'):
                                    converted_info[attr] = getattr(info, attr)
                        except Exception:
                            raise ValueError(f"image_infos[{i}] cannot be converted to dictionary (type: {type(info)})")
            
            # Validate required fields
            required_fields = ['image_url', 'start', 'end']
            for field in required_fields:
                if field not in converted_info:
                    raise ValueError(f"Missing required field '{field}' in image_infos[{i}]")
            
            # Map image_url to material_url for consistency
            converted_info['material_url'] = converted_info['image_url']
            
            result.append(converted_info)
        
        return result
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format in image_infos: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error parsing image_infos (type: {type(image_infos_input)}): {str(e)}")


def load_draft_config(draft_id: str) -> Dict[str, Any]:
    """Load existing draft configuration"""
    draft_folder = os.path.join("/tmp", "jianying_assistant", "drafts", draft_id)
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
    draft_folder = os.path.join("/tmp", "jianying_assistant", "drafts", draft_id)
    config_file = os.path.join(draft_folder, "draft_config.json")
    
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except Exception as e:
        raise Exception(f"Failed to save draft config: {str(e)}")


def create_image_track_with_segments(image_infos: List[Dict[str, Any]]) -> tuple[List[str], List[Dict[str, Any]], Dict[str, Any]]:
    """
    Create a properly structured image track with segments following data structure patterns
    
    Returns:
        tuple: (segment_ids, segment_infos, track_dict)
    """
    segment_ids = []
    segment_infos = []
    segments = []
    
    for info in image_infos:
        segment_id = str(uuid.uuid4())
        segment_ids.append(segment_id)
        
        # Create segment info for return
        segment_infos.append({
            "id": segment_id,
            "start": info['start'],
            "end": info['end']
        })
        
        # Create segment following the proper data structure format
        # This matches the _serialize_image_segment format from DraftConfig
        segment = {
            "id": segment_id,
            "type": "image",
            "material_url": info['material_url'],
            "time_range": {
                "start": info['start'],
                "end": info['end']
            },
            "transform": {
                "position_x": info.get('position_x', 0.0),
                "position_y": info.get('position_y', 0.0),
                "scale_x": info.get('scale_x', 1.0),
                "scale_y": info.get('scale_y', 1.0),
                "rotation": info.get('rotation', 0.0),
                "opacity": info.get('opacity', 1.0)
            },
            "dimensions": {
                "width": info.get('width'),
                "height": info.get('height')
            },
            "crop": {
                "enabled": info.get('crop_enabled', False),
                "left": info.get('crop_left', 0.0),
                "top": info.get('crop_top', 0.0),
                "right": info.get('crop_right', 1.0),
                "bottom": info.get('crop_bottom', 1.0)
            },
            "effects": {
                "filter_type": info.get('filter_type'),
                "filter_intensity": info.get('filter_intensity', 1.0),
                "transition_type": info.get('transition_type'),
                "transition_duration": info.get('transition_duration', 500)
            },
            "background": {
                "blur": info.get('background_blur', False),
                "color": info.get('background_color'),
                "fit_mode": info.get('fit_mode', 'fit')
            },
            "animations": {
                "intro": info.get('in_animation'),  # Map in_animation to intro
                "intro_duration": info.get('in_animation_duration', 500),
                "outro": info.get('outro_animation'),
                "outro_duration": info.get('outro_animation_duration', 500)
            },
            "keyframes": {
                "position": [],
                "scale": [],
                "rotation": [],
                "opacity": []
            }
        }
        
        segments.append(segment)
    
    # Create track following the proper TrackConfig format
    track = {
        "track_type": "image",
        "muted": False,
        "volume": 1.0,
        "segments": segments
    }
    
    return segment_ids, segment_infos, track


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
        
        if args.input.image_infos is None:
            return Output(
                segment_ids=[],
                segment_infos=[],
                success=False,
                message="缺少必需的 image_infos 参数"
            )
        
        # Parse image information with detailed logging
        try:
            if logger:
                logger.info(f"About to parse image_infos: type={type(args.input.image_infos)}, value={repr(args.input.image_infos)[:500]}...")
            
            image_infos = parse_image_infos(args.input.image_infos)
            
            if logger:
                logger.info(f"Successfully parsed {len(image_infos)} image infos")
                
        except ValueError as e:
            if logger:
                logger.error(f"Failed to parse image_infos: {str(e)}")
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
        
        # Create image track with segments using proper data structure patterns
        segment_ids, segment_infos, image_track = create_image_track_with_segments(image_infos)
        
        # Add track to draft configuration
        if "tracks" not in draft_config:
            draft_config["tracks"] = []
        
        draft_config["tracks"].append(image_track)
        
        # Update timestamp
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
        
        if logger:
            logger.info(f"Successfully added {len(image_infos)} images to draft {args.input.draft_id}")
        
        return Output(
            segment_ids=segment_ids,
            segment_infos=segment_infos,
            success=True,
            message=f"成功添加 {len(image_infos)} 张图片到草稿"
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