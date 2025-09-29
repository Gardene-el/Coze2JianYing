"""
Add Images Tool Handler

Adds image content to an existing draft by creating a new video track.
Images are treated as video segments with specified durations.
Each call to this tool creates a new track containing all the image segments.
"""

import os
import json
import time
from typing import NamedTuple, List, Optional, Union
from runtime import Args


# Input/Output type definitions (required for each Coze tool)
class Input(NamedTuple):
    """Input parameters for add_images tool"""
    draft_id: str                               # UUID of the draft to modify
    image_urls: List[str]                       # List of image URLs to add
    durations: Optional[List[int]] = None       # Optional duration for each image in ms
    transitions: Optional[List[str]] = None     # Optional transition types between images
    positions_x: Optional[List[float]] = None   # Optional horizontal positions (0-1)
    positions_y: Optional[List[float]] = None   # Optional vertical positions (0-1)
    scales: Optional[List[float]] = None        # Optional scale factors
    start_time: int = 0                         # Start time in milliseconds on timeline


class Output(NamedTuple):
    """Output for add_images tool"""
    success: bool = True
    message: str = "图片轨道添加成功"
    track_index: int = -1                       # Index of the created track
    total_duration: int = 0                     # Total duration of added images in ms


def validate_uuid_format(uuid_str: str) -> bool:
    """Validate UUID string format"""
    try:
        import uuid
        uuid.UUID(uuid_str)
        return True
    except (ValueError, TypeError):
        return False


def validate_input_parameters(input_data: Input) -> tuple[bool, str]:
    """Validate input parameters"""
    # Validate draft_id
    draft_id = getattr(input_data, 'draft_id', None)
    if not draft_id:
        return False, "draft_id is required"
    
    if not validate_uuid_format(draft_id):
        return False, f"Invalid UUID format: {draft_id}"
    
    # Validate image_urls
    image_urls = getattr(input_data, 'image_urls', None)
    if not image_urls or not isinstance(image_urls, list) or len(image_urls) == 0:
        return False, "image_urls must be a non-empty list"
    
    # Validate URLs
    for i, url in enumerate(image_urls):
        if not isinstance(url, str) or not url.strip():
            return False, f"Invalid image URL at index {i}: {url}"
    
    # Validate optional lists lengths match image_urls
    durations = getattr(input_data, 'durations', None)
    if durations is not None:
        if not isinstance(durations, list) or len(durations) != len(image_urls):
            return False, f"durations list length ({len(durations) if isinstance(durations, list) else 'not list'}) must match image_urls length ({len(image_urls)})"
        
        # Validate duration values
        for i, duration in enumerate(durations):
            if not isinstance(duration, int) or duration <= 0:
                return False, f"Invalid duration at index {i}: {duration} (must be positive integer)"
    
    transitions = getattr(input_data, 'transitions', None)
    if transitions is not None:
        if not isinstance(transitions, list) or len(transitions) != len(image_urls):
            return False, f"transitions list length ({len(transitions) if isinstance(transitions, list) else 'not list'}) must match image_urls length ({len(image_urls)})"
    
    positions_x = getattr(input_data, 'positions_x', None)
    if positions_x is not None:
        if not isinstance(positions_x, list) or len(positions_x) != len(image_urls):
            return False, f"positions_x list length ({len(positions_x) if isinstance(positions_x, list) else 'not list'}) must match image_urls length ({len(image_urls)})"
        
        # Validate position values
        for i, pos_x in enumerate(positions_x):
            if not isinstance(pos_x, (int, float)) or pos_x < -1 or pos_x > 1:
                return False, f"Invalid position_x at index {i}: {pos_x} (must be float between -1 and 1)"
    
    positions_y = getattr(input_data, 'positions_y', None)
    if positions_y is not None:
        if not isinstance(positions_y, list) or len(positions_y) != len(image_urls):
            return False, f"positions_y list length ({len(positions_y) if isinstance(positions_y, list) else 'not list'}) must match image_urls length ({len(image_urls)})"
        
        # Validate position values
        for i, pos_y in enumerate(positions_y):
            if not isinstance(pos_y, (int, float)) or pos_y < -1 or pos_y > 1:
                return False, f"Invalid position_y at index {i}: {pos_y} (must be float between -1 and 1)"
    
    scales = getattr(input_data, 'scales', None)
    if scales is not None:
        if not isinstance(scales, list) or len(scales) != len(image_urls):
            return False, f"scales list length ({len(scales) if isinstance(scales, list) else 'not list'}) must match image_urls length ({len(image_urls)})"
        
        # Validate scale values
        for i, scale in enumerate(scales):
            if not isinstance(scale, (int, float)) or scale <= 0:
                return False, f"Invalid scale at index {i}: {scale} (must be positive number)"
    
    # Validate start_time
    start_time = getattr(input_data, 'start_time', 0)
    if not isinstance(start_time, int) or start_time < 0:
        return False, f"Invalid start_time: {start_time} (must be non-negative integer)"
    
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


