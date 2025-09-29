"""
Add Audios Tool Handler

Adds audio segments to an existing draft by creating a new audio track.
Each call creates a new track containing all the specified audio segments.
"""

import os
import json
import uuid
import time
from typing import NamedTuple, List, Dict, Any, Optional
from runtime import Args


# Input/Output type definitions (required for each Coze tool)
class Input(NamedTuple):
    """Input parameters for add_audios tool"""
    draft_id: str                # UUID of the existing draft
    audio_infos: Any             # JSON string or list containing audio information (flexible type)


class Output(NamedTuple):
    """Output for add_audios tool"""
    segment_ids: List[str]       # List of generated segment UUIDs
    segment_infos: List[Dict[str, Any]]  # List of segment info (id, start, end)
    success: bool = True         # Operation success status
    message: str = "音频添加成功"  # Status message


# Data models (duplicated here for Coze tool independence)
class TimeRange:
    """Time range in milliseconds"""
    def __init__(self, start: int = 0, end: int = 0):
        self.start = start
        self.end = end
    
    @property
    def duration(self) -> int:
        return self.end - self.start


class AudioSegmentConfig:
    """Configuration for an audio segment"""
    def __init__(self, material_url: str, time_range: TimeRange, **kwargs):
        self.material_url = material_url
        self.time_range = time_range
        
        # Material range (for audio clipping)
        self.material_range = kwargs.get('material_range')
        
        # Audio properties
        self.volume = kwargs.get('volume', 1.0)
        self.fade_in = kwargs.get('fade_in', 0)  # milliseconds
        self.fade_out = kwargs.get('fade_out', 0)  # milliseconds
        
        # Audio effects
        self.effect_type = kwargs.get('effect_type')
        self.effect_intensity = kwargs.get('effect_intensity', 1.0)
        
        # Speed control
        self.speed = kwargs.get('speed', 1.0)
        
        # Volume keyframes (empty by default)
        self.volume_keyframes = []


def validate_uuid_format(uuid_str: str) -> bool:
    """Validate UUID string format"""
    try:
        uuid.UUID(uuid_str)
        return True
    except (ValueError, TypeError):
        return False


def parse_audio_infos(audio_infos_input: Any) -> List[Dict[str, Any]]:
    """Parse audio_infos from any input format and validate"""
    try:
        # Handle multiple input formats with extensive debugging
        if isinstance(audio_infos_input, str):
            # Parse JSON string
            audio_infos = json.loads(audio_infos_input)
        elif isinstance(audio_infos_input, list):
            # Direct list - most common case
            audio_infos = audio_infos_input
        elif hasattr(audio_infos_input, '__iter__') and not isinstance(audio_infos_input, (str, bytes)):
            # Other iterable types
            audio_infos = list(audio_infos_input)
        else:
            # Last resort - try string conversion
            try:
                audio_infos_str = str(audio_infos_input)
                audio_infos = json.loads(audio_infos_str)
            except (json.JSONDecodeError, ValueError):
                raise ValueError(f"Cannot parse audio_infos from type {type(audio_infos_input)}")
        
        # Ensure it's a list
        if not isinstance(audio_infos, list):
            raise ValueError(f"audio_infos must resolve to a list, got {type(audio_infos)}")
        
        # Process each item with very robust handling
        result = []
        for i, info in enumerate(audio_infos):
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
                            raise ValueError(f"audio_infos[{i}] cannot be converted to dictionary (type: {type(info)})")
            
            # Validate required fields
            required_fields = ['audio_url', 'start', 'end']
            for field in required_fields:
                if field not in converted_info:
                    raise ValueError(f"Missing required field '{field}' in audio_infos[{i}]")
            
            # Map audio_url to material_url for consistency
            converted_info['material_url'] = converted_info['audio_url']
            
            result.append(converted_info)
        
        return result
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format in audio_infos: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error parsing audio_infos (type: {type(audio_infos_input)}): {str(e)}")


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


