"""
Add Effects Tool Handler

Adds effect segments to an existing draft by creating a new effect track.
Each call creates a new track containing all the specified effects.
"""

import os
import json
import uuid
import time
from typing import NamedTuple, List, Dict, Any
from runtime import Args


# Input/Output type definitions (required for each Coze tool)
class Input(NamedTuple):
    """Input parameters for add_effects tool"""
    draft_id: str                # UUID of the existing draft
    effect_infos: Any            # JSON string or list containing effect information (flexible type)


class Output(NamedTuple):
    """Output for add_effects tool"""
    segment_ids: List[str]       # List of generated segment UUIDs
    segment_infos: List[Dict[str, Any]]  # List of segment info (id, start, end)
    success: bool = True         # Operation success status
    message: str = "特效添加成功"  # Status message


# Data models (duplicated here for Coze tool independence)
class TimeRange:
    """Time range in milliseconds"""
    def __init__(self, start: int = 0, end: int = 0):
        self.start = start
        self.end = end
    
    @property
    def duration(self) -> int:
        return self.end - self.start


class EffectSegmentConfig:
    """Configuration for an effect segment"""
    def __init__(self, effect_type: str, time_range: TimeRange, **kwargs):
        self.effect_type = effect_type
        self.time_range = time_range
        
        # Effect properties
        self.intensity = kwargs.get('intensity', 1.0)
        self.properties = kwargs.get('properties', {})
        
        # Position (for localized effects)
        self.position_x = kwargs.get('position_x')
        self.position_y = kwargs.get('position_y')
        self.scale = kwargs.get('scale', 1.0)


def validate_uuid_format(uuid_str: str) -> bool:
    """Validate UUID string format"""
    try:
        uuid.UUID(uuid_str)
        return True
    except (ValueError, TypeError):
        return False


def parse_effect_infos(effect_infos_input: Any) -> List[Dict[str, Any]]:
    """Parse effect_infos from any input format and validate"""
    try:
        # Handle multiple input formats with extensive debugging
        if isinstance(effect_infos_input, str):
            # Parse JSON string
            effect_infos = json.loads(effect_infos_input)
        elif isinstance(effect_infos_input, list):
            # Direct list - could be list of dicts OR list of strings
            # Check if first element is a string (array of strings format)
            if effect_infos_input and isinstance(effect_infos_input[0], str):
                # Array of strings - parse each string as JSON
                parsed_infos = []
                for i, info_str in enumerate(effect_infos_input):
                    try:
                        parsed_info = json.loads(info_str)
                        parsed_infos.append(parsed_info)
                    except json.JSONDecodeError as e:
                        raise ValueError(f"Invalid JSON in effect_infos[{i}]: {str(e)}")
                effect_infos = parsed_infos
            else:
                # List of objects (original behavior)
                effect_infos = effect_infos_input
        elif hasattr(effect_infos_input, '__iter__') and not isinstance(effect_infos_input, (str, bytes)):
            # Other iterable types
            effect_infos = list(effect_infos_input)
        else:
            # Last resort - try string conversion
            try:
                effect_infos_str = str(effect_infos_input)
                effect_infos = json.loads(effect_infos_str)
            except (json.JSONDecodeError, ValueError):
                raise ValueError(f"Cannot parse effect_infos from type {type(effect_infos_input)}")
        
        # Ensure it's a list
        if not isinstance(effect_infos, list):
            raise ValueError(f"effect_infos must resolve to a list, got {type(effect_infos)}")
        
        # Process each item with very robust handling
        result = []
        for i, info in enumerate(effect_infos):
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
                            raise ValueError(f"effect_infos[{i}] cannot be converted to dictionary (type: {type(info)})")
            
            # Validate required fields
            required_fields = ['effect_type', 'start', 'end']
            for field in required_fields:
                if field not in converted_info:
                    raise ValueError(f"Missing required field '{field}' in effect_infos[{i}]")
            
            result.append(converted_info)
        
        return result
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format in effect_infos: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error parsing effect_infos (type: {type(effect_infos_input)}): {str(e)}")


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


