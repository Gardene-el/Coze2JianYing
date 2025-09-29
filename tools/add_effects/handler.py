"""
Add Effects Tool Handler

Adds effect content to an existing draft by creating a new effect track.
Each call to this tool creates a new track containing all the effect segments.
"""

import os
import json
import time
from typing import NamedTuple, List, Optional, Dict, Any
from runtime import Args


# Input/Output type definitions (required for each Coze tool)
class Input(NamedTuple):
    """Input parameters for add_effects tool"""
    draft_id: str                               # UUID of the draft to modify
    effects: List[Dict[str, Any]]               # List of effect dictionaries
    default_intensity: Optional[float] = 1.0   # Default intensity for effects
    default_position_x: Optional[float] = None # Default horizontal position
    default_position_y: Optional[float] = None # Default vertical position
    default_scale: Optional[float] = 1.0       # Default scale factor


class Output(NamedTuple):
    """Output for add_effects tool"""
    success: bool = True
    message: str = "特效轨道添加成功"
    track_index: int = -1                       # Index of the created track
    total_effects: int = 0                      # Total number of effects added


def validate_uuid_format(uuid_str: str) -> bool:
    """Validate UUID string format"""
    try:
        import uuid
        uuid.UUID(uuid_str)
        return True
    except (ValueError, TypeError):
        return False


def validate_effect_dict(effect: Dict[str, Any], index: int) -> tuple[bool, str]:
    """Validate a single effect dictionary"""
    # Check required fields
    if not isinstance(effect, dict):
        return False, f"Effect at index {index} must be a dictionary"
    
    # Validate effect_type
    if "effect_type" not in effect or not isinstance(effect["effect_type"], str) or not effect["effect_type"].strip():
        return False, f"Effect at index {index} must have non-empty 'effect_type' field"
    
    # Validate start_time
    if "start_time" not in effect:
        return False, f"Effect at index {index} must have 'start_time' field"
    
    start_time = effect["start_time"]
    if not isinstance(start_time, int) or start_time < 0:
        return False, f"Effect at index {index}: start_time must be non-negative integer"
    
    # Validate end_time
    if "end_time" not in effect:
        return False, f"Effect at index {index} must have 'end_time' field"
    
    end_time = effect["end_time"]
    if not isinstance(end_time, int) or end_time <= start_time:
        return False, f"Effect at index {index}: end_time must be greater than start_time"
    
    # Validate optional fields
    if "intensity" in effect:
        intensity = effect["intensity"]
        if not isinstance(intensity, (int, float)) or intensity < 0 or intensity > 2:
            return False, f"Effect at index {index}: intensity must be float between 0-2"
    
    if "position_x" in effect:
        pos_x = effect["position_x"]
        if not isinstance(pos_x, (int, float)):
            return False, f"Effect at index {index}: position_x must be a number"
    
    if "position_y" in effect:
        pos_y = effect["position_y"]
        if not isinstance(pos_y, (int, float)):
            return False, f"Effect at index {index}: position_y must be a number"
    
    if "scale" in effect:
        scale = effect["scale"]
        if not isinstance(scale, (int, float)) or scale <= 0:
            return False, f"Effect at index {index}: scale must be positive number"
    
    # Validate properties field if present
    if "properties" in effect and not isinstance(effect["properties"], dict):
        return False, f"Effect at index {index}: properties must be a dictionary"
    
    return True, ""


def validate_input_parameters(input_data: Input) -> tuple[bool, str]:
    """Validate input parameters"""
    # Validate draft_id
    draft_id = getattr(input_data, 'draft_id', None)
    if not draft_id:
        return False, "draft_id is required"
    
    if not validate_uuid_format(draft_id):
        return False, f"Invalid UUID format: {draft_id}"
    
    # Validate effects
    effects = getattr(input_data, 'effects', None)
    if not effects or not isinstance(effects, list) or len(effects) == 0:
        return False, "effects must be a non-empty list"
    
    # Validate each effect
    for i, effect in enumerate(effects):
        is_valid, error_msg = validate_effect_dict(effect, i)
        if not is_valid:
            return False, error_msg
    
    # Validate optional default parameters
    default_intensity = getattr(input_data, 'default_intensity', 1.0)
    if default_intensity is not None and (not isinstance(default_intensity, (int, float)) or default_intensity < 0 or default_intensity > 2):
        return False, f"Invalid default_intensity: {default_intensity} (must be float between 0-2)"
    
    default_position_x = getattr(input_data, 'default_position_x', None)
    if default_position_x is not None and not isinstance(default_position_x, (int, float)):
        return False, f"Invalid default_position_x: {default_position_x} (must be a number)"
    
    default_position_y = getattr(input_data, 'default_position_y', None)
    if default_position_y is not None and not isinstance(default_position_y, (int, float)):
        return False, f"Invalid default_position_y: {default_position_y} (must be a number)"
    
    default_scale = getattr(input_data, 'default_scale', 1.0)
    if default_scale is not None and (not isinstance(default_scale, (int, float)) or default_scale <= 0):
        return False, f"Invalid default_scale: {default_scale} (must be positive number)"
    
    return True, ""