def create_image_segments(input_data: Input) -> tuple[List[dict], int]:
    """Create image segments from input parameters (treated as video segments)"""
    image_urls = input_data.image_urls
    durations = getattr(input_data, 'durations', None) or [3000] * len(image_urls)  # Default 3 seconds per image
    transitions = getattr(input_data, 'transitions', None) or [None] * len(image_urls)
    positions_x = getattr(input_data, 'positions_x', None) or [0.0] * len(image_urls)
    positions_y = getattr(input_data, 'positions_y', None) or [0.0] * len(image_urls)
    scales = getattr(input_data, 'scales', None) or [1.0] * len(image_urls)
    start_time = getattr(input_data, 'start_time', 0)
    
    segments = []
    current_time = start_time
    
    for i, image_url in enumerate(image_urls):
        duration = durations[i]
        
        # Create image segment (treated as video)
        segment = {
            "type": "video",  # Images are treated as video segments
            "material_url": image_url,
            "time_range": {
                "start": current_time,
                "end": current_time + duration
            },
            "material_range": {
                "start": 0,
                "end": duration
            },
            "transform": {
                "position_x": positions_x[i],
                "position_y": positions_y[i],
                "scale_x": scales[i],
                "scale_y": scales[i],
                "rotation": 0.0,
                "opacity": 1.0
            },
            "crop": {
                "enabled": False,
                "left": 0.0,
                "top": 0.0,
                "right": 1.0,
                "bottom": 1.0
            },
            "effects": {
                "filter_type": None,
                "filter_intensity": 1.0,
                "transition_type": transitions[i],
                "transition_duration": 500
            },
            "speed": {
                "speed": 1.0,
                "reverse": False
            },
            "background": {
                "blur": False,
                "color": None
            },
            "keyframes": {
                "position": [],
                "scale": [],
                "rotation": [],
                "opacity": []
            }
        }
        
        segments.append(segment)
        current_time += duration
    
    total_duration = current_time - start_time
    return segments, total_duration


def handler(args: Args[Input]) -> Output:
    """
    Main handler function for adding images to a draft
    
    Args:
        args: Input arguments containing draft_id and image parameters
        
    Returns:
        Output containing success status and track information
    """
    logger = getattr(args, 'logger', None)
    
    if logger:
        logger.info(f"Adding images to draft with parameters: {args.input}")
    
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
                total_duration=0
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
                total_duration=0
            )
        
        # Create image segments
        image_segments, total_duration = create_image_segments(args.input)
        
        # Add media resources to the draft
        if "media_resources" not in config:
            config["media_resources"] = []
        
        for i, image_url in enumerate(args.input.image_urls):
            # Check if this resource already exists
            existing = any(res.get("url") == image_url for res in config["media_resources"])
            if not existing:
                durations = getattr(args.input, 'durations', None) or [3000] * len(args.input.image_urls)
                config["media_resources"].append({
                    "url": image_url,
                    "resource_type": "image",
                    "duration_ms": durations[i],
                    "file_size": None,
                    "format": image_url.split('.')[-1].lower() if '.' in image_url else "jpg",
                    "width": None,
                    "height": None,
                    "filename": None
                })
        
        # Create new video track for images
        new_track = {
            "track_type": "video",
            "muted": False,
            "volume": 1.0,
            "segments": image_segments
        }
        
        # Add track to configuration
        if "tracks" not in config:
            config["tracks"] = []
        
        config["tracks"].append(new_track)
        track_index = len(config["tracks"]) - 1
        
        # Update total duration if necessary
        max_end_time = max([seg["time_range"]["end"] for seg in image_segments])
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
                total_duration=0
            )
        
        if logger:
            logger.info(f"Successfully added {len(args.input.image_urls)} images to draft {args.input.draft_id}")
        
        return Output(
            success=True,
            message=f"成功添加 {len(args.input.image_urls)} 个图片到新轨道",
            track_index=track_index,
            total_duration=total_duration
        )
        
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        if logger:
            logger.error(error_msg)
        return Output(
            success=False,
            message=f"添加图片失败: {error_msg}",
            track_index=-1,
            total_duration=0
        )