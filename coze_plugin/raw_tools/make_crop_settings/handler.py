"""
make_crop_settings 工具处理器

为 CropSettings 类生成对象
裁剪设置（镜像 pyJianYingDraft.CropSettings）
对应 pyJianYingDraft 的 CropSettings 类，用于定义裁剪区域的四个角点坐标

此工具接收 CropSettings 的所有参数（可选，使用原始默认值），
并返回一个包含 CropSettings 数据的字典。

注意：handler 直接返回 Dict[str, Any]，而不是 NamedTuple，
以确保在 Coze 平台中正确的 JSON 对象序列化。
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


def handler(args: Args[Input]) -> Dict[str, Any]:
    """
    创建 CropSettings 对象的主处理函数
    
    Args:
        args: 包含所有 CropSettings 参数的输入参数（使用原始默认值）
        
    Returns:
        Dict[str, Any]: 包含 result、success、message 字段的字典
            - result: CropSettings 对象的字典表示（参数不完整时为 None）
            - success: 操作是否成功
            - message: 状态消息
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
        obj = CropSettings(upper_left_x=upper_left_x, upper_left_y=upper_left_y, upper_right_x=upper_right_x, upper_right_y=upper_right_y, lower_left_x=lower_left_x, lower_left_y=lower_left_y, lower_right_x=lower_right_x, lower_right_y=lower_right_y)
        
        # 转换为字典以确保正确的 JSON 序列化
        result_dict = obj._asdict()
        
        if logger:
            logger.info(f"Successfully created CropSettings object")
        
        return {
            'result': result_dict,
            'success': True,
            'message': 'CropSettings 对象创建成功'
        }
        
    except Exception as e:
        error_msg = f"创建 CropSettings 对象时发生错误: {str(e)}"
        if logger:
            logger.error(error_msg)
        
        return {
            'result': None,
            'success': False,
            'message': error_msg
        }

