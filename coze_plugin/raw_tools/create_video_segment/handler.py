"""
create_video_segment 工具处理器

自动从 API 端点生成: /video/create
源文件: /home/runner/work/Coze2JianYing/Coze2JianYing/app/api/segment_routes.py
"""

import os
import json
import uuid
import time
from typing import NamedTuple, Dict, Any, Optional, List
from runtime import Args


# ========== 自定义类型定义 ==========
# 以下类型定义从 segment_schemas.py 复制而来
# Coze 平台不支持跨文件 import，因此需要在每个工具中重复定义

class ClipSettings(NamedTuple):
    """ClipSettings"""
    alpha: float  # 透明度 (0.0-1.0)
    rotation: float  # 旋转角度（度）
    scale_x: float  # X 轴缩放比例
    scale_y: float  # Y 轴缩放比例
    transform_x: float  # X 轴位置偏移
    transform_y: float  # Y 轴位置偏移

class CropSettings(NamedTuple):
    """CropSettings"""
    upper_left_x: float  # 左上角 X 坐标 (0.0-1.0)
    upper_left_y: float  # 左上角 Y 坐标 (0.0-1.0)
    upper_right_x: float  # 右上角 X 坐标 (0.0-1.0)
    upper_right_y: float  # 右上角 Y 坐标 (0.0-1.0)
    lower_left_x: float  # 左下角 X 坐标 (0.0-1.0)
    lower_left_y: float  # 左下角 Y 坐标 (0.0-1.0)
    lower_right_x: float  # 右下角 X 坐标 (0.0-1.0)
    lower_right_y: float  # 右下角 Y 坐标 (0.0-1.0)

class TimeRange(NamedTuple):
    """TimeRange"""
    start: int  # 开始时间（微秒）
    duration: int  # 持续时长（微秒）


# Input 类型定义
class Input(NamedTuple):
    """create_video_segment 工具的输入参数"""
    material_url: str  # 视频素材 URL
    target_timerange: TimeRange  # 在轨道上的时间范围
    source_timerange: Optional[TimeRange] = None  # 素材裁剪范围
    speed: float = 1.0  # 播放速度
    volume: float = 1.0  # 音量 0-2
    change_pitch: bool = False  # 是否跟随变速改变音调
    clip_settings: Optional[ClipSettings] = None  # 图像调节设置
    crop_settings: Optional[CropSettings] = None  # 裁剪设置


# Output 类型定义
class Output(NamedTuple):
    """create_video_segment 工具的输出参数"""
    segment_id: str = ""  # Segment UUID，错误时为空字符串
    success: bool = False  # 是否成功
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
        type_name: 目标类型名，如 "TimeRange", "ClipSettings", "CropSettings", "TextStyle"

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
                # 根据最新 schema 重构：ClipSettings, CropSettings, TextStyle, TimeRange
                if 'clip_settings' in key.lower() or key.lower() == 'clipsettings':
                    nested_type_name = 'ClipSettings'
                elif 'crop_settings' in key.lower() or key.lower() == 'cropsettings':
                    nested_type_name = 'CropSettings'
                elif 'timerange' in key.lower():
                    nested_type_name = 'TimeRange'
                elif 'text_style' in key.lower() or key.lower() == 'textstyle':
                    nested_type_name = 'TextStyle'
                # Note: Position class was removed in schema refactoring
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
    create_video_segment 的主处理函数

    Args:
        args: Input arguments

    Returns:
        Output NamedTuple containing response data
    """
    logger = getattr(args, 'logger', None)

    if logger:
        logger.info(f"调用 create_video_segment，参数: {args.input}")

    try:
        # 生成唯一 UUID
        generated_uuid = str(uuid.uuid4()).replace("-", "_")

        if logger:
            logger.info(f"生成 UUID: {generated_uuid}")

        # 生成 API 调用代码
        api_call = f"""
# API 调用: create_video_segment
# 时间: {time.strftime('%Y-%m-%d %H:%M:%S')}

# 构造 request 对象
req_params_{generated_uuid} = {{}}
req_params_{generated_uuid}['material_url'] = "{args.input.material_url}"
req_params_{generated_uuid}['target_timerange'] = {_to_type_constructor(args.input.target_timerange, 'TimeRange')}
if {args.input.source_timerange} is not None:
    req_params_{generated_uuid}['source_timerange'] = {_to_type_constructor(args.input.source_timerange, 'TimeRange')}
if {args.input.speed} is not None:
    req_params_{generated_uuid}['speed'] = {args.input.speed}
if {args.input.volume} is not None:
    req_params_{generated_uuid}['volume'] = {args.input.volume}
if {args.input.change_pitch} is not None:
    req_params_{generated_uuid}['change_pitch'] = {args.input.change_pitch}
if {args.input.clip_settings} is not None:
    req_params_{generated_uuid}['clip_settings'] = {_to_type_constructor(args.input.clip_settings, 'ClipSettings')}
if {args.input.crop_settings} is not None:
    req_params_{generated_uuid}['crop_settings'] = {_to_type_constructor(args.input.crop_settings, 'CropSettings')}
req_{generated_uuid} = CreateVideoSegmentRequest(**req_params_{generated_uuid})

resp_{generated_uuid} = await create_video_segment(req_{generated_uuid})

segment_{generated_uuid} = resp_{generated_uuid}.segment_id
"""

        # 写入 API 调用到文件
        coze_file = ensure_coze2jianying_file()
        append_api_call_to_file(coze_file, api_call)


        if logger:
            logger.info(f"create_video_segment 调用成功")

        return Output(segment_id=f"{generated_uuid}", success=True, message="操作成功")

    except Exception as e:
        error_msg = f"调用 create_video_segment 时发生错误: {str(e)}"
        if logger:
            logger.error(error_msg)
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")

        return Output(success=False, message=error_msg)

