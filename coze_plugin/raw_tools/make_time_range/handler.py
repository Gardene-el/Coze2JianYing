"""
make_time_range 工具处理器

为 TimeRange 类生成对象
时间范围模型（微秒）

此工具接收 TimeRange 的所有参数（可选，使用原始默认值），
并返回一个包含 TimeRange 数据的字典。

注意：handler 直接返回 Dict[str, Any]，而不是 NamedTuple，
以确保在 Coze 平台中正确的 JSON 对象序列化。
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


def handler(args: Args[Input]) -> Dict[str, Any]:
    """
    创建 TimeRange 对象的主处理函数
    
    Args:
        args: 包含所有 TimeRange 参数的输入参数（使用原始默认值）
        
    Returns:
        Dict[str, Any]: 包含 result、success、message 字段的字典
            - result: TimeRange 对象的字典表示（参数不完整时为 None）
            - success: 操作是否成功
            - message: 状态消息
    """
    logger = getattr(args, 'logger', None)
    
    if logger:
        logger.info(f"Creating TimeRange object")
    
    try:
        # 准备参数，使用提供的值或默认值
        if args.input.start is None:
            # start 是必需参数但未提供，返回 None
            if logger:
                logger.warning(f'start 未提供，返回 None')
            return {
                'result': None,
                'success': True,
                'message': 'TimeRange 对象创建成功（参数不完整）'
            }
        start = args.input.start
        if args.input.duration is None:
            # duration 是必需参数但未提供，返回 None
            if logger:
                logger.warning(f'duration 未提供，返回 None')
            return {
                'result': None,
                'success': True,
                'message': 'TimeRange 对象创建成功（参数不完整）'
            }
        duration = args.input.duration
        
        # 创建 TimeRange 对象
        obj = TimeRange(start=start, duration=duration)
        
        # 转换为字典以确保正确的 JSON 序列化
        result_dict = obj._asdict()
        
        if logger:
            logger.info(f"Successfully created TimeRange object")
        
        return {
            'result': result_dict,
            'success': True,
            'message': 'TimeRange 对象创建成功'
        }
        
    except Exception as e:
        error_msg = f"创建 TimeRange 对象时发生错误: {str(e)}"
        if logger:
            logger.error(error_msg)
        
        return {
            'result': None,
            'success': False,
            'message': error_msg
        }

