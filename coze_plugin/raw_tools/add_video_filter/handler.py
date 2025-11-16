"""
add_video_filter 工具处理器

自动从 API 端点生成: /video/{segment_id}/add_filter
源文件: /home/runner/work/Coze2JianYing/Coze2JianYing/app/api/segment_routes.py
"""

import os
import json
import uuid
import time
from typing import NamedTuple, Dict, Any, Optional, List
from runtime import Args


# Input 类型定义
class Input(NamedTuple):
    """add_video_filter 工具的输入参数"""
    segment_id: str  # 片段ID
    filter_type: str  # 滤镜类型
    intensity: float = 100.0  # 滤镜强度 0-100


# Output 类型定义
class Output(NamedTuple):
    """add_video_filter 工具的输出参数"""
    success: bool = False  # 是否成功
    filter_id: str = ""  # 滤镜 UUID
    message: str = ""  # 响应消息


def ensure_coze2jianying_file() -> str:
    """
    确保 /tmp 目录下存在 coze2jianying.py 文件

    Returns:
        coze2jianying.py 文件的完整路径
    """
    file_path = "/tmp/coze2jianying.py"

    if not os.path.exists(file_path):
        # 创建初始文件内容
        initial_content = """# Coze2JianYing API 调用记录
# 此文件由 Coze 工具自动生成和更新
# 记录所有通过 Coze 工具调用的 API 操作

import asyncio
from app.schemas.segment_schemas import *

# API 调用记录将追加在下方
"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(initial_content)

    return file_path


def append_api_call_to_file(file_path: str, api_call_code: str):
    """
    将 API 调用代码追加到 coze2jianying.py 文件

    Args:
        file_path: coze2jianying.py 文件路径
        api_call_code: 要追加的 API 调用代码
    """
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write("\n" + api_call_code + "\n")


def _to_type_constructor(obj, type_name: str) -> str:
    """
    将 CustomNamespace/SimpleNamespace 对象转换为类型构造表达式字符串

    用于处理 Coze 的 CustomNamespace/SimpleNamespace 对象
    这些对象在 Coze 云端使用，在应用端执行时需要转换为对应类型的构造调用

    例如：
        CustomNamespace(start=0, duration=5000000)
        -> "TimeRange(start=0, duration=5000000)"

    Args:
        obj: CustomNamespace/SimpleNamespace 对象
        type_name: 目标类型名，如 "TimeRange", "ClipSettings"

    Returns:
        类型构造表达式字符串，如 "TimeRange(start=0, duration=5000000)"
    """
    if obj is None:
        return 'None'

    # 检查是否有 __dict__ 属性（CustomNamespace, SimpleNamespace 等）
    if hasattr(obj, '__dict__'):
        obj_dict = obj.__dict__
        # 构造类型构造调用的参数列表
        params = []
        for key, value in obj_dict.items():
            # 递归处理嵌套对象
            if hasattr(value, '__dict__'):
                # 嵌套对象：尝试推断其类型名（使用首字母大写的 key）
                nested_type_name = key.capitalize() if key else 'Object'
                # 如果 key 本身就是类型相关的，使用更智能的命名
                if 'settings' in key.lower():
                    nested_type_name = 'ClipSettings'
                elif 'timerange' in key.lower():
                    nested_type_name = 'TimeRange'
                elif 'style' in key.lower():
                    nested_type_name = 'TextStyle'
                elif 'position' in key.lower():
                    nested_type_name = 'Position'
                value_repr = _to_type_constructor(value, nested_type_name)
            elif isinstance(value, str):
                # 字符串值：加引号
                value_repr = f'"{value}"'
            else:
                # 其他类型：直接使用 repr
                value_repr = repr(value)
            params.append(f'{key}={value_repr}')

        # 构造类型构造表达式：TypeName(param1=value1, param2=value2)
        return f'{type_name}(' + ', '.join(params) + ')'

    # 如果不是复杂对象，返回其 repr
    if isinstance(obj, str):
        return f'"{obj}"'
    else:
        return repr(obj)


def handler(args: Args[Input]) -> Output:
    """
    add_video_filter 的主处理函数

    Args:
        args: Input arguments

    Returns:
        Output NamedTuple containing response data
    """
    logger = getattr(args, 'logger', None)

    if logger:
        logger.info(f"调用 add_video_filter，参数: {args.input}")

    try:
        # 生成唯一 UUID
        generated_uuid = str(uuid.uuid4()).replace("-", "_")

        if logger:
            logger.info(f"生成 UUID: {generated_uuid}")

        # 生成 API 调用代码
        api_call = f"""
# API 调用: add_video_filter
# 时间: {time.strftime('%Y-%m-%d %H:%M:%S')}

# 构造 request 对象
req_params_{generated_uuid} = {{}}
req_params_{generated_uuid}['filter_type'] = "{args.input.filter_type}"
if {args.input.intensity} is not None:
    req_params_{generated_uuid}['intensity'] = {args.input.intensity}
req_{generated_uuid} = AddFilterRequest(**req_params_{generated_uuid})

resp_{generated_uuid} = await add_video_filter(segment_{args.input.segment_id}, req_{generated_uuid})
"""

        # 写入 API 调用到文件
        coze_file = ensure_coze2jianying_file()
        append_api_call_to_file(coze_file, api_call)


        if logger:
            logger.info(f"add_video_filter 调用成功")

        return Output(success=True, filter_id="", message="操作成功")

    except Exception as e:
        error_msg = f"调用 add_video_filter 时发生错误: {str(e)}"
        if logger:
            logger.error(error_msg)
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")

        return Output(success=False, message=error_msg)

