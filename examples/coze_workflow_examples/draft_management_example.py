#!/usr/bin/env python3
"""
Draft Management Workflow Examples

This file demonstrates how to use create_draft and export_drafts tools
in Coze workflows, showcasing the UUID-based draft management system.
"""

import json


def example_basic_workflow():
    """Example: Basic draft creation and export workflow"""
    print("=== Example 1: Basic Draft Workflow ===")
    
    # Step 1: Create a draft
    create_draft_step = {
        "tool": "create_draft",
        "input": {
            "project_name": "我的第一个Coze项目",
            "width": 1920,
            "height": 1080,
            "fps": 30,
            "video_quality": "1080p",
            "audio_quality": "320k",
            "background_color": "#000000"
        },
        "output_variable": "new_draft"
    }
    
    print("Step 1 - Create Draft:")
    print(json.dumps(create_draft_step, ensure_ascii=False, indent=2))
    
    print("\nExpected Output:")
    expected_create_output = {
        "draft_id": "123e4567-e89b-12d3-a456-426614174000",
        "success": True,
        "message": "草稿创建成功，ID: 123e4567-e89b-12d3-a456-426614174000"
    }
    print(json.dumps(expected_create_output, ensure_ascii=False, indent=2))
    
    # Step 2: (Here you would add media content, text, effects, etc.)
    print("\n-- Here you would add content to the draft using other tools --")
    print("-- For example: add_video_track, add_audio_track, add_text_track --")
    
    # Step 3: Export the draft
    export_draft_step = {
        "tool": "export_drafts",
        "input": {
            "draft_ids": "{{new_draft.draft_id}}",
            "remove_temp_files": True
        },
        "output_variable": "exported_draft"
    }
    
    print("\nStep 3 - Export Draft:")
    print(json.dumps(export_draft_step, ensure_ascii=False, indent=2))
    
    print("\nExpected Export Output:")
    expected_export_output = {
        "draft_data": "{\"format_version\":\"1.0\",\"export_type\":\"single_draft\",...}",
        "exported_count": 1,
        "success": True,
        "message": "成功导出 1 个草稿; 临时文件已清理"
    }
    print(json.dumps(expected_export_output, ensure_ascii=False, indent=2))


def example_4k_project():
    """Example: Creating a 4K high-quality project"""
    print("\n=== Example 2: 4K High-Quality Project ===")
    
    workflow_steps = [
        {
            "tool": "create_draft",
            "input": {
                "project_name": "4K超清宣传片",
                "width": 3840,
                "height": 2160,
                "fps": 60,
                "video_quality": "4k",
                "audio_quality": "lossless",
                "background_color": "#FFFFFF"
            },
            "output_variable": "hq_draft"
        },
        {
            "tool": "export_drafts",
            "input": {
                "draft_ids": "{{hq_draft.draft_id}}",
                "remove_temp_files": False  # Keep files for further editing
            },
            "output_variable": "hq_exported"
        }
    ]
    
    print("4K Project Workflow:")
    for i, step in enumerate(workflow_steps, 1):
        print(f"\nStep {i}:")
        print(json.dumps(step, ensure_ascii=False, indent=2))


def example_mobile_video():
    """Example: Creating a mobile vertical video project"""
    print("\n=== Example 3: Mobile Vertical Video ===")
    
    mobile_draft = {
        "tool": "create_draft",
        "input": {
            "project_name": "抖音短视频",
            "width": 1080,
            "height": 1920,  # Vertical aspect ratio
            "fps": 30,
            "video_quality": "1080p",
            "audio_quality": "320k",
            "background_color": "#000000"
        },
        "output_variable": "mobile_draft"
    }
    
    print("Mobile Video Configuration:")
    print(json.dumps(mobile_draft, ensure_ascii=False, indent=2))
    
    print("\nNote: This creates a 9:16 aspect ratio perfect for mobile platforms")


