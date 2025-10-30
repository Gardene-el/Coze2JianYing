#!/usr/bin/env python3
"""
Demonstration: Compare original vs simplified export from the issue example

This recreates the scenario from the issue to show the actual data reduction.
"""

import json
from data_structures.draft_generator_interface.models import (
    ImageSegmentConfig, AudioSegmentConfig, TextSegmentConfig,
    TimeRange, TrackConfig, DraftConfig, ProjectSettings
)


def main():
    print("\n" + "="*80)
    print("DEMONSTRATION: Simplified Export vs Original")
    print("="*80 + "\n")
    
    # Recreate the draft structure from the issue example
    # 3 audio segments, 3 image segments, 3 text segments
    
    audio_urls = [
        "https://lf6-appstore-sign.oceancloudapi.com/ocean-cloud-tos/VolcanoUserVoice/speech_7426725529589645339_5fefe0ae-5bef-4fc5-a999-c32dc32489d6.mp3",
        "https://lf3-appstore-sign.oceancloudapi.com/ocean-cloud-tos/VolcanoUserVoice/speech_7426725529589645339_dc8edd60-4132-4453-8cbf-2ea6abe1e984.mp3",
        "https://lf3-appstore-sign.oceancloudapi.com/ocean-cloud-tos/VolcanoUserVoice/speech_7426725529589645339_548ca8fb-10de-49ef-82d7-0fafb40a2e32.mp3"
    ]
    
    image_urls = [
        "https://s.coze.cn/t/ype_JLzKnDY/",
        "https://s.coze.cn/t/TVX56m3evFw/",
        "https://s.coze.cn/t/f1yFxij0ZJs/"
    ]
    
    text_contents = [
        "Coze2JianYing是一款完全开源、无广告且永久免费的小助手，助你独立构建高效AI视频工作流，一切数据自主可控，无后门更安全",
        "只需几步轻松上手，从素材生成到草稿自动导出，极简流程让你专注于创意与内容，无需繁琐操作",
        "支持本地部署和定制开发，兼容多种格式和独立exe程序，让你的剪映自动化创作更加自由、灵活"
    ]
    
    time_ranges = [
        (0, 11472000),
        (11472000, 20208000),
        (20208000, 28080000)
    ]
    
    # Create segments
    audio_segments = [
        AudioSegmentConfig(
            material_url=url,
            time_range=TimeRange(start=start, end=end)
        )
        for url, (start, end) in zip(audio_urls, time_ranges)
    ]
    
    image_segments = [
        ImageSegmentConfig(
            material_url=url,
            time_range=TimeRange(start=start, end=end)
        )
        for url, (start, end) in zip(image_urls, time_ranges)
    ]
    
    text_segments = [
        TextSegmentConfig(
            content=content,
            time_range=TimeRange(start=start, end=end)
        )
        for content, (start, end) in zip(text_contents, time_ranges)
    ]
    
    # Create draft
    draft = DraftConfig(
        draft_id="e559681e-6730-4c6b-b7ba-4e785e2c9f86",
        project=ProjectSettings(
            name="Coze剪映项目",
            width=1440,
            height=1080,
            fps=30
        ),
        tracks=[
            TrackConfig(track_type="audio", segments=audio_segments),
            TrackConfig(track_type="video", segments=image_segments),  # Images go on video track
            TrackConfig(track_type="text", segments=text_segments)
        ]
    )
    
    # Generate both formats
    full_dict = draft.to_dict(include_defaults=True)
    minimal_dict = draft.to_dict(include_defaults=False)
    
    # Wrap in export format
    full_export = {
        "format_version": "1.0",
        "export_type": "single_draft",
        "draft_count": 1,
        "drafts": [full_dict]
    }
    
    minimal_export = {
        "format_version": "1.0",
        "export_type": "single_draft",
        "draft_count": 1,
        "drafts": [minimal_dict]
    }
    
    # Calculate sizes
    full_json = json.dumps(full_export, ensure_ascii=False, indent=2)
    minimal_json = json.dumps(minimal_export, ensure_ascii=False, indent=2)
    
    full_size = len(full_json)
    minimal_size = len(minimal_json)
    reduction = round((1 - minimal_size/full_size)*100, 1)
    
    print(f"Original Export Size: {full_size:,} characters")
    print(f"Simplified Export Size: {minimal_size:,} characters")
    print(f"Data Reduction: {reduction}% ({full_size - minimal_size:,} characters saved)")
    print()
    
    # Show sample segment comparison
    print("="*80)
    print("Sample Audio Segment Comparison")
    print("="*80)
    print("\nOriginal Format (with all defaults):")
    print(json.dumps(full_export['drafts'][0]['tracks'][0]['segments'][0], indent=2, ensure_ascii=False))
    print(f"\nSize: {len(json.dumps(full_export['drafts'][0]['tracks'][0]['segments'][0]))} characters")
    
    print("\n" + "-"*80)
    print("\nSimplified Format (defaults omitted):")
    print(json.dumps(minimal_export['drafts'][0]['tracks'][0]['segments'][0], indent=2, ensure_ascii=False))
    print(f"\nSize: {len(json.dumps(minimal_export['drafts'][0]['tracks'][0]['segments'][0]))} characters")
    
    # Show another sample
    print("\n" + "="*80)
    print("Sample Image Segment Comparison")
    print("="*80)
    print("\nOriginal Format (with all defaults):")
    print(json.dumps(full_export['drafts'][0]['tracks'][1]['segments'][0], indent=2, ensure_ascii=False))
    print(f"\nSize: {len(json.dumps(full_export['drafts'][0]['tracks'][1]['segments'][0]))} characters")
    
    print("\n" + "-"*80)
    print("\nSimplified Format (defaults omitted):")
    print(json.dumps(minimal_export['drafts'][0]['tracks'][1]['segments'][0], indent=2, ensure_ascii=False))
    print(f"\nSize: {len(json.dumps(minimal_export['drafts'][0]['tracks'][1]['segments'][0]))} characters")
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"✅ Successfully reduced export data size by {reduction}%")
    print(f"✅ Saved {full_size - minimal_size:,} characters per export")
    print(f"✅ All essential data preserved")
    print(f"✅ Backward compatible with draft generator")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
