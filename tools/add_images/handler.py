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
    image_infos: str                            # JSON string containing array of image info objects


class Output(NamedTuple):
    """Output for add_images tool"""
    segment_ids: List[str]                      # List of generated segment UUIDs
    segment_infos: List[dict]                   # List of segment info with id, start, end


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
    
    # Validate image_infos JSON string
    image_infos_str = getattr(input_data, 'image_infos', None)
    if not image_infos_str:
        return False, "image_infos is required"
    
    if not isinstance(image_infos_str, str):
        return False, "image_infos must be a JSON string"
    
    # Parse JSON
    try:
        image_infos = json.loads(image_infos_str)
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON in image_infos: {str(e)}"
    
    if not isinstance(image_infos, list) or len(image_infos) == 0:
        return False, "image_infos must contain a non-empty array"
    
    # Validate each image info object
    for i, image_info in enumerate(image_infos):
        if not isinstance(image_info, dict):
            return False, f"Image info at index {i} must be an object"
        
        # Required fields
        if "image_url" not in image_info:
            return False, f"Image info at index {i} must have 'image_url' field"
        
        if not isinstance(image_info["image_url"], str) or not image_info["image_url"].strip():
            return False, f"Image info at index {i}: image_url must be a non-empty string"
        
        if "start" not in image_info:
            return False, f"Image info at index {i} must have 'start' field"
        
        if not isinstance(image_info["start"], int) or image_info["start"] < 0:
            return False, f"Image info at index {i}: start must be a non-negative integer"
        
        if "end" not in image_info:
            return False, f"Image info at index {i} must have 'end' field"
        
        if not isinstance(image_info["end"], int) or image_info["end"] <= image_info["start"]:
            return False, f"Image info at index {i}: end must be greater than start"
        
        # Optional fields validation
        if "width" in image_info and (not isinstance(image_info["width"], int) or image_info["width"] <= 0):
            return False, f"Image info at index {i}: width must be a positive integer"
        
        if "height" in image_info and (not isinstance(image_info["height"], int) or image_info["height"] <= 0):
            return False, f"Image info at index {i}: height must be a positive integer"
        
        if "in_animation_duration" in image_info and (not isinstance(image_info["in_animation_duration"], int) or image_info["in_animation_duration"] < 0):
            return False, f"Image info at index {i}: in_animation_duration must be a non-negative integer"
    
    return True, ""


def parse_image_infos(image_infos_str: str) -> List[dict]:
    """Parse and return image infos from JSON string"""
    return json.loads(image_infos_str)


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


def create_image_segments(input_data: Input) -> tuple[List[dict], List[str], List[dict]]:
    """Create image segments from input parameters (treated as video segments)
    
    Returns:
        tuple: (segments, segment_ids, segment_infos)
    """
    import uuid
    
    # Parse image infos from JSON string
    image_infos = parse_image_infos(input_data.image_infos)
    
    segments = []
    segment_ids = []
    segment_infos = []
    
    for i, image_info in enumerate(image_infos):
        # Generate unique segment ID
        segment_id = str(uuid.uuid4())
        segment_ids.append(segment_id)
        
        # Extract parameters from image_info
        image_url = image_info["image_url"]
        start_time = image_info["start"]
        end_time = image_info["end"]
        duration = end_time - start_time
        
        # Optional parameters with defaults
        width = image_info.get("width")
        height = image_info.get("height")
        in_animation = image_info.get("in_animation")
        in_animation_duration = image_info.get("in_animation_duration", 0)
        
        # Create segment info for output
        segment_info = {
            "id": segment_id,
            "start": start_time,
            "end": end_time
        }
        segment_infos.append(segment_info)
        
        # Create image segment (treated as video)
        segment = {
            "type": "video",  # Images are treated as video segments
            "material_url": image_url,
            "segment_id": segment_id,  # Add segment ID to track
            "time_range": {
                "start": start_time,
                "end": end_time
            },
            "material_range": {
                "start": 0,
                "end": duration
            },
            "transform": {
                "position_x": 0.0,  # Default position
                "position_y": 0.0,
                "scale_x": 1.0,     # Default scale
                "scale_y": 1.0,
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
                "transition_type": None,  # Can be extended
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
            },
            # Additional image-specific properties
            "image_properties": {
                "width": width,
                "height": height,
                "in_animation": in_animation,
                "in_animation_duration": in_animation_duration
            }
        }
        
        segments.append(segment)
    
    return segments, segment_ids, segment_infos


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
        logger.info(f"Adding images to draft with parameters: {args.input}")
    
    try:
        # Validate input parameters
        is_valid, error_msg = validate_input_parameters(args.input)
        if not is_valid:
            if logger:
                logger.error(f"Input validation failed: {error_msg}")
            return Output(
                segment_ids=[],
                segment_infos=[]
            )
        
        # Load existing draft configuration
        success, config, error_msg = load_draft_config(args.input.draft_id)
        if not success:
            if logger:
                logger.error(f"Failed to load draft config: {error_msg}")
            return Output(
                segment_ids=[],
                segment_infos=[]
            )
        
        # Create image segments
        image_segments, segment_ids, segment_infos = create_image_segments(args.input)
        
        # Parse image infos to add media resources
        image_infos = parse_image_infos(args.input.image_infos)
        
        # Add media resources to the draft
        if "media_resources" not in config:
            config["media_resources"] = []
        
        for i, image_info in enumerate(image_infos):
            image_url = image_info["image_url"]
            # Check if this resource already exists
            existing = any(res.get("url") == image_url for res in config["media_resources"])
            if not existing:
                duration = image_info["end"] - image_info["start"]
                config["media_resources"].append({
                    "url": image_url,
                    "resource_type": "image",
                    "duration_ms": duration,
                    "file_size": None,
                    "format": image_url.split('.')[-1].lower() if '.' in image_url else "jpg",
                    "width": image_info.get("width"),
                    "height": image_info.get("height"),
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
        
        # Update total duration if necessary
        if image_segments:
            max_end_time = max([seg["time_range"]["end"] for seg in image_segments])
            if max_end_time > config.get("total_duration_ms", 0):
                config["total_duration_ms"] = max_end_time
        
        # Save updated configuration
        success, error_msg = save_draft_config(args.input.draft_id, config)
        if not success:
            if logger:
                logger.error(f"Failed to save draft config: {error_msg}")
            return Output(
                segment_ids=[],
                segment_infos=[]
            )
        
        if logger:
            logger.info(f"Successfully added {len(image_infos)} images to draft {args.input.draft_id}")
        
        return Output(
            segment_ids=segment_ids,
            segment_infos=segment_infos
        )
        
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        if logger:
            logger.error(error_msg)
        return Output(
            segment_ids=[],
            segment_infos=[]
        )