def example_batch_export():
    """Example: Batch exporting multiple drafts"""
    print("\n=== Example 4: Batch Export Multiple Drafts ===")
    
    # Assume we have created multiple drafts in previous steps
    batch_export = {
        "tool": "export_drafts",
        "input": {
            "draft_ids": [
                "{{draft1.draft_id}}",
                "{{draft2.draft_id}}",
                "{{draft3.draft_id}}"
            ],
            "remove_temp_files": True
        },
        "output_variable": "batch_exported"
    }
    
    print("Batch Export Configuration:")
    print(json.dumps(batch_export, ensure_ascii=False, indent=2))
    
    print("\nExpected Batch Output:")
    expected_batch_output = {
        "draft_data": "{\"format_version\":\"1.0\",\"export_type\":\"batch_draft\",\"draft_count\":3,...}",
        "exported_count": 3,
        "success": True,
        "message": "成功导出 3 个草稿; 临时文件已清理"
    }
    print(json.dumps(expected_batch_output, ensure_ascii=False, indent=2))


def example_error_handling():
    """Example: Error handling and validation"""
    print("\n=== Example 5: Error Handling ===")
    
    # Invalid parameters example
    invalid_create = {
        "tool": "create_draft",
        "input": {
            "project_name": "错误测试",
            "width": -1,  # Invalid width
            "height": 1080,
            "fps": 200,   # Invalid fps
            "video_quality": "8k",  # Invalid quality
            "background_color": "black"  # Invalid color format
        },
        "output_variable": "invalid_draft"
    }
    
    print("Invalid Create Draft Parameters:")
    print(json.dumps(invalid_create, ensure_ascii=False, indent=2))
    
    print("\nExpected Error Output:")
    error_output = {
        "draft_id": "",
        "success": False,
        "message": "参数验证失败: Invalid dimensions: -1x1080"
    }
    print(json.dumps(error_output, ensure_ascii=False, indent=2))
    
    # Invalid export example
    invalid_export = {
        "tool": "export_drafts",
        "input": {
            "draft_ids": "not-a-valid-uuid",
            "remove_temp_files": False
        },
        "output_variable": "invalid_export"
    }
    
    print("\nInvalid Export Parameters:")
    print(json.dumps(invalid_export, ensure_ascii=False, indent=2))
    
    print("\nExpected Error Output:")
    export_error = {
        "draft_data": "",
        "exported_count": 0,
        "success": False,
        "message": "无效的UUID格式: not-a-valid-uuid"
    }
    print(json.dumps(export_error, ensure_ascii=False, indent=2))


def example_complete_workflow():
    """Example: Complete workflow from creation to export"""
    print("\n=== Example 6: Complete Workflow Integration ===")
    
    complete_workflow = {
        "workflow_name": "完整视频制作流程",
        "description": "从创建草稿到最终导出的完整工作流",
        "steps": [
            {
                "step": 1,
                "name": "创建项目草稿",
                "tool": "create_draft",
                "input": {
                    "project_name": "{{user_input.project_name}}",
                    "width": "{{user_input.resolution.width}}",
                    "height": "{{user_input.resolution.height}}",
                    "fps": 30,
                    "video_quality": "1080p",
                    "audio_quality": "320k"
                },
                "output_variable": "project_draft"
            },
            {
                "step": 2,
                "name": "添加视频内容",
                "tool": "add_video_track",
                "input": {
                    "draft_id": "{{project_draft.draft_id}}",
                    "video_urls": "{{user_input.video_list}}",
                    "filters": "{{user_input.video_filters}}"
                },
                "output_variable": "video_added"
            },
            {
                "step": 3,
                "name": "添加音频背景",
                "tool": "add_audio_track",
                "input": {
                    "draft_id": "{{project_draft.draft_id}}",
                    "audio_urls": "{{user_input.background_music}}",
                    "volume": 0.3
                },
                "output_variable": "audio_added"
            },
            {
                "step": 4,
                "name": "添加字幕文本",
                "tool": "add_text_track",
                "input": {
                    "draft_id": "{{project_draft.draft_id}}",
                    "subtitles": "{{user_input.subtitle_list}}",
                    "style": "{{user_input.text_style}}"
                },
                "output_variable": "text_added"
            },
            {
                "step": 5,
                "name": "导出最终草稿",
                "tool": "export_drafts",
                "input": {
                    "draft_ids": "{{project_draft.draft_id}}",
                    "remove_temp_files": True
                },
                "output_variable": "final_draft"
            }
        ]
    }
    
    print("Complete Workflow Configuration:")
    print(json.dumps(complete_workflow, ensure_ascii=False, indent=2))
    
    print("\nUsage in Coze:")
    print("1. 用户提供项目名称、分辨率、视频列表、音频、字幕等")
    print("2. 工作流自动创建草稿并添加所有内容")
    print("3. 最终导出标准化JSON数据供草稿生成器使用")
    print("4. 自动清理临时文件，释放存储空间")


