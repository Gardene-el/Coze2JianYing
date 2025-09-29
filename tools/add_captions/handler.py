"""
Add Captions Tool Handler

Adds text/subtitle content to an existing draft by creating a new text track.
Each call to this tool creates a new track containing all the text segments.
"""

import os
import json
import time
from typing import NamedTuple, List, Optional, Dict, Any
from runtime import Args


# Input/Output type definitions (required for each Coze tool)
class Input(NamedTuple):
    """Input parameters for add_captions tool"""
    draft_id: str                               # UUID of the draft to modify
    captions: List[Dict[str, Any]]              # List of caption dictionaries
    font_family: Optional[str] = "思源黑体"      # Font family name
    font_size: Optional[int] = 48               # Font size
    color: Optional[str] = "#FFFFFF"            # Text color
    position_x: Optional[float] = 0.5           # Horizontal position (0-1)
    position_y: Optional[float] = 0.9           # Vertical position (0-1)
    alignment: Optional[str] = "center"         # Text alignment


class Output(NamedTuple):
    """Output for add_captions tool"""
    success: bool = True
    message: str = "字幕轨道添加成功"
    track_index: int = -1                       # Index of the created track
    total_captions: int = 0                     # Total number of captions added


def validate_uuid_format(uuid_str: str) -> bool:
    """Validate UUID string format"""
    try:
        import uuid
        uuid.UUID(uuid_str)
        return True
    except (ValueError, TypeError):
        return False


def validate_caption_dict(caption: Dict[str, Any], index: int) -> tuple[bool, str]:
    """Validate a single caption dictionary"""
    # Check required fields
    if not isinstance(caption, dict):
        return False, f"Caption at index {index} must be a dictionary"
    
    # Validate text content
    if "text" not in caption or not isinstance(caption["text"], str) or not caption["text"].strip():
        return False, f"Caption at index {index} must have non-empty 'text' field"
    
    # Validate start_time
    if "start_time" not in caption:
        return False, f"Caption at index {index} must have 'start_time' field"
    
    start_time = caption["start_time"]
    if not isinstance(start_time, int) or start_time < 0:
        return False, f"Caption at index {index}: start_time must be non-negative integer"
    
    # Validate end_time
    if "end_time" not in caption:
        return False, f"Caption at index {index} must have 'end_time' field"
    
    end_time = caption["end_time"]
    if not isinstance(end_time, int) or end_time <= start_time:
        return False, f"Caption at index {index}: end_time must be greater than start_time"
    
    # Validate optional position fields
    if "position_x" in caption:
        pos_x = caption["position_x"]
        if not isinstance(pos_x, (int, float)) or pos_x < 0 or pos_x > 1:
            return False, f"Caption at index {index}: position_x must be float between 0-1"
    
    if "position_y" in caption:
        pos_y = caption["position_y"]
        if not isinstance(pos_y, (int, float)) or pos_y < 0 or pos_y > 1:
            return False, f"Caption at index {index}: position_y must be float between 0-1"
    
    return True, ""


def validate_input_parameters(input_data: Input) -> tuple[bool, str]:
    """Validate input parameters"""
    # Validate draft_id
    draft_id = getattr(input_data, 'draft_id', None)
    if not draft_id:
        return False, "draft_id is required"
    
    if not validate_uuid_format(draft_id):
        return False, f"Invalid UUID format: {draft_id}"
    
    # Validate captions
    captions = getattr(input_data, 'captions', None)
    if not captions or not isinstance(captions, list) or len(captions) == 0:
        return False, "captions must be a non-empty list"
    
    # Validate each caption
    for i, caption in enumerate(captions):
        is_valid, error_msg = validate_caption_dict(caption, i)
        if not is_valid:
            return False, error_msg
    
    # Validate optional style parameters
    font_size = getattr(input_data, 'font_size', 48)
    if font_size is not None and (not isinstance(font_size, int) or font_size <= 0):
        return False, f"Invalid font_size: {font_size} (must be positive integer)"
    
    color = getattr(input_data, 'color', "#FFFFFF")
    if color is not None and (not isinstance(color, str) or not color.startswith('#') or len(color) != 7):
        return False, f"Invalid color: {color} (must be hex format like #FFFFFF)"
    
    position_x = getattr(input_data, 'position_x', 0.5)
    if position_x is not None and (not isinstance(position_x, (int, float)) or position_x < 0 or position_x > 1):
        return False, f"Invalid position_x: {position_x} (must be float between 0-1)"
    
    position_y = getattr(input_data, 'position_y', 0.9)
    if position_y is not None and (not isinstance(position_y, (int, float)) or position_y < 0 or position_y > 1):
        return False, f"Invalid position_y: {position_y} (must be float between 0-1)"
    
    alignment = getattr(input_data, 'alignment', "center")
    if alignment is not None and alignment not in ["left", "center", "right"]:
        return False, f"Invalid alignment: {alignment} (must be 'left', 'center', or 'right')"
    
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


