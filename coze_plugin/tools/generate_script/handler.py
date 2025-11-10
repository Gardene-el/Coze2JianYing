"""
生成可执行的 Python 脚本工具

从草稿配置生成完整的可执行 Python 脚本，用户可以直接运行该脚本来生成剪映草稿。
这是手动导入和云端API之间的一个中间方案。
"""

import os
import json
from typing import NamedTuple, Union, List, Dict, Any
from runtime import Args


# Input/Output 类型定义
class Input(NamedTuple):
    """输入参数 for generate_script tool"""
    draft_ids: Union[str, List[str]]  # 单个 UUID 字符串或 UUID 列表
    api_base_url: str = "http://127.0.0.1:8000"  # API 服务地址
    output_folder: Union[str, None] = None  # 输出文件夹路径


def validate_uuid_format(uuid_str: str) -> bool:
    """验证 UUID 字符串格式"""
    try:
        import uuid
        uuid.UUID(uuid_str)
        return True
    except (ValueError, TypeError):
        return False


def normalize_draft_ids(draft_ids: Union[str, List[str]]) -> List[str]:
    """将 draft_ids 输入规范化为列表格式"""
    if isinstance(draft_ids, str):
        return [draft_ids]
    elif isinstance(draft_ids, list):
        return draft_ids
    else:
        return []


def load_draft_config(draft_id: str) -> tuple[bool, dict, str]:
    """从文件加载草稿配置"""
    draft_folder = os.path.join("/tmp", "jianying_assistant", "drafts", draft_id)
    config_file = os.path.join(draft_folder, "draft_config.json")
    
    if not os.path.exists(draft_folder):
        return False, {}, f"草稿文件夹不存在: {draft_id}"
    
    if not os.path.exists(config_file):
        return False, {}, f"草稿配置文件不存在: {draft_id}"
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return True, config, ""
    except json.JSONDecodeError as e:
        return False, {}, f"草稿配置文件格式错误: {str(e)}"
    except Exception as e:
        return False, {}, f"读取草稿配置失败: {str(e)}"


def generate_script_for_draft(draft_config: Dict[str, Any], api_base_url: str, output_folder: Union[str, None]) -> str:
    """
    为单个草稿生成 Python 脚本
    
    Args:
        draft_config: 草稿配置字典
        api_base_url: API 服务地址
        output_folder: 输出文件夹路径
        
    Returns:
        生成的 Python 脚本字符串
    """
    # 提取草稿基本信息
    draft_name = draft_config.get("draft_name", "未命名项目")
    width = draft_config.get("width", 1920)
    height = draft_config.get("height", 1080)
    fps = draft_config.get("fps", 30)
    tracks = draft_config.get("tracks", [])
    
    # 生成脚本内容
    script = f'''#!/usr/bin/env python3
"""
Coze2JianYing 自动草稿生成脚本
项目: {draft_name}
由 Coze 工作流自动生成

使用说明:
1. 确保草稿生成器 API 服务正在运行（默认端口 8000）
2. 确保已安装 requests: pip install requests
3. 执行脚本: python generated_script.py
"""

import requests
import json
import sys

# 配置
API_BASE_URL = "{api_base_url}"
OUTPUT_FOLDER = {json.dumps(output_folder)}

# 草稿基本配置
DRAFT_CONFIG = {{
    "draft_name": "{draft_name}",
    "width": {width},
    "height": {height},
    "fps": {fps}
}}

# 草稿内容
DRAFT_CONTENT = {json.dumps({"tracks": tracks}, ensure_ascii=False, indent=4)}


def check_api_server():
    """检查 API 服务是否可用"""
    try:
        response = requests.get(f"{{API_BASE_URL}}/", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def create_draft():
    """创建草稿"""
    print("📝 创建草稿...")
    response = requests.post(
        f"{{API_BASE_URL}}/api/draft/create",
        json=DRAFT_CONFIG,
        timeout=10
    )
    response.raise_for_status()
    result = response.json()
    draft_id = result["draft_id"]
    print(f"✅ 草稿创建成功: {{draft_id}}")
    return draft_id


def add_track(draft_id, track_type):
    """添加轨道"""
    response = requests.post(
        f"{{API_BASE_URL}}/api/draft/{{draft_id}}/add_track",
        json={{"track_type": track_type}},
        timeout=10
    )
    response.raise_for_status()
    return response.json()["track_index"]


def add_segment(draft_id, segment_config):
    """添加片段"""
    # 先创建片段
    response = requests.post(
        f"{{API_BASE_URL}}/api/segment/create",
        json=segment_config,
        timeout=10
    )
    response.raise_for_status()
    segment_id = response.json()["segment_id"]
    
    # 将片段添加到草稿
    response = requests.post(
        f"{{API_BASE_URL}}/api/draft/{{draft_id}}/add_segment",
        json={{"segment_id": segment_id}},
        timeout=10
    )
    response.raise_for_status()
    return segment_id


def add_content(draft_id):
    """添加所有内容到草稿"""
    print("🎬 添加内容...")
    
    for track_idx, track in enumerate(DRAFT_CONTENT["tracks"], 1):
        track_type = track["track_type"]
        segments = track.get("segments", [])
        
        print(f"  轨道 {{track_idx}} ({{track_type}}):")
        
        # 添加轨道
        track_index = add_track(draft_id, track_type)
        print(f"    ✓ 轨道已创建")
        
        # 添加片段
        for seg_idx, segment in enumerate(segments, 1):
            try:
                segment_id = add_segment(draft_id, segment)
                print(f"    ✓ 片段 {{seg_idx}}/{{len(segments)}} 已添加")
            except Exception as e:
                print(f"    ✗ 片段 {{seg_idx}} 失败: {{e}}")
    
    print("✅ 内容添加完成")


def save_draft(draft_id):
    """保存草稿"""
    print("💾 保存草稿...")
    
    payload = {{"draft_id": draft_id}}
    if OUTPUT_FOLDER:
        payload["output_folder"] = OUTPUT_FOLDER
    
    response = requests.post(
        f"{{API_BASE_URL}}/api/draft/{{draft_id}}/save",
        json=payload,
        timeout=300
    )
    response.raise_for_status()
    
    result = response.json()
    if result["success"]:
        print(f"✅ 保存成功: {{result['output_path']}}")
    return result


def main():
    """主流程"""
    print("=" * 60)
    print("  Coze2JianYing 自动草稿生成")
    print("=" * 60)
    print()
    
    try:
        # 检查服务
        print("🔍 检查 API 服务...")
        if not check_api_server():
            print("❌ 错误: 无法连接到 API 服务")
            print("\\n请确保草稿生成器应用正在运行，API 服务已启动")
            return 1
        print("✅ API 服务正常\\n")
        
        # 创建草稿
        draft_id = create_draft()
        print()
        
        # 添加内容
        add_content(draft_id)
        print()
        
        # 保存草稿
        save_draft(draft_id)
        print()
        
        print("=" * 60)
        print("  🎉 完成！")
        print("=" * 60)
        return 0
        
    except requests.exceptions.ConnectionError:
        print("\\n❌ 连接错误: 无法连接到 API 服务")
        return 1
    except requests.exceptions.HTTPError as e:
        print(f"\\n❌ API 错误: {{e}}")
        print(f"响应: {{e.response.text}}")
        return 1
    except Exception as e:
        print(f"\\n❌ 错误: {{e}}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
'''
    
    return script


