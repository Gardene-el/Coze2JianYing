"""
Make Audio Info Tool Handler

Creates a JSON string representation of audio configuration with all possible parameters.
This is a helper tool for add_audios - generates a single audio info string that can be
collected into an array and passed to add_audios.

Total parameters: 10 (3 required + 7 optional)
Based on pyJianYingDraft library's AudioSegment and AudioSegmentConfig.
"""

import json
from typing import NamedTuple, Optional
from runtime import Args


# Input/Output type definitions (required for each Coze tool)
class Input(NamedTuple):
    """Input parameters for make_audio_info tool"""
    # Required fields
    audio_url: str                              # Audio URL
    start: int                                  # Start time in milliseconds
    end: int                                    # End time in milliseconds
    
    # Optional audio properties
    volume: Optional[float] = 1.0               # Volume level (0.0-2.0, default 1.0)
    fade_in: Optional[int] = 0                  # Fade in duration in milliseconds
    fade_out: Optional[int] = 0                 # Fade out duration in milliseconds
    
    # Optional audio effects
    effect_type: Optional[str] = None           # Audio effect type (e.g., "变声", "混响")
    effect_intensity: Optional[float] = 1.0     # Effect intensity (0.0-1.0)
    
    # Optional speed control
    speed: Optional[float] = 1.0                # Playback speed (0.5-2.0, default 1.0)
    
    # Optional material range (trim audio)
    material_start: Optional[int] = None        # Material start time in milliseconds
    material_end: Optional[int] = None          # Material end time in milliseconds


class Output(NamedTuple):
    """Output for make_audio_info tool"""
    audio_info_string: str                      # JSON string representation of audio info
    success: bool = True                        # Operation success status
    message: str = "音频信息字符串生成成功"       # Status message


def handler(args: Args[Input]) -> Output:
    """
    Main handler function for creating audio info string
    
    Args:
        args: Input arguments containing all audio parameters
        
    Returns:
        Output containing the JSON string representation of audio info
    """
    logger = getattr(args, 'logger', None)
    
    if logger:
        logger.info(f"Creating audio info string for: {args.input.audio_url}")
    
    try:
        # Validate required parameters
        if not args.input.audio_url:
            return Output(
                audio_info_string="",
                success=False,
                message="缺少必需的 audio_url 参数"
            )
        
        if args.input.start is None:
            return Output(
                audio_info_string="",
                success=False,
                message="缺少必需的 start 参数"
            )
        
        if args.input.end is None:
            return Output(
                audio_info_string="",
                success=False,
                message="缺少必需的 end 参数"
            )
        
        # Validate time range
        if args.input.start < 0:
            return Output(
                audio_info_string="",
                success=False,
                message="start 时间不能为负数"
            )
        
        if args.input.end <= args.input.start:
            return Output(
                audio_info_string="",
                success=False,
                message="end 时间必须大于 start 时间"
            )
        
        # Validate optional parameters
        if args.input.volume is not None and (args.input.volume < 0.0 or args.input.volume > 2.0):
            return Output(
                audio_info_string="",
                success=False,
                message="volume 必须在 0.0 到 2.0 之间"
            )
        
        if args.input.speed is not None and (args.input.speed < 0.5 or args.input.speed > 2.0):
            return Output(
                audio_info_string="",
                success=False,
                message="speed 必须在 0.5 到 2.0 之间"
            )
        
        if args.input.fade_in is not None and args.input.fade_in < 0:
            return Output(
                audio_info_string="",
                success=False,
                message="fade_in 时间不能为负数"
            )
        
        if args.input.fade_out is not None and args.input.fade_out < 0:
            return Output(
                audio_info_string="",
                success=False,
                message="fade_out 时间不能为负数"
            )
        
        # Validate material range if provided
        if args.input.material_start is not None or args.input.material_end is not None:
            if args.input.material_start is None or args.input.material_end is None:
                return Output(
                    audio_info_string="",
                    success=False,
                    message="material_start 和 material_end 必须同时提供"
                )
            
            if args.input.material_start < 0:
                return Output(
                    audio_info_string="",
                    success=False,
                    message="material_start 时间不能为负数"
                )
            
            if args.input.material_end <= args.input.material_start:
                return Output(
                    audio_info_string="",
                    success=False,
                    message="material_end 时间必须大于 material_start 时间"
                )
        
        # Build audio info dictionary with all parameters
        audio_info = {
            "audio_url": args.input.audio_url,
            "start": args.input.start,
            "end": args.input.end
        }
        
        # Add optional parameters only if they are not None or not default values
        # This keeps the output clean and only includes specified parameters
        
        # Audio properties (only add if not default values)
        if args.input.volume != 1.0:
            audio_info["volume"] = args.input.volume
        if args.input.fade_in != 0:
            audio_info["fade_in"] = args.input.fade_in
        if args.input.fade_out != 0:
            audio_info["fade_out"] = args.input.fade_out
        
        # Audio effects
        if args.input.effect_type is not None:
            audio_info["effect_type"] = args.input.effect_type
            if args.input.effect_intensity != 1.0:
                audio_info["effect_intensity"] = args.input.effect_intensity
        
        # Speed control
        if args.input.speed != 1.0:
            audio_info["speed"] = args.input.speed
        
        # Material range (trim)
        if args.input.material_start is not None and args.input.material_end is not None:
            audio_info["material_start"] = args.input.material_start
            audio_info["material_end"] = args.input.material_end
        
        # Convert to JSON string without extra whitespace for compact representation
        audio_info_string = json.dumps(audio_info, ensure_ascii=False, separators=(',', ':'))
        
        if logger:
            logger.info(f"Successfully created audio info string: {len(audio_info_string)} characters")
        
        return Output(
            audio_info_string=audio_info_string,
            success=True,
            message="音频信息字符串生成成功"
        )
        
    except Exception as e:
        error_msg = f"生成音频信息字符串时发生错误: {str(e)}"
        if logger:
            logger.error(error_msg)
        
        return Output(
            audio_info_string="",
            success=False,
            message=error_msg
        )
