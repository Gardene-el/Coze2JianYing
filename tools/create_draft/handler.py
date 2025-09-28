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
    project_name: str = "Coze剪映项目"
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
    # Validate dimensions
    if input_data.width <= 0 or input_data.height <= 0:
        return False, f"Invalid dimensions: {input_data.width}x{input_data.height}"
    
    # Validate fps
    if input_data.fps <= 0 or input_data.fps > 120:
        return False, f"Invalid fps: {input_data.fps}"
    
    # Validate video quality
    valid_video_qualities = [VideoQuality.SD_480P, VideoQuality.HD_720P, 
                           VideoQuality.FHD_1080P, VideoQuality.QHD_1440P, VideoQuality.UHD_4K]
    if input_data.video_quality not in valid_video_qualities:
        return False, f"Invalid video quality: {input_data.video_quality}"
    
    # Validate audio quality
    valid_audio_qualities = [AudioQuality.LOW_128K, AudioQuality.MEDIUM_192K, 
                           AudioQuality.HIGH_320K, AudioQuality.LOSSLESS]
    if input_data.audio_quality not in valid_audio_qualities:
        return False, f"Invalid audio quality: {input_data.audio_quality}"
    
    # Validate background color (should be hex color)
    if not input_data.background_color.startswith('#') or len(input_data.background_color) != 7:
        return False, f"Invalid background color: {input_data.background_color}"
    
    return True, ""


def create_draft_folder(draft_id: str) -> str:
    """
    Create draft folder in /tmp directory
    
    Args:
        draft_id: UUID string for the draft
        
    Returns:
        Path to created draft folder
        
    Raises:
        Exception: If folder creation fails
    """
    draft_folder = os.path.join("/tmp", draft_id)
    
    try:
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
    
    # Create initial draft configuration
    draft_config = {
        "draft_id": draft_id,
        "project": {
            "name": input_data.project_name,
            "width": input_data.width,
            "height": input_data.height,
            "fps": input_data.fps,
            "video_quality": input_data.video_quality,
            "audio_quality": input_data.audio_quality,
            "background_color": input_data.background_color
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
        
        return Output(
            draft_id="",
            success=False,
            message=f"创建草稿时发生意外错误: {str(e)}"
        )