def handler(args: Args[Input]) -> Dict[str, Any]:
    """
    生成可执行 Python 脚本的处理器
    
    Args:
        args: 输入参数
        
    Returns:
        包含脚本内容的字典
    """
    args.logger.info("=" * 60)
    args.logger.info("开始生成 Python 脚本")
    args.logger.info("=" * 60)
    
    # 规范化 draft_ids
    draft_ids = normalize_draft_ids(args.input.draft_ids)
    
    if not draft_ids:
        error_msg = "错误: 未提供有效的 draft_ids"
        args.logger.error(error_msg)
        return {
            "success": False,
            "message": error_msg,
            "scripts": []
        }
    
    args.logger.info(f"要生成脚本的草稿数量: {len(draft_ids)}")
    
    # 生成脚本
    scripts = []
    errors = []
    
    for draft_id in draft_ids:
        args.logger.info(f"\\n处理草稿: {draft_id}")
        
        # 验证 UUID 格式
        if not validate_uuid_format(draft_id):
            error = f"无效的 UUID 格式: {draft_id}"
            args.logger.error(f"  ✗ {error}")
            errors.append(error)
            continue
        
        # 加载草稿配置
        success, config, error = load_draft_config(draft_id)
        
        if not success:
            args.logger.error(f"  ✗ {error}")
            errors.append(error)
            continue
        
        args.logger.info(f"  ✓ 配置加载成功")
        
        # 生成脚本
        try:
            script_content = generate_script_for_draft(
                config, 
                args.input.api_base_url,
                args.input.output_folder
            )
            
            scripts.append({
                "draft_id": draft_id,
                "draft_name": config.get("draft_name", "未命名"),
                "script": script_content
            })
            
            args.logger.info(f"  ✓ 脚本生成成功")
            
        except Exception as e:
            error = f"生成脚本失败 ({draft_id}): {str(e)}"
            args.logger.error(f"  ✗ {error}")
            errors.append(error)
    
    # 汇总结果
    args.logger.info("\\n" + "=" * 60)
    args.logger.info("脚本生成完成")
    args.logger.info(f"成功: {len(scripts)} 个")
    args.logger.info(f"失败: {len(errors)} 个")
    args.logger.info("=" * 60)
    
    success = len(scripts) > 0
    
    # 返回结果
    result = {
        "success": success,
        "message": f"成功生成 {len(scripts)} 个脚本" if success else "脚本生成失败",
        "scripts": scripts,
        "errors": errors if errors else None
    }
    
    return result
