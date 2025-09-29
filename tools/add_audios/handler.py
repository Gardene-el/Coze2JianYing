"""
Add Audios Tool Handler

Adds audio content to an existing draft by creating a new audio track.
Each call to this tool creates a new track containing all the audio segments.
"""

import os
import json
import time
from typing import NamedTuple, List, Optional, Union
from runtime import Args


# Input/Output type definitions (required for each Coze tool)
class Input(NamedTuple):
    """Input parameters for add_audios tool"""
    draft_id: str                           # UUID of the draft to modify
    audio_urls: List[str]                   # List of audio URLs to add
    volumes: Optional[List[float]] = None   # Optional volume settings for each audio
    fade_ins: Optional[List[int]] = None    # Optional fade-in durations in ms
    fade_outs: Optional[List[int]] = None   # Optional fade-out durations in ms
    effects: Optional[List[str]] = None     # Optional audio effect types
    start_time: int = 0                     # Start time in milliseconds on timeline


class Output(NamedTuple):
    """Output for add_audios tool"""
    success: bool = True
    message: str = "音频轨道添加成功"
    track_index: int = -1                   # Index of the created track
    total_duration: int = 0                 # Total duration of added audios in ms


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
    
    # Validate audio_urls
    audio_urls = getattr(input_data, 'audio_urls', None)
    if not audio_urls or not isinstance(audio_urls, list) or len(audio_urls) == 0:
        return False, "audio_urls must be a non-empty list"
    
    # Validate URLs
    for i, url in enumerate(audio_urls):
        if not isinstance(url, str) or not url.strip():
            return False, f"Invalid audio URL at index {i}: {url}"
    
    # Validate optional lists lengths match audio_urls
    volumes = getattr(input_data, 'volumes', None)
    if volumes is not None:
        if not isinstance(volumes, list) or len(volumes) != len(audio_urls):
            return False, f"volumes list length ({len(volumes) if isinstance(volumes, list) else 'not list'}) must match audio_urls length ({len(audio_urls)})"
        
        # Validate volume values
        for i, volume in enumerate(volumes):
            if not isinstance(volume, (int, float)) or volume < 0 or volume > 2:
                return False, f"Invalid volume at index {i}: {volume} (must be 0-2)"
    
    fade_ins = getattr(input_data, 'fade_ins', None)
    if fade_ins is not None:
        if not isinstance(fade_ins, list) or len(fade_ins) != len(audio_urls):
            return False, f"fade_ins list length ({len(fade_ins) if isinstance(fade_ins, list) else 'not list'}) must match audio_urls length ({len(audio_urls)})"
        
        # Validate fade-in values
        for i, fade_in in enumerate(fade_ins):
            if not isinstance(fade_in, int) or fade_in < 0:
                return False, f"Invalid fade_in at index {i}: {fade_in} (must be non-negative integer)"
    
    fade_outs = getattr(input_data, 'fade_outs', None)
    if fade_outs is not None:
        if not isinstance(fade_outs, list) or len(fade_outs) != len(audio_urls):
            return False, f"fade_outs list length ({len(fade_outs) if isinstance(fade_outs, list) else 'not list'}) must match audio_urls length ({len(audio_urls)})"
        
        # Validate fade-out values
        for i, fade_out in enumerate(fade_outs):
            if not isinstance(fade_out, int) or fade_out < 0:
                return False, f"Invalid fade_out at index {i}: {fade_out} (must be non-negative integer)"
    
    effects = getattr(input_data, 'effects', None)
    if effects is not None:
        if not isinstance(effects, list) or len(effects) != len(audio_urls):
            return False, f"effects list length ({len(effects) if isinstance(effects, list) else 'not list'}) must match audio_urls length ({len(audio_urls)})"
    
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


def estimate_audio_duration(audio_url: str) -> int:
    """
    Estimate audio duration in milliseconds.
    Since we can't actually download the audio, we return a default duration.
    In a real implementation, this would analyze the audio file.
    """
    # For now, return a default duration of 30 seconds for audio
    # This should be replaced with actual audio analysis in production
    return 30000


def create_audio_segments(input_data: Input) -> tuple[List[dict], int]:
    """Create audio segments from input parameters"""
    audio_urls = input_data.audio_urls
    volumes = getattr(input_data, 'volumes', None) or [1.0] * len(audio_urls)
    fade_ins = getattr(input_data, 'fade_ins', None) or [0] * len(audio_urls)
    fade_outs = getattr(input_data, 'fade_outs', None) or [0] * len(audio_urls)
    effects = getattr(input_data, 'effects', None) or [None] * len(audio_urls)
    start_time = getattr(input_data, 'start_time', 0)
    
    segments = []
    current_time = start_time
    
    for i, audio_url in enumerate(audio_urls):
        # Estimate duration for this audio
        duration = estimate_audio_duration(audio_url)
        
        # Create audio segment
        segment = {
            "type": "audio",
            "material_url": audio_url,
            "time_range": {
                "start": current_time,
                "end": current_time + duration
            },
            "material_range": {
                "start": 0,
                "end": duration
            },
            "audio": {
                "volume": volumes[i],
                "fade_in": fade_ins[i],
                "fade_out": fade_outs[i],
                "effect_type": effects[i],
                "effect_intensity": 1.0,
                "speed": 1.0
            },
            "keyframes": {
                "volume": []
            }
        }
        
        segments.append(segment)
        current_time += duration
    
    total_duration = current_time - start_time
    return segments, total_duration


def handler(args: Args[Input]) -> Output:
    """
    Main handler function for adding audios to a draft
    
    Args:
        args: Input arguments containing draft_id and audio parameters
        
    Returns:
        Output containing success status and track information
    """
    logger = getattr(args, 'logger', None)
    
    if logger:
        logger.info(f"Adding audios to draft with parameters: {args.input}")
    
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
        
        # Create audio segments
        audio_segments, total_duration = create_audio_segments(args.input)
        
        # Add media resources to the draft
        if "media_resources" not in config:
            config["media_resources"] = []
        
        for audio_url in args.input.audio_urls:
            # Check if this resource already exists
            existing = any(res.get("url") == audio_url for res in config["media_resources"])
            if not existing:
                config["media_resources"].append({
                    "url": audio_url,
                    "resource_type": "audio",
                    "duration_ms": estimate_audio_duration(audio_url),
                    "file_size": None,
                    "format": audio_url.split('.')[-1].lower() if '.' in audio_url else "mp3",
                    "width": None,
                    "height": None,
                    "filename": None
                })
        
        # Create new audio track
        new_track = {
            "track_type": "audio",
            "muted": False,
            "volume": 1.0,
            "segments": audio_segments
        }
        
        # Add track to configuration
        if "tracks" not in config:
            config["tracks"] = []
        
        config["tracks"].append(new_track)
        track_index = len(config["tracks"]) - 1
        
        # Update total duration if necessary
        max_end_time = max([seg["time_range"]["end"] for seg in audio_segments])
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
            logger.info(f"Successfully added {len(args.input.audio_urls)} audios to draft {args.input.draft_id}")
        
        return Output(
            success=True,
            message=f"成功添加 {len(args.input.audio_urls)} 个音频到新轨道",
            track_index=track_index,
            total_duration=total_duration
        )
        
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        if logger:
            logger.error(error_msg)
        return Output(
            success=False,
            message=f"添加音频失败: {error_msg}",
            track_index=-1,
            total_duration=0
        )