def example_data_structure():
    """Example: Understanding the exported data structure"""
    print("\n=== Example 7: Exported Data Structure ===")
    
    sample_exported_data = {
        "format_version": "1.0",
        "export_type": "single_draft",
        "draft_count": 1,
        "drafts": [
            {
                "draft_id": "123e4567-e89b-12d3-a456-426614174000",
                "project": {
                    "name": "示例项目",
                    "width": 1920,
                    "height": 1080,
                    "fps": 30,
                    "video_quality": "1080p",
                    "audio_quality": "320k",
                    "background_color": "#000000"
                },
                "media_resources": [
                    {
                        "url": "https://example.com/video1.mp4",
                        "resource_type": "video",
                        "duration_ms": 30000,
                        "format": "mp4"
                    },
                    {
                        "url": "https://example.com/audio1.mp3", 
                        "resource_type": "audio",
                        "duration_ms": 45000,
                        "format": "mp3"
                    }
                ],
                "tracks": [
                    {
                        "track_type": "video",
                        "muted": False,
                        "volume": 1.0,
                        "segments": [
                            {
                                "type": "video",
                                "material_url": "https://example.com/video1.mp4",
                                "time_range": {"start": 0, "end": 30000},
                                "transform": {
                                    "position_x": 0.0,
                                    "position_y": 0.0,
                                    "scale_x": 1.0,
                                    "scale_y": 1.0,
                                    "rotation": 0.0,
                                    "opacity": 1.0
                                },
                                "effects": {
                                    "filter_type": "暖冬",
                                    "filter_intensity": 0.8,
                                    "transition_type": "淡化",
                                    "transition_duration": 1000
                                }
                            }
                        ]
                    },
                    {
                        "track_type": "text",
                        "muted": False,
                        "volume": 1.0,
                        "segments": [
                            {
                                "type": "text",
                                "content": "欢迎使用Coze剪映助手",
                                "time_range": {"start": 5000, "end": 10000},
                                "style": {
                                    "font_family": "思源黑体",
                                    "font_size": 48,
                                    "color": "#FFFFFF"
                                }
                            }
                        ]
                    }
                ],
                "total_duration_ms": 30000,
                "created_timestamp": 1703123456.789,
                "last_modified": 1703123456.789,
                "status": "created"
            }
        ]
    }
    
    print("Sample Exported Data Structure:")
    print(json.dumps(sample_exported_data, ensure_ascii=False, indent=2))
    
    print("\nKey Features:")
    print("- 完整的项目配置信息")
    print("- 所有媒体资源的URL和元数据")
    print("- 详细的轨道和片段配置")
    print("- 支持视频变换、滤镜、转场效果")
    print("- 文本样式和动画配置")
    print("- 时间轴和关键帧信息")


if __name__ == "__main__":
    print("Coze Draft Management Workflow Examples")
    print("=" * 50)
    
    example_basic_workflow()
    example_4k_project()
    example_mobile_video()
    example_batch_export()
    example_error_handling()
    example_complete_workflow()
    example_data_structure()
    
    print("\n" + "=" * 50)
    print("Examples completed. Use these patterns in your Coze workflows!")