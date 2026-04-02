"""
add_captions 工具处理器

自动从 API 端点生成: 
源文件: D:/Codespace/coze-jianying/Coze2JianYing/src/backend/api/easy.py
"""

import os
import json
import uuid
import time
from typing import NamedTuple, Dict, Any, Optional, List
from runtime import Args


# ========== 自定义类型定义 ==========
# 以下类型定义从 general_schemas.py 复制而来
# Coze 平台不支持跨文件 import，因此需要在每个工具中重复定义

class ShadowInfo(NamedTuple):
    """ShadowInfo"""
    shadow_alpha: float  # 阴影不透明度
    shadow_color: str  # 阴影颜色（十六进制）
    shadow_diffuse: float  # 阴影扩散程度
    shadow_distance: float  # 阴影距离
    shadow_angle: float  # 阴影角度


# Input 类型定义
class Input(NamedTuple):
    """add_captions 工具的输入参数"""
    draft_id: str  # 草稿ID
    captions: str  # 字幕信息列表，JSON字符串
    text_color: str = "#ffffff"  # 文本颜色（十六进制）
    border_color: Optional[str] = None  # 边框颜色（十六进制）
    alignment: int = 1  # 文本对齐方式
    alpha: float = 1.0  # 文本透明度
    font: Optional[str] = None  # 字体名称
    font_size: int = 15  # 字体大小
    letter_spacing: Optional[float] = None  # 字间距
    line_spacing: Optional[float] = None  # 行间距
    scale_x: float = 1.0  # 水平缩放
    scale_y: float = 1.0  # 垂直缩放
    transform_x: float = 0.0  # 水平位移
    transform_y: float = 0.0  # 垂直位移
    style_text: bool = False  # 是否使用样式文本
    underline: bool = False  # 文字下划线开关
    italic: bool = False  # 文本斜体开关
    bold: bool = False  # 文本加粗开关
    has_shadow: bool = False  # 是否启用文本阴影
    shadow_info: Optional[ShadowInfo] = None  # 文本阴影参数


# Output 类型定义
class Output(NamedTuple):
    """add_captions 工具的输出参数"""
    segment_ids: List[str] = []  # 字幕片段ID列表
    api_call: str = ""  # 生成的 API 调用代码


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
from src.backend.schemas import *
from src.backend.core.common_types import *

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



def _is_meaningful_object(obj) -> bool:
    """
    检查对象是否包含有意义的数据

    用于区分空的 CustomNamespace() 对象和包含有效数据的对象
    避免将空对象视为有效值，导致 Pydantic 验证失败

    Args:
        obj: 任意对象

    Returns:
        True 如果对象包含有意义的数据，False 如果对象为 None 或为空
    """
    # None 值不是有意义的对象
    if obj is None:
        return False

    # 检查是否有 __dict__ 属性（CustomNamespace, SimpleNamespace 等）
    if hasattr(obj, '__dict__'):
        obj_dict = obj.__dict__
        # 空字典意味着空对象
        if not obj_dict:
            return False
        # 检查是否所有值都是 None（也视为空对象）
        if all(v is None for v in obj_dict.values()):
            return False
        # 至少有一个非 None 值，视为有意义的对象
        return True

    # 对于基本类型（字符串、数字、布尔值等），非 None 即为有意义
    return True


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


def handler(args: Args[Input]) -> Dict[str, Any]:
    """
    add_captions 的主处理函数

    Args:
        args: Input arguments

    Returns:
        Dict containing response data (converted from Output NamedTuple for Coze compatibility)
    """
    logger = getattr(args, 'logger', None)

    if logger:
        logger.info(f"调用 add_captions，参数: {args.input}")

    try:
        # 生成唯一 UUID
        generated_uuid = str(uuid.uuid4()).replace("-", "_")

        if logger:
            logger.info(f"生成 UUID: {generated_uuid}")

        # 生成 API 调用代码
        api_call = f"""
# API 调用: add_captions
# 时间: {time.strftime('%Y-%m-%d %H:%M:%S')}

# 构造 request 对象
req_params_{generated_uuid} = {{}}
req_params_{generated_uuid}['captions'] = "{args.input.captions}"
if {args.input.text_color} is not None:
    req_params_{generated_uuid}['text_color'] = "{args.input.text_color}"
if {args.input.border_color} is not None:
    req_params_{generated_uuid}['border_color'] = "{args.input.border_color}"
if {args.input.alignment} is not None:
    req_params_{generated_uuid}['alignment'] = {args.input.alignment}
if {args.input.alpha} is not None:
    req_params_{generated_uuid}['alpha'] = {args.input.alpha}
if {args.input.font} is not None:
    req_params_{generated_uuid}['font'] = "{args.input.font}"
if {args.input.font_size} is not None:
    req_params_{generated_uuid}['font_size'] = {args.input.font_size}
if {args.input.letter_spacing} is not None:
    req_params_{generated_uuid}['letter_spacing'] = {args.input.letter_spacing}
if {args.input.line_spacing} is not None:
    req_params_{generated_uuid}['line_spacing'] = {args.input.line_spacing}
if {args.input.scale_x} is not None:
    req_params_{generated_uuid}['scale_x'] = {args.input.scale_x}
if {args.input.scale_y} is not None:
    req_params_{generated_uuid}['scale_y'] = {args.input.scale_y}
if {args.input.transform_x} is not None:
    req_params_{generated_uuid}['transform_x'] = {args.input.transform_x}
if {args.input.transform_y} is not None:
    req_params_{generated_uuid}['transform_y'] = {args.input.transform_y}
if {args.input.style_text} is not None:
    req_params_{generated_uuid}['style_text'] = {args.input.style_text}
if {args.input.underline} is not None:
    req_params_{generated_uuid}['underline'] = {args.input.underline}
if {args.input.italic} is not None:
    req_params_{generated_uuid}['italic'] = {args.input.italic}
if {args.input.bold} is not None:
    req_params_{generated_uuid}['bold'] = {args.input.bold}
if {args.input.has_shadow} is not None:
    req_params_{generated_uuid}['has_shadow'] = {args.input.has_shadow}
if {_is_meaningful_object(args.input.shadow_info)}:
    req_params_{generated_uuid}['shadow_info'] = {_to_type_constructor(args.input.shadow_info, 'ShadowInfo')}
req_{generated_uuid} = AddCaptionsRequest(**req_params_{generated_uuid})

resp_{generated_uuid} = await add_captions(draft_{args.input.draft_id}, req_{generated_uuid})
"""

        # 写入 API 调用到文件
        coze_file = ensure_coze2jianying_file()
        append_api_call_to_file(coze_file, api_call)


        if logger:
            logger.info(f"add_captions 调用成功")

        return Output(segment_ids=[], api_call=api_call)._asdict()

    except Exception as e:
        error_msg = f"调用 add_captions 时发生错误: {str(e)}"
        if logger:
            logger.error(error_msg)
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")

        return Output(success=False, message=error_msg)._asdict()

