"""
make_crop_settings 工具处理器

为 CropSettings 类生成 Object 对象
裁剪设置（镜像 pyJianYingDraft.CropSettings）
对应 pyJianYingDraft 的 CropSettings 类，用于定义裁剪区域的四个角点坐标

此工具接收 CropSettings 的所有参数（全部为可选），
并返回一个 Object（字典）表示。
"""

import json
from typing import NamedTuple, Optional, Dict, Any, List
from runtime import Args


# Input 类型定义
class Input(NamedTuple):
    """make_crop_settings 工具的输入参数（全部可选）"""
    upper_left_x: Optional[float] = None  # 左上角 X 坐标 (0.0-1.0)
    upper_left_y: Optional[float] = None  # 左上角 Y 坐标 (0.0-1.0)
    upper_right_x: Optional[float] = None  # 右上角 X 坐标 (0.0-1.0)
    upper_right_y: Optional[float] = None  # 右上角 Y 坐标 (0.0-1.0)
    lower_left_x: Optional[float] = None  # 左下角 X 坐标 (0.0-1.0)
    lower_left_y: Optional[float] = None  # 左下角 Y 坐标 (0.0-1.0)
    lower_right_x: Optional[float] = None  # 右下角 X 坐标 (0.0-1.0)
    lower_right_y: Optional[float] = None  # 右下角 Y 坐标 (0.0-1.0)


# Output 类型定义
class Output(NamedTuple):
    """make_crop_settings 工具的输出"""
    result: Dict[str, Any]  # CropSettings 对象的字典表示
    success: bool           # 操作成功状态
    message: str            # 状态消息


def handler(args: Args[Input]) -> Output:
    """
    创建 CropSettings 对象的主处理函数
    
    Args:
        args: 包含所有 CropSettings 参数的输入参数（全部可选）
        
    Returns:
        包含 CropSettings 对象字典表示的 Output
    """
    logger = getattr(args, 'logger', None)
    
    if logger:
        logger.info(f"Creating CropSettings object")
    
    try:
        # 构建结果字典，仅包含提供的非 None 参数
        result = {}
        
        if args.input.upper_left_x is not None:
            result['upper_left_x'] = args.input.upper_left_x
        if args.input.upper_left_y is not None:
            result['upper_left_y'] = args.input.upper_left_y
        if args.input.upper_right_x is not None:
            result['upper_right_x'] = args.input.upper_right_x
        if args.input.upper_right_y is not None:
            result['upper_right_y'] = args.input.upper_right_y
        if args.input.lower_left_x is not None:
            result['lower_left_x'] = args.input.lower_left_x
        if args.input.lower_left_y is not None:
            result['lower_left_y'] = args.input.lower_left_y
        if args.input.lower_right_x is not None:
            result['lower_right_x'] = args.input.lower_right_x
        if args.input.lower_right_y is not None:
            result['lower_right_y'] = args.input.lower_right_y
        
        if logger:
            logger.info(f"Successfully created CropSettings object with {len(result)} fields")
        
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
            result={},
            success=False,
            message=error_msg
        )