def create_text_segments(input_data: Input) -> List[dict]:
    """Create text segments from input parameters"""
    captions = input_data.captions
    
    # Get default style settings
    font_family = getattr(input_data, 'font_family', None) or "思源黑体"
    font_size = getattr(input_data, 'font_size', None) or 48
    color = getattr(input_data, 'color', None) or "#FFFFFF"
    default_position_x = getattr(input_data, 'position_x', None) or 0.5
    default_position_y = getattr(input_data, 'position_y', None) or 0.9
    alignment = getattr(input_data, 'alignment', None) or "center"
    
    segments = []
    
    for caption in captions:
        # Use caption-specific position if provided, otherwise use defaults
        position_x = caption.get("position_x", default_position_x)
        position_y = caption.get("position_y", default_position_y)
        
        # Create text segment
        segment = {
            "type": "text",
            "content": caption["text"],
            "time_range": {
                "start": caption["start_time"],
                "end": caption["end_time"]
            },
            "transform": {
                "position_x": position_x,
                "position_y": position_y,
                "scale": 1.0,
                "rotation": 0.0,
                "opacity": 1.0
            },
            "style": {
                "font_family": font_family,
                "font_size": font_size,
                "font_weight": "normal",
                "font_style": "normal",
                "color": color,
                "stroke": {
                    "enabled": False,
                    "color": "#000000",
                    "width": 2
                },
                "shadow": {
                    "enabled": False,
                    "color": "#000000",
                    "offset_x": 2,
                    "offset_y": 2,
                    "blur": 4
                },
                "background": {
                    "enabled": False,
                    "color": "#000000",
                    "opacity": 0.5
                }
            },
            "alignment": alignment,
            "animations": {
                "intro": None,
                "outro": None,
                "loop": None
            },
            "keyframes": {
                "position": [],
                "scale": [],
                "rotation": [],
                "opacity": []
            }
        }
        
        segments.append(segment)
    
    return segments


def handler(args: Args[Input]) -> Output:
    """
    Main handler function for adding captions to a draft
    
    Args:
        args: Input arguments containing draft_id and caption parameters
        
    Returns:
        Output containing success status and track information
    """
    logger = getattr(args, 'logger', None)
    
    if logger:
        logger.info(f"Adding captions to draft with parameters: {args.input}")
    
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
                total_captions=0
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
                total_captions=0
            )
        
        # Create text segments
        text_segments = create_text_segments(args.input)
        
        # Create new text track
        new_track = {
            "track_type": "text",
            "muted": False,
            "volume": 1.0,
            "segments": text_segments
        }
        
        # Add track to configuration
        if "tracks" not in config:
            config["tracks"] = []
        
        config["tracks"].append(new_track)
        track_index = len(config["tracks"]) - 1
        
        # Update total duration if necessary
        if text_segments:
            max_end_time = max([seg["time_range"]["end"] for seg in text_segments])
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
                total_captions=0
            )
        
        if logger:
            logger.info(f"Successfully added {len(args.input.captions)} captions to draft {args.input.draft_id}")
        
        return Output(
            success=True,
            message=f"成功添加 {len(args.input.captions)} 个字幕到新轨道",
            track_index=track_index,
            total_captions=len(args.input.captions)
        )
        
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        if logger:
            logger.error(error_msg)
        return Output(
            success=False,
            message=f"添加字幕失败: {error_msg}",
            track_index=-1,
            total_captions=0
        )