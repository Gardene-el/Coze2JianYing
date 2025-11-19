"""
make_crop_settings 工具处理器

为 CropSettings 类生成对象
裁剪设置（镜像 pyJianYingDraft.CropSettings）
对应 pyJianYingDraft 的 CropSettings 类，用于定义裁剪区域的四个角点坐标

此工具接收 CropSettings 的所有参数（可选，使用原始默认值），
并返回一个 CropSettings 对象。
"""

import json
from typing import NamedTuple, Optional, Dict, Any, List
from runtime import Args


# CropSettings 类型定义
class CropSettings(NamedTuple):
    """裁剪设置（镜像 pyJianYingDraft.CropSettings）
对应 pyJianYingDraft 的 CropSettings 类，用于定义裁剪区域的四个角点坐标"""
    upper_left_x: float  # 左上角 X 坐标 (0.0-1.0)
    upper_left_y: float  # 左上角 Y 坐标 (0.0-1.0)
    upper_right_x: float  # 右上角 X 坐标 (0.0-1.0)
    upper_right_y: float  # 右上角 Y 坐标 (0.0-1.0)
    lower_left_x: float  # 左下角 X 坐标 (0.0-1.0)
    lower_left_y: float  # 左下角 Y 坐标 (0.0-1.0)
    lower_right_x: float  # 右下角 X 坐标 (0.0-1.0)
    lower_right_y: float  # 右下角 Y 坐标 (0.0-1.0)


# Input 类型定义
class Input(NamedTuple):
    """make_crop_settings 工具的输入参数（可选，有默认值的参数使用原始默认值）"""
    upper_left_x: Optional[float] = 0.0  # 左上角 X 坐标 (0.0-1.0)
    upper_left_y: Optional[float] = 0.0  # 左上角 Y 坐标 (0.0-1.0)
    upper_right_x: Optional[float] = 1.0  # 右上角 X 坐标 (0.0-1.0)
    upper_right_y: Optional[float] = 0.0  # 右上角 Y 坐标 (0.0-1.0)
    lower_left_x: Optional[float] = 0.0  # 左下角 X 坐标 (0.0-1.0)
    lower_left_y: Optional[float] = 1.0  # 左下角 Y 坐标 (0.0-1.0)
    lower_right_x: Optional[float] = 1.0  # 右下角 X 坐标 (0.0-1.0)
    lower_right_y: Optional[float] = 1.0  # 右下角 Y 坐标 (0.0-1.0)


# Output 类型定义
class Output(NamedTuple):
    """make_crop_settings 工具的输出"""
    result: Optional[CropSettings]  # CropSettings 对象（错误时为 None）
    success: bool           # 操作成功状态
    message: str            # 状态消息


def handler(args: Args[Input]) -> Output:
    """
    创建 CropSettings 对象的主处理函数
    
    Args:
        args: 包含所有 CropSettings 参数的输入参数（使用原始默认值）
        
    Returns:
        包含 CropSettings 对象的 Output
    """
    logger = getattr(args, 'logger', None)
    
    if logger:
        logger.info(f"Creating CropSettings object")
    
    try:
        # 准备参数，使用提供的值或默认值
        upper_left_x = args.input.upper_left_x if args.input.upper_left_x is not None else 0.0
        upper_left_y = args.input.upper_left_y if args.input.upper_left_y is not None else 0.0
        upper_right_x = args.input.upper_right_x if args.input.upper_right_x is not None else 1.0
        upper_right_y = args.input.upper_right_y if args.input.upper_right_y is not None else 0.0
        lower_left_x = args.input.lower_left_x if args.input.lower_left_x is not None else 0.0
        lower_left_y = args.input.lower_left_y if args.input.lower_left_y is not None else 1.0
        lower_right_x = args.input.lower_right_x if args.input.lower_right_x is not None else 1.0
        lower_right_y = args.input.lower_right_y if args.input.lower_right_y is not None else 1.0
        
        # 创建 CropSettings 对象
        result = CropSettings(upper_left_x=upper_left_x, upper_left_y=upper_left_y, upper_right_x=upper_right_x, upper_right_y=upper_right_y, lower_left_x=lower_left_x, lower_left_y=lower_left_y, lower_right_x=lower_right_x, lower_right_y=lower_right_y)
        
        if logger:
            logger.info(f"Successfully created CropSettings object")
        
        return Output(
            result=result,
            success=True,
            message="CropSettings 对象创建成功"
        )
        
    except Exception as e:
        error_msg = f"创建 CropSettings 对象时发生错误: {str(e)}"
        if logger:
            logger.error(error_msg)
        
        return Output(
            result=None,
            success=False,
            message=error_msg
        )

