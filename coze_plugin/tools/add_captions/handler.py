"""
Add Captions Tool Handler

Adds text/caption segments to an existing draft by creating a new text track.
Each call creates a new track containing all the specified captions.
"""

import os
import json
import uuid
import time
from typing import NamedTuple, List, Dict, Any
from runtime import Args


# Input/Output type definitions (required for each Coze tool)
class Input(NamedTuple):
    """Input parameters for add_captions tool"""
    draft_id: str                # UUID of the existing draft
    caption_infos: Any           # JSON string or list containing caption information (flexible type)


class Output(NamedTuple):
    """Output for add_captions tool"""
    segment_ids: List[str]       # List of generated segment UUIDs
    segment_infos: List[Dict[str, Any]]  # List of segment info (id, start, end)
    success: bool = True         # Operation success status
    message: str = "字幕添加成功"  # Status message


# Data models (duplicated here for Coze tool independence)
class TimeRange:
    """Time range in milliseconds"""
    def __init__(self, start: int = 0, end: int = 0):
        self.start = start
        self.end = end
    
    @property
    def duration(self) -> int:
        return self.end - self.start


class TextStyle:
    """Text styling configuration"""
    def __init__(self, **kwargs):
        self.font_family = kwargs.get('font_family', "默认")
        self.font_size = kwargs.get('font_size', 48)
        self.font_weight = kwargs.get('font_weight', "normal")
        self.font_style = kwargs.get('font_style', "normal")
        self.color = kwargs.get('color', "#FFFFFF")
        
        # Text effects
        self.stroke_enabled = kwargs.get('stroke_enabled', False)
        self.stroke_color = kwargs.get('stroke_color', "#000000")
        self.stroke_width = kwargs.get('stroke_width', 2)
        
        self.shadow_enabled = kwargs.get('shadow_enabled', False)
        self.shadow_color = kwargs.get('shadow_color', "#000000")
        self.shadow_offset_x = kwargs.get('shadow_offset_x', 2)
        self.shadow_offset_y = kwargs.get('shadow_offset_y', 2)
        self.shadow_blur = kwargs.get('shadow_blur', 4)
        
        self.background_enabled = kwargs.get('background_enabled', False)
        self.background_color = kwargs.get('background_color', "#000000")
        self.background_opacity = kwargs.get('background_opacity', 0.5)


class TextSegmentConfig:
    """Configuration for a text/caption segment"""
    def __init__(self, content: str, time_range: TimeRange, **kwargs):
        self.content = content
        self.time_range = time_range
        
        # Position and transform
        self.position_x = kwargs.get('position_x', 0.5)
        self.position_y = kwargs.get('position_y', -0.9)
        self.scale = kwargs.get('scale', 1.0)
        self.rotation = kwargs.get('rotation', 0.0)
        self.opacity = kwargs.get('opacity', 1.0)
        
        # Text styling
        self.style = TextStyle(**kwargs)
        
        # Alignment
        self.alignment = kwargs.get('alignment', 'center')
        
        # Animations
        self.intro_animation = kwargs.get('intro_animation')
        self.outro_animation = kwargs.get('outro_animation')
        self.loop_animation = kwargs.get('loop_animation')
        
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


def parse_caption_infos(caption_infos_input: Any) -> List[Dict[str, Any]]:
    """Parse caption_infos from any input format and validate"""
    try:
        # Handle multiple input formats with extensive debugging
        if isinstance(caption_infos_input, str):
            # Parse JSON string
            caption_infos = json.loads(caption_infos_input)
        elif isinstance(caption_infos_input, list):
            # Direct list - could be list of dicts OR list of strings
            # Check if first element is a string (array of strings format)
            if caption_infos_input and isinstance(caption_infos_input[0], str):
                # Array of strings - parse each string as JSON
                parsed_infos = []
                for i, info_str in enumerate(caption_infos_input):
                    try:
                        parsed_info = json.loads(info_str)
                        parsed_infos.append(parsed_info)
                    except json.JSONDecodeError as e:
                        raise ValueError(f"Invalid JSON in caption_infos[{i}]: {str(e)}")
                caption_infos = parsed_infos
            else:
                # List of objects (original behavior)
                caption_infos = caption_infos_input
        elif hasattr(caption_infos_input, '__iter__') and not isinstance(caption_infos_input, (str, bytes)):
            # Other iterable types
            caption_infos = list(caption_infos_input)
        else:
            # Last resort - try string conversion
            try:
                caption_infos_str = str(caption_infos_input)
                caption_infos = json.loads(caption_infos_str)
            except (json.JSONDecodeError, ValueError):
                raise ValueError(f"Cannot parse caption_infos from type {type(caption_infos_input)}")
        
        # Ensure it's a list
        if not isinstance(caption_infos, list):
            raise ValueError(f"caption_infos must resolve to a list, got {type(caption_infos)}")
        
        # Process each item with very robust handling
        result = []
        for i, info in enumerate(caption_infos):
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
                            raise ValueError(f"caption_infos[{i}] cannot be converted to dictionary (type: {type(info)})")
            
            # Validate required fields
            required_fields = ['content', 'start', 'end']
            for field in required_fields:
                if field not in converted_info:
                    raise ValueError(f"Missing required field '{field}' in caption_infos[{i}]")
            
            result.append(converted_info)
        
        return result
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format in caption_infos: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error parsing caption_infos (type: {type(caption_infos_input)}): {str(e)}")


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


