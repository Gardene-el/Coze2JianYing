"""
add_text_effect 工具处理器

自动从 API 端点生成: /text/{segment_id}/add_effect
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
    """add_text_effect 工具的输入参数"""
    segment_id: str
    effect_id: Optional[str] = Ellipsis


# Output 现在返回 Dict[str, Any] 而不是 NamedTuple
# 这确保了在 Coze 平台中正确的 JSON 对象序列化


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


def handler(args: Args[Input]) -> Dict[str, Any]:
    """
    add_text_effect 的主处理函数
    
    Args:
        args: Input arguments
        
    Returns:
        Dict containing response data
    """
    logger = getattr(args, 'logger', None)
    
    if logger:
        logger.info(f"调用 add_text_effect，参数: {args.input}")
    
    try:
        # 生成唯一 UUID
        generated_uuid = str(uuid.uuid4())
        
        if logger:
            logger.info(f"生成 UUID: {generated_uuid}")

    # 生成 API 调用代码
    api_call = f"""
# API 调用: add_text_effect
# 时间: {time.strftime('%Y-%m-%d %H:%M:%S')}

segment_id_{generated_uuid} = "{generated_uuid}"

    # 构造 request 对象
    req_{generated_uuid} = AddTextEffectRequest(effect_id=args.input.effect_id)

resp_{generated_uuid} = await add_text_effect(segment_id_{generated_uuid}, req_{generated_uuid})
"""
    
    # 写入 API 调用到文件
    coze_file = ensure_coze2jianying_file()
    append_api_call_to_file(coze_file, api_call)

        
        if logger:
            logger.info(f"add_text_effect 调用成功")
        
        return {
        "success": True,
        "effect_id": "",
        "message": "操作成功"
        }
        
    except Exception as e:
        error_msg = f"调用 add_text_effect 时发生错误: {str(e)}"
        if logger:
            logger.error(error_msg)
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
        
        return {
            "success": False,
            "message": error_msg
        }

