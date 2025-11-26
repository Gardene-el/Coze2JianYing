"""
生成音频信息工具处理器

创建包含所有可能参数的音频配置的 JSON 字符串表示。
这是 add_audios 的辅助工具 - 生成单个音频信息字符串，可以
收集到数组中并传递给 add_audios。

总参数数： 11 (3 必需 + 8 可选)
基于 pyJianYingDraft 库的 AudioSegment 和 AudioSegmentConfig。
"""

import json
from typing import NamedTuple, Optional, Dict, Any
from runtime import Args


# Input/Output 类型定义（每个 Coze 工具都需要）
class Input(NamedTuple):
    """make_audio_info 工具的输入参数"""
    # 必需字段
    audio_url: str                              # 音频 URL
    start: int                                  # 开始时间（毫秒）
    end: int                                    # 结束时间（毫秒）
    
    # Optional audio properties
    volume: Optional[float] = 1.0               # 音量级别（0.0-2.0，默认 1.0）
    fade_in: Optional[int] = 0                  # Fade in duration in milliseconds
    fade_out: Optional[int] = 0                 # Fade out duration in milliseconds
    
    # Optional audio effects
    effect_type: Optional[str] = None           # 音频特效类型 (e.g., "变声", "混响")
    effect_intensity: Optional[float] = 1.0     # 特效强度（0.0-1.0）
    
    # Optional speed control
    speed: Optional[float] = 1.0                # 播放速度（0.5-2.0，默认 1.0）
    change_pitch: Optional[bool] = False        # 速度变化时改变音高（默认 False）
    
    # Optional material range (trim audio)
    material_start: Optional[int] = None        # 素材开始时间（毫秒）
    material_end: Optional[int] = None          # 素材结束时间（毫秒）


class Output(NamedTuple):
    """make_audio_info 工具的输出"""
    audio_info_string: str    # 音频信息的 JSON 字符串表示
    success: bool             # Operation success status
    message: str              # Status message


def handler(args: Args[Input]) -> Dict[str, Any]:
    """
    创建音频信息字符串的主处理函数
    
    Args:
        args: 包含所有音频参数的输入参数
        
    Returns:
        Dict containing the 音频信息的 JSON 字符串表示
    """
    logger = getattr(args, 'logger', None)
    
    if logger:
        logger.info(f"Creating audio info string for: {args.input.audio_url}")
    
    try:
        # 验证必需参数
        if not args.input.audio_url:
            return Output(
                audio_info_string="",
                success=False,
                message="缺少必需的 audio_url 参数"
            )._asdict()
        
        if args.input.start is None:
            return Output(
                audio_info_string="",
                success=False,
                message="缺少必需的 start 参数"
            )._asdict()
        
        if args.input.end is None:
            return Output(
                audio_info_string="",
                success=False,
                message="缺少必需的 end 参数"
            )._asdict()
        
        # 验证时间范围
        if args.input.start < 0:
            return Output(
                audio_info_string="",
                success=False,
                message="start 时间不能为负数"
            )._asdict()
        
        if args.input.end <= args.input.start:
            return Output(
                audio_info_string="",
                success=False,
                message="end 时间必须大于 start 时间"
            )._asdict()
        
        # Validate 可选 parameters
        if args.input.volume is not None and (args.input.volume < 0.0 or args.input.volume > 2.0):
            return Output(
                audio_info_string="",
                success=False,
                message="volume 必须在 0.0 到 2.0 之间"
            )._asdict()
        
        if args.input.speed is not None and (args.input.speed < 0.5 or args.input.speed > 2.0):
            return Output(
                audio_info_string="",
                success=False,
                message="speed 必须在 0.5 到 2.0 之间"
            )._asdict()
        
        if args.input.fade_in is not None and args.input.fade_in < 0:
            return Output(
                audio_info_string="",
                success=False,
                message="fade_in 时间不能为负数"
            )._asdict()
        
        if args.input.fade_out is not None and args.input.fade_out < 0:
            return Output(
                audio_info_string="",
                success=False,
                message="fade_out 时间不能为负数"
            )._asdict()
        
        # 如果提供，验证素材范围
        if args.input.material_start is not None or args.input.material_end is not None:
            if args.input.material_start is None or args.input.material_end is None:
                return Output(
                    audio_info_string="",
                    success=False,
                    message="material_start 和 material_end 必须同时提供"
                )._asdict()
            
            if args.input.material_start < 0:
                return Output(
                    audio_info_string="",
                    success=False,
                    message="material_start 时间不能为负数"
                )._asdict()
            
            if args.input.material_end <= args.input.material_start:
                return Output(
                    audio_info_string="",
                    success=False,
                    message="material_end 时间必须大于 material_start 时间"
                )._asdict()
        
        # 使用所有参数构建音频信息字典
        audio_info = {
            "audio_url": args.input.audio_url,
            "start": args.input.start,
            "end": args.input.end
        }
        
        # 仅在非 None 或非默认值时添加可选参数
        # 这使输出保持清洁，仅包含指定的参数
        
        # 音频 properties (only add if not None and not default values)
        if args.input.volume is not None and args.input.volume != 1.0:
            audio_info["volume"] = args.input.volume
        if args.input.fade_in is not None and args.input.fade_in != 0:
            audio_info["fade_in"] = args.input.fade_in
        if args.input.fade_out is not None and args.input.fade_out != 0:
            audio_info["fade_out"] = args.input.fade_out
        
        # 音频 effects
        if args.input.effect_type is not None:
            audio_info["effect_type"] = args.input.effect_type
            if args.input.effect_intensity is not None and args.input.effect_intensity != 1.0:
                audio_info["effect_intensity"] = args.input.effect_intensity
        
        # 速度控制
        if args.input.speed is not None and args.input.speed != 1.0:
            audio_info["speed"] = args.input.speed
        if args.input.change_pitch:
            audio_info["change_pitch"] = args.input.change_pitch
        
        # Material range (trim)
        if args.input.material_start is not None and args.input.material_end is not None:
            audio_info["material_start"] = args.input.material_start
            audio_info["material_end"] = args.input.material_end
        
        # 转换为 JSON 字符串，不带额外空格以进行紧凑表示
        audio_info_string = json.dumps(audio_info, ensure_ascii=False, separators=(',', ':'))
        
        if logger:
            logger.info(f"Successfully created audio info string: {len(audio_info_string)} characters")
        
        return Output(
            audio_info_string=audio_info_string,
            success=True,
            message="音频信息字符串生成成功"
        )._asdict()
        
    except Exception as e:
        error_msg = f"生成音频信息字符串时发生错误: {str(e)}"
        if logger:
            logger.error(error_msg)
        
        return Output(
            audio_info_string="",
            success=False,
            message=error_msg
        )._asdict()
