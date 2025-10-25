#!/usr/bin/env python3
"""
示例：使用 make_image_info 和 add_images 的完整工作流

演示如何使用 make_image_info 工具生成图片配置字符串，
然后将这些字符串组合成数组，最后传递给 add_images 工具。

这是问题 #issue 中要求的使用场景。
"""

import sys
import os
import json
import types
from typing import Generic, TypeVar

# Add project path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock the runtime module for demonstration
T = TypeVar('T')

class MockArgsType(Generic[T]):
    pass

runtime_mock = types.ModuleType('runtime')
runtime_mock.Args = MockArgsType
sys.modules['runtime'] = runtime_mock

# Now import the tools
from coze_plugin.tools.make_image_info.handler import handler as make_image_info, Input as MakeInput
from coze_plugin.tools.add_images.handler import handler as add_images, Input as AddInput
from coze_plugin.tools.create_draft.handler import handler as create_draft, Input as CreateInput


class MockArgs:
    """Mock Args class for demonstration"""
    def __init__(self, input_data):
        self.input = input_data
        self.logger = None


def main():
    print("=" * 80)
    print("演示：使用 make_image_info 生成图片信息数组字符串")
    print("=" * 80)
    
    # 步骤 1: 创建一个草稿
    print("\n步骤 1: 创建草稿")
    print("-" * 40)
    
    draft_result = create_draft(MockArgs(CreateInput(
        draft_name="数组字符串演示",
        fps=30
    )))
    
    if not draft_result["success"]:
        print(f"❌ 创建草稿失败: {draft_result["message"]}")
        return
    
    draft_id = draft_result["draft_id"]
    print(f"✅ 草稿创建成功")
    print(f"   草稿 ID: {draft_id}")
    
    # 步骤 2: 使用 make_image_info 生成多个图片配置字符串
    print("\n步骤 2: 使用 make_image_info 生成图片配置字符串")
    print("-" * 40)
    
    # 图片 1: 基本配置
    image1_result = make_image_info(MockArgs(MakeInput(
        image_url="https://s.coze.cn/t/W9CvmtJHJWI/",
        start=0,
        end=3000,
    )))
    
    if image1_result["success"]:
        print(f"✅ 图片 1 配置字符串:")
        print(f"   {image1_result["image_info_string"]}")
    else:
        print(f"❌ 生成失败: {image1_result["message"]}")
        return
    
    # 图片 2: 带动画和滤镜
    image2_result = make_image_info(MockArgs(MakeInput(
        image_url="https://example.com/image2.jpg",
        start=3000,
        end=6000,
        in_animation="轻微放大",
        in_animation_duration=500,
        filter_type="暖冬",
        filter_intensity=0.8
    )))
    
    if image2_result["success"]:
        print(f"✅ 图片 2 配置字符串:")
        print(f"   {image2_result["image_info_string"]}")
    else:
        print(f"❌ 生成失败: {image2_result["message"]}")
        return
    
    # 图片 3: 带位置和缩放
    image3_result = make_image_info(MockArgs(MakeInput(
        image_url="https://example.com/image3.jpg",
        start=6000,
        end=9000,
        position_x=0.1,
        position_y=0.1,
        scale_x=1.2,
        scale_y=1.2,
        rotation=15.0,
        opacity=0.9
    )))
    
    if image3_result["success"]:
        print(f"✅ 图片 3 配置字符串:")
        print(f"   {image3_result["image_info_string"]}")
    else:
        print(f"❌ 生成失败: {image3_result["message"]}")
        return
    
    # 步骤 3: 将字符串收集到数组中
    print("\n步骤 3: 将配置字符串收集到数组中")
    print("-" * 40)
    
    # 这是核心：创建一个数组字符串 (数组中的每个元素是字符串)
    image_infos_array = [
        image1_result["image_info_string"],
        image2_result["image_info_string"],
        image3_result["image_info_string"]
    ]
    
    print(f"✅ 创建了包含 {len(image_infos_array)} 个字符串的数组")
    print(f"   数组类型: {type(image_infos_array)}")
    print(f"   第一个元素类型: {type(image_infos_array[0])}")
    print(f"   数组内容:")
    for i, img_str in enumerate(image_infos_array, 1):
        print(f"   [{i}] {img_str[:60]}..." if len(img_str) > 60 else f"   [{i}] {img_str}")
    
    # 步骤 4: 将数组字符串传递给 add_images
    print("\n步骤 4: 将数组字符串传递给 add_images")
    print("-" * 40)
    
    add_result = add_images(MockArgs(AddInput(
        draft_id=draft_id,
        image_infos=image_infos_array  # 数组字符串格式！
    )))
    
    if not add_result.success:
        print(f"❌ 添加图片失败: {add_result.message}")
        return
    
    print(f"✅ {add_result.message}")
    print(f"   生成的片段 ID: {add_result.segment_ids}")
    print(f"   片段信息:")
    for info in add_result.segment_infos:
        print(f"      - ID: {info['id']}")
        print(f"        时间: {info['start']}ms - {info['end']}ms")
    
    # 步骤 5: 验证结果
    print("\n步骤 5: 验证草稿配置")
    print("-" * 40)
    
    draft_folder = os.path.join("/tmp", "jianying_assistant", "drafts", draft_id)
    config_file = os.path.join(draft_folder, "draft_config.json")
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    print(f"✅ 草稿配置验证成功")
    print(f"   草稿名称: {config['project']['name']}")
    print(f"   轨道数量: {len(config['tracks'])}")
    print(f"   图片轨道片段数: {len(config['tracks'][0]['segments'])}")
    
    # 显示片段详细信息
    print(f"\n   片段详细信息:")
    for i, segment in enumerate(config['tracks'][0]['segments'], 1):
        print(f"   片段 {i}:")
        print(f"      URL: {segment['material_url']}")
        print(f"      时间: {segment['time_range']['start']}ms - {segment['time_range']['end']}ms")
        if segment['animations']['intro']:
            print(f"      入场动画: {segment['animations']['intro']}")
        if segment['effects']['filter_type']:
            print(f"      滤镜: {segment['effects']['filter_type']}")
        if segment['transform']['rotation'] != 0:
            print(f"      旋转: {segment['transform']['rotation']}°")
    
    # 总结
    print("\n" + "=" * 80)
    print("✅ 演示完成！")
    print("=" * 80)
    print("\n关键要点:")
    print("1. make_image_info 生成单个图片的 JSON 字符串配置")
    print("2. 将多个字符串收集到一个数组中 (数组字符串格式)")
    print("3. add_images 现在支持接收数组字符串作为 image_infos 参数")
    print("4. 这种方式特别适合在 Coze 工作流中动态构建图片配置")
    print("\n支持的 image_infos 格式:")
    print("  - 格式1: 数组对象 (原有支持)")
    print("  - 格式2: 数组字符串 (新增支持) ← 本演示使用的格式")
    print("  - 格式3: JSON字符串 (原有支持)")


if __name__ == "__main__":
    main()
