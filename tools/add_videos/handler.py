"""
Add Videos Tool Handler

Adds video content to an existing draft by creating a new video track.
Each call to this tool creates a new track containing all the video segments.
"""

import os
import json
import time
from typing import NamedTuple, List, Optional, Union
from runtime import Args


# Input/Output type definitions (required for each Coze tool)
class Input(NamedTuple):
    """Input parameters for add_videos tool"""
    draft_id: str                           # UUID of the draft to modify
    video_urls: List[str]                   # List of video URLs to add
    filters: Optional[List[str]] = None     # Optional filter names for each video
    transitions: Optional[List[str]] = None # Optional transition types between videos
    volumes: Optional[List[float]] = None   # Optional volume settings for each video
    start_time: int = 0                     # Start time in milliseconds on timeline


class Output(NamedTuple):
    """Output for add_videos tool"""
    success: bool = True
    message: str = "视频轨道添加成功"
    track_index: int = -1                   # Index of the created track
    total_duration: int = 0                 # Total duration of added videos in ms


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
    
    # Validate video_urls
    video_urls = getattr(input_data, 'video_urls', None)
    if not video_urls or not isinstance(video_urls, list) or len(video_urls) == 0:
        return False, "video_urls must be a non-empty list"
    
    # Validate URLs
    for i, url in enumerate(video_urls):
        if not isinstance(url, str) or not url.strip():
            return False, f"Invalid video URL at index {i}: {url}"
    
    # Validate optional lists lengths match video_urls
    filters = getattr(input_data, 'filters', None)
    if filters is not None:
        if not isinstance(filters, list) or len(filters) != len(video_urls):
            return False, f"filters list length ({len(filters) if isinstance(filters, list) else 'not list'}) must match video_urls length ({len(video_urls)})"
    
    transitions = getattr(input_data, 'transitions', None)
    if transitions is not None:
        if not isinstance(transitions, list) or len(transitions) != len(video_urls):
            return False, f"transitions list length ({len(transitions) if isinstance(transitions, list) else 'not list'}) must match video_urls length ({len(video_urls)})"
    
    volumes = getattr(input_data, 'volumes', None)
    if volumes is not None:
        if not isinstance(volumes, list) or len(volumes) != len(video_urls):
            return False, f"volumes list length ({len(volumes) if isinstance(volumes, list) else 'not list'}) must match video_urls length ({len(video_urls)})"
        
        # Validate volume values
        for i, volume in enumerate(volumes):
            if not isinstance(volume, (int, float)) or volume < 0 or volume > 2:
                return False, f"Invalid volume at index {i}: {volume} (must be 0-2)"
    
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


def estimate_video_duration(video_url: str) -> int:
    """
    Estimate video duration in milliseconds.
    Since we can't actually download the video, we return a default duration.
    In a real implementation, this would analyze the video file.
    """
    # For now, return a default duration of 10 seconds
    # This should be replaced with actual video analysis in production
    return 10000


def create_video_segments(input_data: Input) -> tuple[List[dict], int]:
    """Create video segments from input parameters"""
    video_urls = input_data.video_urls
    filters = getattr(input_data, 'filters', None) or [None] * len(video_urls)
    transitions = getattr(input_data, 'transitions', None) or [None] * len(video_urls)
    volumes = getattr(input_data, 'volumes', None) or [1.0] * len(video_urls)
    start_time = getattr(input_data, 'start_time', 0)
    
    segments = []
    current_time = start_time
    
    for i, video_url in enumerate(video_urls):
        # Estimate duration for this video
        duration = estimate_video_duration(video_url)
        
        # Create video segment
        segment = {
            "type": "video",
            "material_url": video_url,
            "time_range": {
                "start": current_time,
                "end": current_time + duration
            },
            "material_range": {
                "start": 0,
                "end": duration
            },
            "transform": {
                "position_x": 0.0,
                "position_y": 0.0,
                "scale_x": 1.0,
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
                "filter_type": filters[i],
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
            },
            "volume": volumes[i]  # Add volume for video segments
        }
        
        segments.append(segment)
        current_time += duration
    
    total_duration = current_time - start_time
    return segments, total_duration


def handler(args: Args[Input]) -> Output:
    """
    Main handler function for adding videos to a draft
    
    Args:
        args: Input arguments containing draft_id and video parameters
        
    Returns:
        Output containing success status and track information
    """
    logger = getattr(args, 'logger', None)
    
    if logger:
        logger.info(f"Adding videos to draft with parameters: {args.input}")
    
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
        
        # Create video segments
        video_segments, total_duration = create_video_segments(args.input)
        
        # Add media resources to the draft
        if "media_resources" not in config:
            config["media_resources"] = []
        
        for video_url in args.input.video_urls:
            # Check if this resource already exists
            existing = any(res.get("url") == video_url for res in config["media_resources"])
            if not existing:
                config["media_resources"].append({
                    "url": video_url,
                    "resource_type": "video",
                    "duration_ms": estimate_video_duration(video_url),
                    "file_size": None,
                    "format": video_url.split('.')[-1].lower() if '.' in video_url else "mp4",
                    "width": None,
                    "height": None,
                    "filename": None
                })
        
        # Create new video track
        new_track = {
            "track_type": "video",
            "muted": False,
            "volume": 1.0,
            "segments": video_segments
        }
        
        # Add track to configuration
        if "tracks" not in config:
            config["tracks"] = []
        
        config["tracks"].append(new_track)
        track_index = len(config["tracks"]) - 1
        
        # Update total duration if necessary
        max_end_time = max([seg["time_range"]["end"] for seg in video_segments])
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
            logger.info(f"Successfully added {len(args.input.video_urls)} videos to draft {args.input.draft_id}")
        
        return Output(
            success=True,
            message=f"成功添加 {len(args.input.video_urls)} 个视频到新轨道",
            track_index=track_index,
            total_duration=total_duration
        )
        
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        if logger:
            logger.error(error_msg)
        return Output(
            success=False,
            message=f"添加视频失败: {error_msg}",
            track_index=-1,
            total_duration=0
        )