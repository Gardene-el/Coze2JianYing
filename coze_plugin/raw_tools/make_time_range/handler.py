"""
make_time_range 工具处理器

为 TimeRange 类生成对象
时间范围模型（微秒）

此工具接收 TimeRange 的所有参数（可选，使用原始默认值），
并返回一个 TimeRange 对象。
"""

import json
from typing import NamedTuple, Optional, Dict, Any, List
from runtime import Args


# TimeRange 类型定义
class TimeRange(NamedTuple):
    """时间范围模型（微秒）"""
    start: int  # 开始时间（微秒）
    duration: int  # 持续时长（微秒）


# Input 类型定义
class Input(NamedTuple):
    """make_time_range 工具的输入参数（可选，有默认值的参数使用原始默认值）"""
    start: Optional[int] = None  # 开始时间（微秒）
    duration: Optional[int] = None  # 持续时长（微秒）


# Output 类型定义
class Output(NamedTuple):
    """make_time_range 工具的输出"""
    result: Optional[TimeRange]  # TimeRange 对象（错误时为 None）
    success: bool           # 操作成功状态
    message: str            # 状态消息


def handler(args: Args[Input]) -> Output:
    """
    创建 TimeRange 对象的主处理函数
    
    Args:
        args: 包含所有 TimeRange 参数的输入参数（使用原始默认值）
        
    Returns:
        包含 TimeRange 对象的 Output
    """
    logger = getattr(args, 'logger', None)
    
    if logger:
        logger.info(f"Creating TimeRange object")
    
    try:
        # 准备参数，使用提供的值或默认值
        if args.input.start is None:
            raise ValueError('start 是必需参数，必须提供')
        start = args.input.start
        if args.input.duration is None:
            raise ValueError('duration 是必需参数，必须提供')
        duration = args.input.duration
        
        # 创建 TimeRange 对象
        result = TimeRange(start=start, duration=duration)
        
        if logger:
            logger.info(f"Successfully created TimeRange object")
        
        return Output(
            result=result,
            success=True,
            message="TimeRange 对象创建成功"
        )
        
    except ValueError as e:
        # 参数验证错误
        error_msg = f"参数错误: {str(e)}"
        if logger:
            logger.error(error_msg)
        
        # 返回 None 作为错误情况（Output 中 result 改为 Optional）
        return Output(
            result=None,
            success=False,
            message=error_msg
        )
    except Exception as e:
        error_msg = f"创建 TimeRange 对象时发生错误: {str(e)}"
        if logger:
            logger.error(error_msg)
        
        return Output(
            result=None,
            success=False,
            message=error_msg
        )

