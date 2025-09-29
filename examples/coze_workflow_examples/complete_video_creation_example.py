#!/usr/bin/env python3
"""
Complete Video Creation Example

Demonstrates how to use all the Coze tools together to create a complete video project.
This example shows the full workflow from draft creation to final export.
"""

def example_complete_video_workflow():
    """Example: Complete video creation workflow using all tools"""
    
    workflow = {
        "workflow_name": "完整视频制作流程",
        "description": "展示如何使用所有Coze工具创建完整视频项目",
        "steps": [
            {
                "step": 1,
                "name": "创建项目草稿",
                "tool": "create_draft",
                "input": {
                    "draft_name": "产品宣传视频",
                    "width": 1920,
                    "height": 1080,
                    "fps": 30,
                    "video_quality": "1080p",
                    "audio_quality": "320k",
                    "background_color": "#000000"
                },
                "output_variable": "project_draft"
            },
            {
                "step": 2,
                "name": "添加主要视频内容",
                "tool": "add_videos",
                "input": {
                    "draft_id": "{{project_draft.draft_id}}",
                    "video_urls": [
                        "https://example.com/intro.mp4",
                        "https://example.com/product_demo.mp4",
                        "https://example.com/testimonial.mp4"
                    ],
                    "filters": ["暖冬", "电影", "清新"],
                    "transitions": ["淡化", "切镜", "滑动"],
                    "volumes": [1.0, 0.9, 1.0],
                    "start_time": 0
                },
                "output_variable": "main_videos"
            },
            {
                "step": 3,
                "name": "添加背景音乐",
                "tool": "add_audios",
                "input": {
                    "draft_id": "{{project_draft.draft_id}}",
                    "audio_urls": [
                        "https://example.com/background_music.mp3"
                    ],
                    "volumes": [0.3],
                    "fade_ins": [2000],
                    "fade_outs": [3000],
                    "start_time": 0
                },
                "output_variable": "background_music"
            },
            {
                "step": 4,
                "name": "添加产品图片展示",
                "tool": "add_images",
                "input": {
                    "draft_id": "{{project_draft.draft_id}}",
                    "image_urls": [
                        "https://example.com/product1.jpg",
                        "https://example.com/product2.jpg",
                        "https://example.com/logo.png"
                    ],
                    "durations": [3000, 3000, 2000],
                    "transitions": ["淡化", "缩放", "旋转"],
                    "positions_x": [0.0, 0.0, 0.8],
                    "positions_y": [0.0, 0.0, -0.8],
                    "scales": [1.0, 1.0, 0.3],
                    "start_time": 45000
                },
                "output_variable": "product_images"
            },
            {
                "step": 5,
                "name": "添加主要字幕",
                "tool": "add_captions",
                "input": {
                    "draft_id": "{{project_draft.draft_id}}",
                    "captions": [
                        {
                            "text": "欢迎来到我们的产品世界",
                            "start_time": 1000,
                            "end_time": 4000,
                            "position_x": 0.5,
                            "position_y": 0.2
                        },
                        {
                            "text": "创新科技，改变生活",
                            "start_time": 5000,
                            "end_time": 8000
                        },
                        {
                            "text": "立即体验",
                            "start_time": 50000,
                            "end_time": 53000
                        }
                    ],
                    "font_family": "思源黑体",
                    "font_size": 56,
                    "color": "#FFFFFF",
                    "position_x": 0.5,
                    "position_y": 0.85,
                    "alignment": "center"
                },
                "output_variable": "main_captions"
            },
            {
                "step": 6,
                "name": "添加特效增强",
                "tool": "add_effects",
                "input": {
                    "draft_id": "{{project_draft.draft_id}}",
                    "effects": [
                        {
                            "effect_type": "光芒四射",
                            "start_time": 0,
                            "end_time": 2000,
                            "intensity": 1.5,
                            "position_x": 0.5,
                            "position_y": 0.5
                        },
                        {
                            "effect_type": "粒子爆炸",
                            "start_time": 48000,
                            "end_time": 51000,
                            "intensity": 1.8,
                            "properties": {
                                "particle_count": 200,
                                "color": "#FFD700"
                            }
                        },
                        {
                            "effect_type": "光效闪烁",
                            "start_time": 52000,
                            "end_time": 55000,
                            "intensity": 1.2
                        }
                    ],
                    "default_intensity": 1.0
                },
                "output_variable": "visual_effects"
            },
            {
                "step": 7,
                "name": "添加音效",
                "tool": "add_audios",
                "input": {
                    "draft_id": "{{project_draft.draft_id}}",
                    "audio_urls": [
                        "https://example.com/intro_sound.wav",
                        "https://example.com/click_sound.wav",
                        "https://example.com/ending_sound.wav"
                    ],
                    "volumes": [0.8, 0.6, 1.0],
                    "start_time": 0
                },
                "output_variable": "sound_effects"
            },
            {
                "step": 8,
                "name": "添加补充说明字幕",
                "tool": "add_captions",
                "input": {
                    "draft_id": "{{project_draft.draft_id}}",
                    "captions": [
                        {
                            "text": "* 更多详情请访问官网",
                            "start_time": 53000,
                            "end_time": 57000,
                            "position_x": 0.95,
                            "position_y": 0.95
                        }
                    ],
                    "font_size": 24,
                    "color": "#CCCCCC",
                    "alignment": "right"
                },
                "output_variable": "footnote_captions"
            },
            {
                "step": 9,
                "name": "导出最终草稿",
                "tool": "export_drafts",
                "input": {
                    "draft_ids": "{{project_draft.draft_id}}",
                    "remove_temp_files": False
                },
                "output_variable": "final_draft"
            }
        ]
    }
    
    print("=== 完整视频制作工作流示例 ===")
    print(f"工作流名称: {workflow['workflow_name']}")
    print(f"描述: {workflow['description']}")
    print(f"总步骤数: {len(workflow['steps'])}")
    
    print("\n=== 工作流步骤详情 ===")
    for step in workflow["steps"]:
        print(f"\n步骤 {step['step']}: {step['name']}")
        print(f"使用工具: {step['tool']}")
        print(f"输出变量: {step['output_variable']}")
        
        # 显示关键输入参数
        if step['tool'] == 'create_draft':
            input_params = step['input']
            print(f"  项目设置: {input_params['width']}x{input_params['height']} @ {input_params['fps']}fps")
        elif step['tool'] == 'add_videos':
            print(f"  视频数量: {len(step['input']['video_urls'])}")
            print(f"  滤镜效果: {step['input']['filters']}")
        elif step['tool'] == 'add_audios':
            print(f"  音频数量: {len(step['input']['audio_urls'])}")
            if 'volumes' in step['input']:
                print(f"  音量设置: {step['input']['volumes']}")
        elif step['tool'] == 'add_images':
            print(f"  图片数量: {len(step['input']['image_urls'])}")
            print(f"  显示时长: {step['input']['durations']}ms")
        elif step['tool'] == 'add_captions':
            print(f"  字幕数量: {len(step['input']['captions'])}")
            print(f"  字体设置: {step['input'].get('font_family', '默认')} {step['input'].get('font_size', 48)}px")
        elif step['tool'] == 'add_effects':
            print(f"  特效数量: {len(step['input']['effects'])}")
            effect_types = [e['effect_type'] for e in step['input']['effects']]
            print(f"  特效类型: {effect_types}")
    
    print("\n=== 预期结果 ===")
    print("完成此工作流后，你将获得一个包含以下内容的完整视频草稿：")
    print("- 1个视频轨道：包含3个主要视频片段(intro、产品演示、用户评价)")
    print("- 2个音频轨道：背景音乐轨道 + 音效轨道")
    print("- 1个图片轨道：产品图片展示 + Logo")
    print("- 2个字幕轨道：主要字幕 + 补充说明")
    print("- 1个特效轨道：开场光效 + 结尾粒子效果")
    print("- 总时长：约57秒")
    print("- 导出的JSON数据：可供草稿生成器使用")
    
    return workflow


