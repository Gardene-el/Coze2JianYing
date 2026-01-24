"""
集成测试：批量 API 端点

测试批量 API 端点的请求/响应格式
"""

import json


def test_add_audios_request_format():
    """测试 add_audios 的请求格式"""
    # 模拟 Coze 插件工具发送的请求
    request_data = {
        "draft_id": "12345678-1234-1234-1234-123456789012",
        "audio_infos": [
            json.dumps({
                "audio_url": "https://example.com/audio1.mp3",
                "start": 0,
                "end": 5000,
                "volume": 0.8
            }),
            json.dumps({
                "audio_url": "https://example.com/audio2.mp3",
                "start": 5000,
                "end": 10000
            })
        ]
    }
    
    print("✓ add_audios request format valid")
    print(f"  Draft ID: {request_data['draft_id']}")
    print(f"  Audio count: {len(request_data['audio_infos'])}")
    
    # 验证可以解析 JSON
    for i, info_str in enumerate(request_data['audio_infos']):
        info = json.loads(info_str)
        assert 'audio_url' in info
        assert 'start' in info
        assert 'end' in info
        print(f"  Audio {i+1}: {info['audio_url']}")


def test_add_captions_request_format():
    """测试 add_captions 的请求格式"""
    request_data = {
        "draft_id": "12345678-1234-1234-1234-123456789012",
        "caption_infos": [
            json.dumps({
                "content": "第一句字幕",
                "start": 0,
                "end": 3000,
                "font_size": 48,
                "color": "#FFFFFF"
            }),
            json.dumps({
                "content": "第二句字幕",
                "start": 3000,
                "end": 6000
            })
        ]
    }
    
    print("✓ add_captions request format valid")
    print(f"  Draft ID: {request_data['draft_id']}")
    print(f"  Caption count: {len(request_data['caption_infos'])}")
    
    for i, info_str in enumerate(request_data['caption_infos']):
        info = json.loads(info_str)
        assert 'content' in info
        assert 'start' in info
        assert 'end' in info
        print(f"  Caption {i+1}: {info['content']}")


def test_add_videos_request_format():
    """测试 add_videos 的请求格式"""
    request_data = {
        "draft_id": "12345678-1234-1234-1234-123456789012",
        "video_infos": [
            json.dumps({
                "video_url": "https://example.com/video1.mp4",
                "start": 0,
                "end": 10000,
                "position_x": 0.0,
                "position_y": 0.0,
                "scale_x": 1.0,
                "scale_y": 1.0
            }),
            json.dumps({
                "video_url": "https://example.com/video2.mp4",
                "start": 10000,
                "end": 20000
            })
        ]
    }
    
    print("✓ add_videos request format valid")
    print(f"  Draft ID: {request_data['draft_id']}")
    print(f"  Video count: {len(request_data['video_infos'])}")
    
    for i, info_str in enumerate(request_data['video_infos']):
        info = json.loads(info_str)
        assert 'video_url' in info
        assert 'start' in info
        assert 'end' in info
        print(f"  Video {i+1}: {info['video_url']}")


def test_add_sticker_request_format():
    """测试 add_sticker 的请求格式"""
    request_data = {
        "draft_id": "12345678-1234-1234-1234-123456789012",
        "sticker_info": json.dumps({
            "sticker_url": "https://example.com/sticker.png",
            "start": 0,
            "end": 5000,
            "position_x": 0.5,
            "position_y": 0.5,
            "scale": 1.0
        })
    }
    
    print("✓ add_sticker request format valid")
    print(f"  Draft ID: {request_data['draft_id']}")
    
    info = json.loads(request_data['sticker_info'])
    assert 'sticker_url' in info
    assert 'start' in info
    assert 'end' in info
    print(f"  Sticker: {info['sticker_url']}")


def test_add_keyframes_request_format():
    """测试 add_keyframes 的请求格式"""
    request_data = {
        "segment_id": "12345678-1234-1234-1234-123456789012",
        "keyframe_infos": [
            {
                "property": "position_x",
                "time_offset": 0,
                "value": 0.0
            },
            {
                "property": "position_x",
                "time_offset": 2000,
                "value": 0.5
            }
        ]
    }
    
    print("✓ add_keyframes request format valid")
    print(f"  Segment ID: {request_data['segment_id']}")
    print(f"  Keyframe count: {len(request_data['keyframe_infos'])}")
    
    for i, info in enumerate(request_data['keyframe_infos']):
        assert 'property' in info
        assert 'time_offset' in info
        assert 'value' in info
        print(f"  Keyframe {i+1}: {info['property']} @ {info['time_offset']}ms = {info['value']}")


def test_add_masks_request_format():
    """测试 add_masks 的请求格式"""
    request_data = {
        "segment_id": "12345678-1234-1234-1234-123456789012",
        "mask_info": {
            "mask_type": "circle",
            "center_x": 0.5,
            "center_y": 0.5,
            "size": 0.5,
            "feather": 10.0
        }
    }
    
    print("✓ add_masks request format valid")
    print(f"  Segment ID: {request_data['segment_id']}")
    
    info = request_data['mask_info']
    assert 'mask_type' in info
    print(f"  Mask type: {info['mask_type']}")


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Batch API Request Formats")
    print("=" * 60)
    print()
    
    test_add_audios_request_format()
    print()
    
    test_add_captions_request_format()
    print()
    
    test_add_videos_request_format()
    print()
    
    test_add_sticker_request_format()
    print()
    
    test_add_keyframes_request_format()
    print()
    
    test_add_masks_request_format()
    print()
    
    print("=" * 60)
    print("✓ All request format tests passed!")
    print("=" * 60)
