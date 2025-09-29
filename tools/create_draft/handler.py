"""
Create Draft Tool Handler

Creates a new draft with basic project settings and returns a UUID for future reference.
The draft data is stored in /tmp directory with UUID as folder name.
"""

import os
import json
import uuid
import time
from typing import NamedTuple
from runtime import Args


# Input/Output type definitions (required for each Coze tool)
class Input(NamedTuple):
    """Input parameters for create_draft tool"""
    draft_name: str = "Coze剪映项目"
    width: int = 1920
    height: int = 1080
    fps: int = 30
    video_quality: str = "1080p"
    audio_quality: str = "320k"
    background_color: str = "#000000"


class Output(NamedTuple):
    """Output for create_draft tool"""
    draft_id: str
    success: bool = True
    message: str = "草稿创建成功"


# Data models (duplicated here for Coze tool independence)
class VideoQuality:
    """Video quality settings"""
    SD_480P = "480p"
    HD_720P = "720p"
    FHD_1080P = "1080p"
    QHD_1440P = "1440p"
    UHD_4K = "4k"


class AudioQuality:
    """Audio quality settings"""
    LOW_128K = "128k"
    MEDIUM_192K = "192k"
    HIGH_320K = "320k"
    LOSSLESS = "lossless"


def validate_input_parameters(input_data: Input) -> tuple[bool, str]:
    """
    Validate input parameters for create_draft
    
    Args:
        input_data: Input parameters
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Validate dimensions (handle None values)
    width = getattr(input_data, 'width', None) or 1920
    height = getattr(input_data, 'height', None) or 1080
    if width <= 0 or height <= 0:
        return False, f"Invalid dimensions: {width}x{height}"
    
    # Validate fps (handle None values)
    fps = getattr(input_data, 'fps', None) or 30
    if fps <= 0 or fps > 120:
        return False, f"Invalid fps: {fps}"
    
    # Validate video quality (handle None values)
    video_quality = getattr(input_data, 'video_quality', None) or "1080p"
    valid_video_qualities = [VideoQuality.SD_480P, VideoQuality.HD_720P, 
                           VideoQuality.FHD_1080P, VideoQuality.QHD_1440P, VideoQuality.UHD_4K]
    if video_quality not in valid_video_qualities:
        return False, f"Invalid video quality: {video_quality}"
    
    # Validate audio quality (handle None values)
    audio_quality = getattr(input_data, 'audio_quality', None) or "320k"
    valid_audio_qualities = [AudioQuality.LOW_128K, AudioQuality.MEDIUM_192K, 
                           AudioQuality.HIGH_320K, AudioQuality.LOSSLESS]
    if audio_quality not in valid_audio_qualities:
        return False, f"Invalid audio quality: {audio_quality}"
    
    # Validate background color (handle None values)
    background_color = getattr(input_data, 'background_color', None) or "#000000"
    if not background_color.startswith('#') or len(background_color) != 7:
        return False, f"Invalid background color: {background_color}"
    
    return True, ""


def create_draft_folder(draft_id: str) -> str:
    """
    Create draft folder in /tmp/jianying_assistant/drafts/ directory
    
    Args:
        draft_id: UUID string for the draft
        
    Returns:
        Path to created draft folder
        
    Raises:
        Exception: If folder creation fails
    """
    # Create the base directory structure
    base_dir = os.path.join("/tmp", "jianying_assistant", "drafts")
    draft_folder = os.path.join(base_dir, draft_id)
    
    try:
        # Create the full directory structure including parents
        os.makedirs(draft_folder, exist_ok=True)
        return draft_folder
    except Exception as e:
        raise Exception(f"Failed to create draft folder: {str(e)}")


def create_initial_draft_config(input_data: Input, draft_id: str, draft_folder: str) -> None:
    """
    Create initial draft configuration file
    
    Args:
        input_data: Input parameters
        draft_id: UUID string for the draft
        draft_folder: Path to draft folder
        
    Raises:
        Exception: If config creation fails
    """
    timestamp = time.time()
    
    # Handle None values and provide defaults
    draft_name = getattr(input_data, 'draft_name', None) or "Coze剪映项目"
    width = getattr(input_data, 'width', None) or 1920
    height = getattr(input_data, 'height', None) or 1080
    fps = getattr(input_data, 'fps', None) or 30
    video_quality = getattr(input_data, 'video_quality', None) or "1080p"
    audio_quality = getattr(input_data, 'audio_quality', None) or "320k"
    background_color = getattr(input_data, 'background_color', None) or "#000000"
    
    # Create initial draft configuration
    draft_config = {
        "draft_id": draft_id,
        "project": {
            "name": draft_name,
            "width": width,
            "height": height,
            "fps": fps,
            "video_quality": video_quality,
            "audio_quality": audio_quality,
            "background_color": background_color
        },
        "media_resources": [],
        "tracks": [],
        "total_duration_ms": 0,
        "created_timestamp": timestamp,
        "last_modified": timestamp,
        "status": "created"
    }
    
    # Save configuration to file
    config_file = os.path.join(draft_folder, "draft_config.json")
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(draft_config, f, ensure_ascii=False, indent=2)
    except Exception as e:
        raise Exception(f"Failed to save draft config: {str(e)}")


def handler(args: Args[Input]) -> Output:
    """
    Main handler function for creating a draft
    
    Args:
        args: Input arguments containing project settings
        
    Returns:
        Output containing draft_id and status
    """
    logger = getattr(args, 'logger', None)
    
    if logger:
        logger.info(f"Creating new draft with parameters: {args.input}")
    
    try:
        # Log the actual received parameters for debugging
        if logger:
            logger.info(f"Received parameters - width: {getattr(args.input, 'width', None)}, "
                       f"height: {getattr(args.input, 'height', None)}, "
                       f"fps: {getattr(args.input, 'fps', None)}, "
                       f"draft_name: {getattr(args.input, 'draft_name', None)}")
        
        # Validate input parameters
        is_valid, error_msg = validate_input_parameters(args.input)
        if not is_valid:
            if logger:
                logger.error(f"Input validation failed: {error_msg}")
            return Output(
                draft_id="",
                success=False,
                message=f"参数验证失败: {error_msg}"
            )
        
        # Generate unique draft ID
        draft_id = str(uuid.uuid4())
        
        if logger:
            logger.info(f"Generated draft ID: {draft_id}")
        
        # Create draft folder
        try:
            draft_folder = create_draft_folder(draft_id)
            if logger:
                logger.info(f"Created draft folder: {draft_folder}")
        except Exception as e:
            if logger:
                logger.error(f"Failed to create draft folder: {str(e)}")
            return Output(
                draft_id="",
                success=False,
                message=f"创建草稿文件夹失败: {str(e)}"
            )
        
        # Create initial draft configuration
        try:
            create_initial_draft_config(args.input, draft_id, draft_folder)
            if logger:
                logger.info(f"Created initial draft configuration")
        except Exception as e:
            if logger:
                logger.error(f"Failed to create draft config: {str(e)}")
            return Output(
                draft_id="",
                success=False,
                message=f"创建草稿配置失败: {str(e)}"
            )
        
        if logger:
            logger.info(f"Draft created successfully with ID: {draft_id}")
        
        return Output(
            draft_id=draft_id,
            success=True,
            message=f"草稿创建成功，ID: {draft_id}"
        )
        
    except Exception as e:
        error_msg = f"Unexpected error in create_draft handler: {str(e)}"
        if logger:
            logger.error(error_msg)
            logger.error(f"Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
        
        return Output(
            draft_id="",
            success=False,
            message=f"创建草稿时发生意外错误: {str(e)}"
        )