def example_simple_workflow():
    """Example: Simple workflow for beginners"""
    
    simple_workflow = {
        "workflow_name": "简单视频制作",
        "description": "适合初学者的基础视频制作流程",
        "steps": [
            {
                "step": 1,
                "tool": "create_draft",
                "input": {
                    "draft_name": "我的第一个视频",
                    "width": 1280,
                    "height": 720
                }
            },
            {
                "step": 2,
                "tool": "add_videos",
                "input": {
                    "draft_id": "{{draft.draft_id}}",
                    "video_urls": ["https://example.com/myvideo.mp4"]
                }
            },
            {
                "step": 3,
                "tool": "add_captions",
                "input": {
                    "draft_id": "{{draft.draft_id}}",
                    "captions": [
                        {
                            "text": "Hello World!",
                            "start_time": 1000,
                            "end_time": 4000
                        }
                    ]
                }
            },
            {
                "step": 4,
                "tool": "export_drafts",
                "input": {
                    "draft_ids": "{{draft.draft_id}}"
                }
            }
        ]
    }
    
    print("\n=== 简单工作流示例 ===")
    print("这是一个4步完成的基础视频制作流程：")
    for i, step in enumerate(simple_workflow["steps"], 1):
        print(f"{i}. {step['tool']} - 使用{step['tool']}工具")
    
    return simple_workflow


def example_advanced_workflow():
    """Example: Advanced workflow with complex effects"""
    
    advanced_workflow = {
        "workflow_name": "高级视频制作",
        "description": "包含复杂特效和多轨道的专业视频制作",
        "features": [
            "多层视频合成",
            "复杂音频混合",
            "动态字幕效果",
            "高级特效组合",
            "精确时间控制"
        ],
        "estimated_duration": "2-3分钟",
        "complexity": "高级"
    }
    
    print("\n=== 高级工作流特性 ===")
    print(f"工作流名称: {advanced_workflow['workflow_name']}")
    print(f"复杂度: {advanced_workflow['complexity']}")
    print(f"预计时长: {advanced_workflow['estimated_duration']}")
    print("主要特性:")
    for feature in advanced_workflow["features"]:
        print(f"  • {feature}")
    
    print("\n高级工作流可以实现:")
    print("- 多达10+个轨道的复杂合成")
    print("- 精确到毫秒的时间控制")
    print("- 自定义特效参数组合")
    print("- 专业级音频后期处理")
    print("- 多语言字幕支持")
    
    return advanced_workflow


if __name__ == "__main__":
    print("Coze剪映助手 - 完整视频制作示例")
    print("=" * 50)
    
    # 运行完整工作流示例
    complete_workflow = example_complete_video_workflow()
    
    # 运行简单工作流示例
    simple_workflow = example_simple_workflow()
    
    # 运行高级工作流示例
    advanced_workflow = example_advanced_workflow()
    
    print("\n" + "=" * 50)
    print("更多详细信息，请查看各工具的README文档:")
    print("- tools/create_draft/README.md")
    print("- tools/add_videos/README.md")
    print("- tools/add_audios/README.md")
    print("- tools/add_captions/README.md")
    print("- tools/add_images/README.md")
    print("- tools/add_effects/README.md")
    print("- tools/export_drafts/README.md")