"""
make_time_range 工具处理器

为 TimeRange 类生成 Object 对象
时间范围模型（微秒）

此工具接收 TimeRange 的所有参数（全部为可选），
并返回一个 Object（字典）表示。
"""

import json
from typing import NamedTuple, Optional, Dict, Any, List
from runtime import Args


# Input 类型定义
class Input(NamedTuple):
    """make_time_range 工具的输入参数（全部可选）"""
    start: Optional[int] = None  # 开始时间（微秒）
    duration: Optional[int] = None  # 持续时长（微秒）


# Output 类型定义
class Output(NamedTuple):
    """make_time_range 工具的输出"""
    result: Dict[str, Any]  # TimeRange 对象的字典表示
    success: bool           # 操作成功状态
    message: str            # 状态消息


def handler(args: Args[Input]) -> Output:
    """
    创建 TimeRange 对象的主处理函数
    
    Args:
        args: 包含所有 TimeRange 参数的输入参数（全部可选）
        
    Returns:
        包含 TimeRange 对象字典表示的 Output
    """
    logger = getattr(args, 'logger', None)
    
    if logger:
        logger.info(f"Creating TimeRange object")
    
    try:
        # 构建结果字典，仅包含提供的非 None 参数
        result = {}
        
        if args.input.start is not None:
            result['start'] = args.input.start
        if args.input.duration is not None:
            result['duration'] = args.input.duration
        
        if logger:
            logger.info(f"Successfully created TimeRange object with {len(result)} fields")
        
        return Output(
            result=result,
            success=True,
            message="TimeRange 对象创建成功"
        )
        
    except Exception as e:
        error_msg = f"创建 TimeRange 对象时发生错误: {str(e)}"
        if logger:
            logger.error(error_msg)
        
        return Output(
            result={},
            success=False,
            message=error_msg
        )