def create_text_track_with_segments(caption_infos: List[Dict[str, Any]]) -> tuple[List[str], List[Dict[str, Any]], Dict[str, Any]]:
    """
    Create a properly structured text track with segments following data structure patterns
    
    Returns:
        tuple: (segment_ids, segment_infos, track_dict)
    """
    segment_ids = []
    segment_infos = []
    segments = []
    
    for info in caption_infos:
        segment_id = str(uuid.uuid4())
        segment_ids.append(segment_id)
        
        # Create segment info for return
        segment_infos.append({
            "id": segment_id,
            "start": info['start'],
            "end": info['end']
        })
        
        # Create segment following the proper data structure format
        # This matches the _serialize_text_segment format from DraftConfig
        segment = {
            "id": segment_id,
            "type": "text",
            "content": info['content'],
            "time_range": {
                "start": info['start'],
                "end": info['end']
            },
            "transform": {
                "position_x": info.get('position_x', 0.5),
                "position_y": info.get('position_y', -0.9),
                "scale": info.get('scale', 1.0),
                "rotation": info.get('rotation', 0.0),
                "opacity": info.get('opacity', 1.0)
            },
            "style": {
                "font_family": info.get('font_family', "默认"),
                "font_size": info.get('font_size', 48),
                "font_weight": info.get('font_weight', "normal"),
                "font_style": info.get('font_style', "normal"),
                "color": info.get('color', "#FFFFFF"),
                "stroke": {
                    "enabled": info.get('stroke_enabled', False),
                    "color": info.get('stroke_color', "#000000"),
                    "width": info.get('stroke_width', 2)
                },
                "shadow": {
                    "enabled": info.get('shadow_enabled', False),
                    "color": info.get('shadow_color', "#000000"),
                    "offset_x": info.get('shadow_offset_x', 2),
                    "offset_y": info.get('shadow_offset_y', 2),
                    "blur": info.get('shadow_blur', 4)
                },
                "background": {
                    "enabled": info.get('background_enabled', False),
                    "color": info.get('background_color', "#000000"),
                    "opacity": info.get('background_opacity', 0.5)
                }
            },
            "alignment": info.get('alignment', 'center'),
            "animations": {
                "intro": info.get('intro_animation'),
                "outro": info.get('outro_animation'),
                "loop": info.get('loop_animation')
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
        "track_type": "text",
        "muted": False,
        "volume": 1.0,
        "segments": segments
    }
    
    return segment_ids, segment_infos, track


def handler(args: Args[Input]) -> Output:
    """
    Main handler function for adding captions to a draft
    
    Args:
        args: Input arguments containing draft_id and caption_infos
        
    Returns:
        Output containing segment_ids and segment_infos
    """
    logger = getattr(args, 'logger', None)
    
    if logger:
        logger.info(f"Adding captions to draft: {args.input.draft_id}")
    
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
        
        if args.input.caption_infos is None:
            return Output(
                segment_ids=[],
                segment_infos=[],
                success=False,
                message="缺少必需的 caption_infos 参数"
            )
        
        # Parse caption information with detailed logging
        try:
            if logger:
                logger.info(f"About to parse caption_infos: type={type(args.input.caption_infos)}, value={repr(args.input.caption_infos)[:500]}...")
            
            caption_infos = parse_caption_infos(args.input.caption_infos)
            
            if logger:
                logger.info(f"Successfully parsed {len(caption_infos)} caption infos")
                
        except ValueError as e:
            if logger:
                logger.error(f"Failed to parse caption_infos: {str(e)}")
            return Output(
                segment_ids=[],
                segment_infos=[],
                success=False,
                message=f"解析 caption_infos 失败: {str(e)}"
            )
        
        if not caption_infos:
            return Output(
                segment_ids=[],
                segment_infos=[],
                success=False,
                message="caption_infos 不能为空"
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
        
        # Create text track with segments using proper data structure patterns
        segment_ids, segment_infos, text_track = create_text_track_with_segments(caption_infos)
        
        # Add track to draft configuration
        if "tracks" not in draft_config:
            draft_config["tracks"] = []
        
        draft_config["tracks"].append(text_track)
        
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
            logger.info(f"Successfully added {len(caption_infos)} captions to draft {args.input.draft_id}")
        
        return Output(
            segment_ids=segment_ids,
            segment_infos=segment_infos,
            success=True,
            message=f"成功添加 {len(caption_infos)} 条字幕到草稿"
        )
        
    except Exception as e:
        error_msg = f"添加字幕时发生错误: {str(e)}"
        if logger:
            logger.error(error_msg)
        
        return Output(
            segment_ids=[],
            segment_infos=[],
            success=False,
            message=error_msg
        )
