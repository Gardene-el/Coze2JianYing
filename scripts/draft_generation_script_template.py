#!/usr/bin/env python3
"""
Coze2JianYing 自动草稿生成脚本模板
由 Coze 工作流生成，用于本地执行

使用说明：
1. 确保草稿生成器 API 服务正在运行（默认端口 8000）
2. 确保已安装 requests: pip install requests
3. 执行脚本: python draft_generation_script_template.py
"""

import requests
import json
import sys
from typing import Dict, List, Any

# ============================================================================
# 配置区域 - 由 Coze 工作流自动填充
# ============================================================================

# API 服务地址
API_BASE_URL = "http://127.0.0.1:8000"

# 草稿基本配置
DRAFT_CONFIG = {
    "draft_name": "示例项目",
    "width": 1920,
    "height": 1080,
    "fps": 30
}

# 草稿内容 - 由 Coze 工作流生成
# 这是标准的 Draft Generator Interface 格式
DRAFT_CONTENT = {
    "tracks": [
        # 示例：图片轨道
        {
            "track_type": "video",  # 图片使用 video 轨道
            "segments": [
                {
                    "segment_type": "image",
                    "material_url": "https://example.com/image1.jpg",
                    "time_range": {"start": 0, "duration": 3000000},  # 3秒，微秒单位
                    "position": {"x": 0.0, "y": 0.0},
                    "scale": {"x": 1.0, "y": 1.0}
                }
            ]
        },
        # 示例：音频轨道
        {
            "track_type": "audio",
            "segments": [
                {
                    "segment_type": "audio",
                    "material_url": "https://example.com/audio1.mp3",
                    "time_range": {"start": 0, "duration": 5000000},  # 5秒
                    "volume": 0.8,
                    "fade_in_duration": 500000,  # 0.5秒淡入
                    "fade_out_duration": 500000  # 0.5秒淡出
                }
            ]
        },
        # 示例：字幕轨道
        {
            "track_type": "text",
            "segments": [
                {
                    "segment_type": "text",
                    "content": "示例字幕文本",
                    "time_range": {"start": 0, "duration": 3000000},
                    "position": {"x": 0.5, "y": 0.9},  # 屏幕底部居中
                    "font_size": 36,
                    "font_color": "#FFFFFF",
                    "background_color": "#000000",
                    "background_alpha": 0.5
                }
            ]
        }
    ]
}

# 输出文件夹路径（None 表示使用默认路径）
OUTPUT_FOLDER = None

# ============================================================================
# API 调用函数 - 无需修改
# ============================================================================

def check_api_server() -> bool:
    """
    检查 API 服务是否可用
    
    Returns:
        True 如果服务可用，False 否则
    """
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def create_draft() -> str:
    """
    创建草稿
    
    Returns:
        草稿 ID (UUID)
        
    Raises:
        Exception: API 调用失败
    """
    print("📝 创建草稿...")
    print(f"   项目名称: {DRAFT_CONFIG['draft_name']}")
    print(f"   分辨率: {DRAFT_CONFIG['width']}x{DRAFT_CONFIG['height']}")
    print(f"   帧率: {DRAFT_CONFIG['fps']}")
    
    response = requests.post(
        f"{API_BASE_URL}/api/draft/create",
        json=DRAFT_CONFIG,
        timeout=10
    )
    response.raise_for_status()
    
    result = response.json()
    draft_id = result.get("draft_id")
    
    if not draft_id:
        raise Exception("API 未返回草稿 ID")
    
    print(f"✅ 草稿创建成功: {draft_id}")
    return draft_id


def add_track(draft_id: str, track_type: str) -> int:
    """
    添加轨道
    
    Args:
        draft_id: 草稿 ID
        track_type: 轨道类型 (video/audio/text/sticker)
        
    Returns:
        轨道索引
    """
    response = requests.post(
        f"{API_BASE_URL}/api/draft/{draft_id}/add_track",
        json={"track_type": track_type},
        timeout=10
    )
    response.raise_for_status()
    
    result = response.json()
    return result.get("track_index", 0)


def add_segment(draft_id: str, segment_config: Dict[str, Any]) -> str:
    """
    添加片段到草稿
    
    Args:
        draft_id: 草稿 ID
        segment_config: 片段配置
        
    Returns:
        片段 ID
    """
    response = requests.post(
        f"{API_BASE_URL}/api/segment/create",
        json=segment_config,
        timeout=10
    )
    response.raise_for_status()
    
    segment_result = response.json()
    segment_id = segment_result.get("segment_id")
    
    if not segment_id:
        raise Exception("API 未返回片段 ID")
    
    # 将片段添加到草稿
    response = requests.post(
        f"{API_BASE_URL}/api/draft/{draft_id}/add_segment",
        json={"segment_id": segment_id},
        timeout=10
    )
    response.raise_for_status()
    
    return segment_id