def load_draft_config(draft_id: str) -> tuple[bool, dict, str]:
    """Load draft configuration from file"""
    draft_folder = os.path.join("/tmp", "jianying_assistant", "drafts", draft_id)
    config_file = os.path.join(draft_folder, "draft_config.json")
    
    if not os.path.exists(draft_folder):
        return False, {}, f"Draft folder not found: {draft_id}"
    
    if not os.path.exists(config_file):
        return False, {}, f"Draft config file not found: {draft_id}"
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return True, config, ""
    except Exception as e:
        return False, {}, f"Failed to load draft config: {str(e)}"


def save_draft_config(draft_id: str, config: dict) -> tuple[bool, str]:
    """Save draft configuration to file"""
    draft_folder = os.path.join("/tmp", "jianying_assistant", "drafts", draft_id)
    config_file = os.path.join(draft_folder, "draft_config.json")
    
    try:
        # Update timestamp
        config["last_modified"] = time.time()
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True, ""
    except Exception as e:
        return False, f"Failed to save draft config: {str(e)}"


def create_effect_segments(input_data: Input) -> List[dict]:
    """Create effect segments from input parameters"""
    effects = input_data.effects
    
    # Get default settings
    default_intensity = getattr(input_data, 'default_intensity', None) or 1.0
    default_position_x = getattr(input_data, 'default_position_x', None)
    default_position_y = getattr(input_data, 'default_position_y', None)
    default_scale = getattr(input_data, 'default_scale', None) or 1.0
    
    segments = []
    
    for effect in effects:
        # Use effect-specific values if provided, otherwise use defaults
        intensity = effect.get("intensity", default_intensity)
        position_x = effect.get("position_x", default_position_x)
        position_y = effect.get("position_y", default_position_y)
        scale = effect.get("scale", default_scale)
        properties = effect.get("properties", {})
        
        # Create effect segment
        segment = {
            "type": "effect",
            "effect_type": effect["effect_type"],
            "time_range": {
                "start": effect["start_time"],
                "end": effect["end_time"]
            },
            "properties": {
                "intensity": intensity,
                "position_x": position_x,
                "position_y": position_y,
                "scale": scale,
                **properties  # Merge any additional properties
            }
        }
        
        segments.append(segment)
    
    return segments


def handler(args: Args[Input]) -> Output:
    """
    Main handler function for adding effects to a draft
    
    Args:
        args: Input arguments containing draft_id and effect parameters
        
    Returns:
        Output containing success status and track information
    """
    logger = getattr(args, 'logger', None)
    
    if logger:
        logger.info(f"Adding effects to draft with parameters: {args.input}")
    
    try:
        # Validate input parameters
        is_valid, error_msg = validate_input_parameters(args.input)
        if not is_valid:
            if logger:
                logger.error(f"Input validation failed: {error_msg}")
            return Output(
                success=False,
                message=f"参数验证失败: {error_msg}",
                track_index=-1,
                total_effects=0
            )
        
        # Load existing draft configuration
        success, config, error_msg = load_draft_config(args.input.draft_id)
        if not success:
            if logger:
                logger.error(f"Failed to load draft config: {error_msg}")
            return Output(
                success=False,
                message=f"加载草稿失败: {error_msg}",
                track_index=-1,
                total_effects=0
            )
        
        # Create effect segments
        effect_segments = create_effect_segments(args.input)
        
        # Create new effect track
        new_track = {
            "track_type": "effect",
            "muted": False,
            "volume": 1.0,
            "segments": effect_segments
        }
        
        # Add track to configuration
        if "tracks" not in config:
            config["tracks"] = []
        
        config["tracks"].append(new_track)
        track_index = len(config["tracks"]) - 1
        
        # Update total duration if necessary
        if effect_segments:
            max_end_time = max([seg["time_range"]["end"] for seg in effect_segments])
            if max_end_time > config.get("total_duration_ms", 0):
                config["total_duration_ms"] = max_end_time
        
        # Save updated configuration
        success, error_msg = save_draft_config(args.input.draft_id, config)
        if not success:
            if logger:
                logger.error(f"Failed to save draft config: {error_msg}")
            return Output(
                success=False,
                message=f"保存草稿失败: {error_msg}",
                track_index=-1,
                total_effects=0
            )
        
        if logger:
            logger.info(f"Successfully added {len(args.input.effects)} effects to draft {args.input.draft_id}")
        
        return Output(
            success=True,
            message=f"成功添加 {len(args.input.effects)} 个特效到新轨道",
            track_index=track_index,
            total_effects=len(args.input.effects)
        )
        
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        if logger:
            logger.error(error_msg)
        return Output(
            success=False,
            message=f"添加特效失败: {error_msg}",
            track_index=-1,
            total_effects=0
        )