def create_audio_track_with_segments(audio_infos: List[Dict[str, Any]]) -> tuple[List[str], List[Dict[str, Any]], Dict[str, Any]]:
    """
    Create a properly structured audio track with segments following data structure patterns
    
    Returns:
        tuple: (segment_ids, segment_infos, track_dict)
    """
    segment_ids = []
    segment_infos = []
    segments = []
    
    for info in audio_infos:
        segment_id = str(uuid.uuid4())
        segment_ids.append(segment_id)
        
        # Create segment info for return
        segment_infos.append({
            "id": segment_id,
            "start": info['start'],
            "end": info['end']
        })
        
        # Create segment following the proper data structure format
        # This matches the _serialize_audio_segment format from DraftConfig
        segment = {
            "id": segment_id,
            "type": "audio",
            "material_url": info['material_url'],
            "time_range": {
                "start": info['start'],
                "end": info['end']
            },
            "material_range": {
                "start": info.get('material_start', 0),
                "end": info.get('material_end', info['end'] - info['start'])
            } if info.get('material_start') is not None or info.get('material_end') is not None else None,
            "audio": {
                "volume": info.get('volume', 1.0),
                "fade_in": info.get('fade_in', 0),
                "fade_out": info.get('fade_out', 0),
                "effect_type": info.get('effect_type'),
                "effect_intensity": info.get('effect_intensity', 1.0),
                "speed": info.get('speed', 1.0)
            },
            "keyframes": {
                "volume": []  # Will be populated if volume keyframes are provided
            }
        }
        
        segments.append(segment)
    
    # Create track following the proper TrackConfig format
    track = {
        "track_type": "audio",
        "muted": False,
        "volume": 1.0,
        "segments": segments
    }
    
    return segment_ids, segment_infos, track


def handler(args) -> Output:
    """
    Main handler function for adding audios to a draft
    
    Args:
        args: Input arguments containing draft_id and audio_infos
        
    Returns:
        Output containing segment_ids and segment_infos
    """
    logger = getattr(args, 'logger', None)
    
    if logger:
        logger.info(f"Adding audios to draft: {args.input.draft_id}")
    
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
        
        if args.input.audio_infos is None:
            return Output(
                segment_ids=[],
                segment_infos=[],
                success=False,
                message="缺少必需的 audio_infos 参数"
            )
        
        # Parse audio information with detailed logging
        try:
            if logger:
                logger.info(f"About to parse audio_infos: type={type(args.input.audio_infos)}, value={repr(args.input.audio_infos)[:500]}...")
            
            audio_infos = parse_audio_infos(args.input.audio_infos)
            
            if logger:
                logger.info(f"Successfully parsed {len(audio_infos)} audio infos")
                
        except ValueError as e:
            if logger:
                logger.error(f"Failed to parse audio_infos: {str(e)}")
            return Output(
                segment_ids=[],
                segment_infos=[],
                success=False,
                message=f"解析 audio_infos 失败: {str(e)}"
            )
        
        if not audio_infos:
            return Output(
                segment_ids=[],
                segment_infos=[],
                success=False,
                message="audio_infos 不能为空"
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
        
        # Create audio track with segments using proper data structure patterns
        segment_ids, segment_infos, audio_track = create_audio_track_with_segments(audio_infos)
        
        # Add track to draft configuration
        if "tracks" not in draft_config:
            draft_config["tracks"] = []
        
        draft_config["tracks"].append(audio_track)
        
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
            logger.info(f"Successfully added {len(audio_infos)} audios to draft {args.input.draft_id}")
        
        return Output(
            segment_ids=segment_ids,
            segment_infos=segment_infos,
            success=True,
            message=f"成功添加 {len(audio_infos)} 个音频片段"
        )
        
    except Exception as e:
        if logger:
            logger.error(f"Unexpected error in add_audios handler: {str(e)}")
        return Output(
            segment_ids=[],
            segment_infos=[],
            success=False,
            message=f"处理音频添加时发生错误: {str(e)}"
        )