def create_effect_track_with_segments(effect_infos: List[Dict[str, Any]]) -> tuple[List[str], List[Dict[str, Any]], Dict[str, Any]]:
    """
    Create a properly structured effect track with segments following data structure patterns
    
    Returns:
        tuple: (segment_ids, segment_infos, track_dict)
    """
    segment_ids = []
    segment_infos = []
    segments = []
    
    for info in effect_infos:
        segment_id = str(uuid.uuid4())
        segment_ids.append(segment_id)
        
        # Create segment info for return
        segment_infos.append({
            "id": segment_id,
            "start": info['start'],
            "end": info['end']
        })
        
        # Create segment following the proper data structure format
        # This matches the _serialize_effect_segment format from DraftConfig
        segment = {
            "id": segment_id,
            "type": "effect",
            "effect_type": info['effect_type'],
            "time_range": {
                "start": info['start'],
                "end": info['end']
            },
            "properties": {
                "intensity": info.get('intensity', 1.0),
                "position_x": info.get('position_x'),
                "position_y": info.get('position_y'),
                "scale": info.get('scale', 1.0)
            }
        }
        
        # Add custom properties if provided
        if 'properties' in info and info['properties']:
            segment["properties"].update(info['properties'])
        
        segments.append(segment)
    
    # Create track following the proper TrackConfig format
    track = {
        "track_type": "effect",
        "muted": False,
        "volume": 1.0,
        "segments": segments
    }
    
    return segment_ids, segment_infos, track


def handler(args: Args[Input]) -> Output:
    """
    Main handler function for adding effects to a draft
    
    Args:
        args: Input arguments containing draft_id and effect_infos
        
    Returns:
        Output containing segment_ids and segment_infos
    """
    logger = getattr(args, 'logger', None)
    
    if logger:
        logger.info(f"Adding effects to draft: {args.input.draft_id}")
    
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
        
        if args.input.effect_infos is None:
            return Output(
                segment_ids=[],
                segment_infos=[],
                success=False,
                message="缺少必需的 effect_infos 参数"
            )
        
        # Parse effect information with detailed logging
        try:
            if logger:
                logger.info(f"About to parse effect_infos: type={type(args.input.effect_infos)}, value={repr(args.input.effect_infos)[:500]}...")
            
            effect_infos = parse_effect_infos(args.input.effect_infos)
            
            if logger:
                logger.info(f"Successfully parsed {len(effect_infos)} effect infos")
                
        except ValueError as e:
            if logger:
                logger.error(f"Failed to parse effect_infos: {str(e)}")
            return Output(
                segment_ids=[],
                segment_infos=[],
                success=False,
                message=f"解析 effect_infos 失败: {str(e)}"
            )
        
        if not effect_infos:
            return Output(
                segment_ids=[],
                segment_infos=[],
                success=False,
                message="effect_infos 不能为空"
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
        
        # Create effect track with segments using proper data structure patterns
        segment_ids, segment_infos, effect_track = create_effect_track_with_segments(effect_infos)
        
        # Add track to draft configuration
        if "tracks" not in draft_config:
            draft_config["tracks"] = []
        
        draft_config["tracks"].append(effect_track)
        
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
            logger.info(f"Successfully added {len(effect_infos)} effects to draft {args.input.draft_id}")
        
        return Output(
            segment_ids=segment_ids,
            segment_infos=segment_infos,
            success=True,
            message=f"成功添加 {len(effect_infos)} 个特效到草稿"
        )
        
    except Exception as e:
        error_msg = f"添加特效时发生错误: {str(e)}"
        if logger:
            logger.error(error_msg)
        
        return Output(
            segment_ids=[],
            segment_infos=[],
            success=False,
            message=error_msg
        )