def add_content_to_draft(draft_id: str):
    """
    将所有内容添加到草稿
    
    Args:
        draft_id: 草稿 ID
    """
    print("🎬 添加内容到草稿...")
    
    track_count = len(DRAFT_CONTENT.get("tracks", []))
    print(f"   共 {track_count} 个轨道")
    
    for track_idx, track in enumerate(DRAFT_CONTENT.get("tracks", []), 1):
        track_type = track.get("track_type", "video")
        segments = track.get("segments", [])
        
        print(f"\\n   轨道 {track_idx}/{track_count} ({track_type}):")
        
        # 添加轨道
        track_index = add_track(draft_id, track_type)
        print(f"   ✓ 轨道已创建 (索引: {track_index})")
        
        # 添加片段
        segment_count = len(segments)
        for seg_idx, segment in enumerate(segments, 1):
            try:
                segment_id = add_segment(draft_id, segment)
                print(f"   ✓ 片段 {seg_idx}/{segment_count} 已添加 (ID: {segment_id[:8]}...)")
            except Exception as e:
                print(f"   ✗ 片段 {seg_idx}/{segment_count} 添加失败: {e}")
                # 继续处理其他片段
    
    print("\\n✅ 所有内容已添加")


def save_draft(draft_id: str) -> Dict[str, Any]:
    """
    保存草稿到剪映项目文件夹
    
    Args:
        draft_id: 草稿 ID
        
    Returns:
        保存结果
    """
    print("💾 保存草稿到剪映...")
    
    payload = {"draft_id": draft_id}
    if OUTPUT_FOLDER:
        payload["output_folder"] = OUTPUT_FOLDER
    
    response = requests.post(
        f"{API_BASE_URL}/api/draft/{draft_id}/save",
        json=payload,
        timeout=300  # 保存可能需要较长时间（下载素材）
    )
    response.raise_for_status()
    
    result = response.json()
    
    if result.get("success"):
        output_path = result.get("output_path", "未知路径")
        print(f"✅ 草稿保存成功")
        print(f"   输出路径: {output_path}")
    else:
        print(f"⚠️  草稿保存出现问题: {result.get('message', '未知错误')}")
    
    return result


# ============================================================================
# 主程序 - 无需修改
# ============================================================================

def print_header():
    """打印程序标题"""
    print("=" * 70)
    print("   Coze2JianYing 自动草稿生成脚本".center(70))
    print("=" * 70)
    print()


def print_summary():
    """打印配置摘要"""
    print("📋 配置摘要:")
    print(f"   API 地址: {API_BASE_URL}")
    print(f"   项目名称: {DRAFT_CONFIG['draft_name']}")
    print(f"   分辨率: {DRAFT_CONFIG['width']}x{DRAFT_CONFIG['height']}")
    print(f"   帧率: {DRAFT_CONFIG['fps']}")
    print(f"   轨道数量: {len(DRAFT_CONTENT.get('tracks', []))}")
    print()


def main():
    """主流程"""
    print_header()
    print_summary()
    
    try:
        # 检查 API 服务
        print("🔍 检查 API 服务...")
        if not check_api_server():
            print("❌ 错误: 无法连接到 API 服务")
            print()
            print("请确保:")
            print("  1. 草稿生成器应用正在运行")
            print("  2. 切换到\"云端服务\"标签页")
            print("  3. 点击\"启动服务\"按钮")
            print("  4. API 服务运行在 http://127.0.0.1:8000")
            print()
            return 1
        
        print("✅ API 服务连接正常")
        print()
        
        # 1. 创建草稿
        draft_id = create_draft()
        print()
        
        # 2. 添加内容
        add_content_to_draft(draft_id)
        print()
        
        # 3. 保存草稿
        result = save_draft(draft_id)
        print()
        
        # 4. 完成
        print("=" * 70)
        print("   🎉 草稿生成完成！".center(70))
        print("=" * 70)
        print()
        print("现在可以:")
        print("  1. 打开剪映专业版")
        print("  2. 在草稿列表中找到新生成的项目")
        print("  3. 开始编辑你的视频")
        print()
        
        return 0
        
    except requests.exceptions.ConnectionError as e:
        print()
        print("❌ 连接错误: 无法连接到 API 服务")
        print(f"   详细信息: {e}")
        print()
        print("解决方法:")
        print("  1. 确保草稿生成器应用正在运行")
        print("  2. 确保 API 服务已启动 (\"云端服务\" -> \"启动服务\")")
        print("  3. 检查端口是否被占用")
        return 1
        
    except requests.exceptions.HTTPError as e:
        print()
        print(f"❌ API 错误: {e}")
        print(f"   状态码: {e.response.status_code}")
        print(f"   响应内容: {e.response.text}")
        print()
        return 1
        
    except requests.exceptions.Timeout:
        print()
        print("❌ 请求超时")
        print("   可能原因:")
        print("   1. 素材下载时间过长")
        print("   2. 网络连接不稳定")
        print("   3. 服务器响应缓慢")
        print()
        return 1
        
    except KeyboardInterrupt:
        print()
        print("⚠️  用户中断操作")
        return 130
        
    except Exception as e:
        print()
        print(f"❌ 未知错误: {e}")
        print()
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
