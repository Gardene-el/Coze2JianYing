#!/usr/bin/env python3
"""
演示修复后的生成代码行为
展示空 CustomNamespace 对象如何被正确过滤
"""

from types import SimpleNamespace


def _is_meaningful_object(obj) -> bool:
    """
    检查对象是否包含有意义的数据
    """
    if obj is None:
        return False
    
    if hasattr(obj, '__dict__'):
        obj_dict = obj.__dict__
        if not obj_dict:
            return False
        if all(v is None for v in obj_dict.values()):
            return False
        return True
    
    return True


def _to_type_constructor(obj, type_name: str) -> str:
    """
    将 CustomNamespace/SimpleNamespace 对象转换为类型构造表达式字符串
    """
    if obj is None:
        return 'None'
    
    if hasattr(obj, '__dict__'):
        obj_dict = obj.__dict__
        params = []
        for key, value in obj_dict.items():
            if hasattr(value, '__dict__'):
                nested_type_name = key.capitalize() if key else 'Object'
                if 'clip_settings' in key.lower() or key.lower() == 'clipsettings':
                    nested_type_name = 'ClipSettings'
                elif 'crop_settings' in key.lower() or key.lower() == 'cropsettings':
                    nested_type_name = 'CropSettings'
                elif 'timerange' in key.lower():
                    nested_type_name = 'TimeRange'
                elif 'text_style' in key.lower() or key.lower() == 'textstyle':
                    nested_type_name = 'TextStyle'
                value_repr = _to_type_constructor(value, nested_type_name)
            elif isinstance(value, str):
                value_repr = f'"{value}"'
            else:
                value_repr = repr(value)
            params.append(f'{key}={value_repr}')
        
        return f'{type_name}(' + ', '.join(params) + ')'
    
    if isinstance(obj, str):
        return f'"{obj}"'
    else:
        return repr(obj)


def demonstrate_audio_segment_example():
    """演示音频片段创建的代码生成"""
    print("=" * 60)
    print("示例 1: 音频片段创建（修复前会失败的场景）")
    print("=" * 60)
    print()
    
    # 模拟 Coze 传入的参数（包含空的 source_timerange）
    class Input:
        material_url = "https://gardene-el.github.io/Coze2JianYing/assets/audio.mp3"
        target_timerange = SimpleNamespace(start=0, duration=5000000)
        source_timerange = SimpleNamespace()  # 空对象！这是问题根源
        speed = 1
        volume = 0.6
        change_pitch = True
    
    args_input = Input()
    generated_uuid = "591ab9ac_73ee_42f0_97c9_7013a9fa9665"
    
    print("Coze 传入的参数:")
    print(f"  material_url: {args_input.material_url}")
    print(f"  target_timerange: {args_input.target_timerange}")
    print(f"  source_timerange: {args_input.source_timerange} (空对象!)")
    print(f"  speed: {args_input.speed}")
    print(f"  volume: {args_input.volume}")
    print(f"  change_pitch: {args_input.change_pitch}")
    print()
    
    print("修复后生成的代码:")
    print("-" * 60)
    
    # 构造 request 对象（修复后的逻辑）
    req_params = {}
    req_params['material_url'] = args_input.material_url
    req_params['target_timerange'] = _to_type_constructor(args_input.target_timerange, 'TimeRange')
    
    # 关键修复：使用 _is_meaningful_object 检查
    if _is_meaningful_object(args_input.source_timerange):
        req_params['source_timerange'] = _to_type_constructor(args_input.source_timerange, 'TimeRange')
    
    if args_input.speed is not None:
        req_params['speed'] = args_input.speed
    
    if args_input.volume is not None:
        req_params['volume'] = args_input.volume
    
    if args_input.change_pitch is not None:
        req_params['change_pitch'] = args_input.change_pitch
    
    # 生成代码字符串（这是写入 /tmp/coze2jianying.py 的内容）
    code_lines = [
        "# API 调用: create_audio_segment",
        "# 时间: 2025-11-20 04:16:20",
        "",
        "# 构造 request 对象",
        f"req_params_{generated_uuid} = {{}}",
        f"req_params_{generated_uuid}['material_url'] = \"{args_input.material_url}\"",
        f"req_params_{generated_uuid}['target_timerange'] = {req_params['target_timerange']}",
    ]
    
    if 'source_timerange' in req_params:
        code_lines.append(f"req_params_{generated_uuid}['source_timerange'] = {req_params['source_timerange']}")
    
    if 'speed' in req_params:
        code_lines.append(f"req_params_{generated_uuid}['speed'] = {req_params['speed']}")
    
    if 'volume' in req_params:
        code_lines.append(f"req_params_{generated_uuid}['volume'] = {req_params['volume']}")
    
    if 'change_pitch' in req_params:
        code_lines.append(f"req_params_{generated_uuid}['change_pitch'] = {req_params['change_pitch']}")
    
    code_lines.append(f"req_{generated_uuid} = CreateAudioSegmentRequest(**req_params_{generated_uuid})")
    code_lines.append("")
    code_lines.append(f"resp_{generated_uuid} = await create_audio_segment(req_{generated_uuid})")
    code_lines.append("")
    code_lines.append(f"segment_{generated_uuid} = resp_{generated_uuid}.segment_id")
    
    for line in code_lines:
        print(line)
    
    print("-" * 60)
    print()
    
    print("关键点:")
    print(f"  ✅ 空的 source_timerange 被过滤: {'source_timerange' not in req_params}")
    print(f"  ✅ 有效的 target_timerange 被包含: {'target_timerange' in req_params}")
    print(f"  ✅ 其他参数正常包含: {'speed' in req_params and 'volume' in req_params}")
    print()
    
    print("结果:")
    print("  修复前: Pydantic 验证失败 - TimeRange() 缺少必需参数 start 和 duration")
    print("  修复后: 代码正确执行 - 空对象被正确过滤，只包含有效参数")
    print()


def demonstrate_video_segment_example():
    """演示视频片段创建的代码生成"""
    print("=" * 60)
    print("示例 2: 视频片段创建（包含多个复杂类型）")
    print("=" * 60)
    print()
    
    # 模拟 Coze 传入的参数
    class Input:
        material_url = "https://gardene-el.github.io/Coze2JianYing/assets/video.mp4"
        target_timerange = SimpleNamespace(duration=4200000, start=0)
        source_timerange = SimpleNamespace()  # 空对象
        speed = None
        volume = 0.6
        change_pitch = None
        clip_settings = SimpleNamespace()  # 空对象
        crop_settings = SimpleNamespace()  # 空对象
    
    args_input = Input()
    generated_uuid = "8afb9b4f_a9b6_4163_9121_c09682f9dd79"
    
    print("Coze 传入的参数:")
    print(f"  material_url: {args_input.material_url}")
    print(f"  target_timerange: {args_input.target_timerange}")
    print(f"  source_timerange: {args_input.source_timerange} (空)")
    print(f"  speed: {args_input.speed}")
    print(f"  volume: {args_input.volume}")
    print(f"  change_pitch: {args_input.change_pitch}")
    print(f"  clip_settings: {args_input.clip_settings} (空)")
    print(f"  crop_settings: {args_input.crop_settings} (空)")
    print()
    
    print("修复后生成的代码:")
    print("-" * 60)
    
    # 构造 request 对象
    req_params = {}
    req_params['material_url'] = args_input.material_url
    req_params['target_timerange'] = _to_type_constructor(args_input.target_timerange, 'TimeRange')
    
    if _is_meaningful_object(args_input.source_timerange):
        req_params['source_timerange'] = _to_type_constructor(args_input.source_timerange, 'TimeRange')
    
    if args_input.speed is not None:
        req_params['speed'] = args_input.speed
    
    if args_input.volume is not None:
        req_params['volume'] = args_input.volume
    
    if args_input.change_pitch is not None:
        req_params['change_pitch'] = args_input.change_pitch
    
    if _is_meaningful_object(args_input.clip_settings):
        req_params['clip_settings'] = _to_type_constructor(args_input.clip_settings, 'ClipSettings')
    
    if _is_meaningful_object(args_input.crop_settings):
        req_params['crop_settings'] = _to_type_constructor(args_input.crop_settings, 'CropSettings')
    
    # 生成代码字符串
    code_lines = [
        "# API 调用: create_video_segment",
        "# 时间: 2025-11-20 04:16:21",
        "",
        "# 构造 request 对象",
        f"req_params_{generated_uuid} = {{}}",
        f"req_params_{generated_uuid}['material_url'] = \"{args_input.material_url}\"",
        f"req_params_{generated_uuid}['target_timerange'] = {req_params['target_timerange']}",
    ]
    
    if 'source_timerange' in req_params:
        code_lines.append(f"req_params_{generated_uuid}['source_timerange'] = {req_params['source_timerange']}")
    
    if 'speed' in req_params:
        code_lines.append(f"req_params_{generated_uuid}['speed'] = {req_params['speed']}")
    
    if 'volume' in req_params:
        code_lines.append(f"req_params_{generated_uuid}['volume'] = {req_params['volume']}")
    
    if 'change_pitch' in req_params:
        code_lines.append(f"req_params_{generated_uuid}['change_pitch'] = {req_params['change_pitch']}")
    
    if 'clip_settings' in req_params:
        code_lines.append(f"req_params_{generated_uuid}['clip_settings'] = {req_params['clip_settings']}")
    
    if 'crop_settings' in req_params:
        code_lines.append(f"req_params_{generated_uuid}['crop_settings'] = {req_params['crop_settings']}")
    
    code_lines.append(f"req_{generated_uuid} = CreateVideoSegmentRequest(**req_params_{generated_uuid})")
    code_lines.append("")
    code_lines.append(f"resp_{generated_uuid} = await create_video_segment(req_{generated_uuid})")
    code_lines.append("")
    code_lines.append(f"segment_{generated_uuid} = resp_{generated_uuid}.segment_id")
    
    for line in code_lines:
        print(line)
    
    print("-" * 60)
    print()
    
    print("关键点:")
    print(f"  ✅ 空的 source_timerange 被过滤: {'source_timerange' not in req_params}")
    print(f"  ✅ 空的 clip_settings 被过滤: {'clip_settings' not in req_params}")
    print(f"  ✅ 空的 crop_settings 被过滤: {'crop_settings' not in req_params}")
    print(f"  ✅ None 的 speed 被过滤: {'speed' not in req_params}")
    print(f"  ✅ 有效的参数被包含: {'target_timerange' in req_params and 'volume' in req_params}")
    print()


def main():
    """运行所有示例"""
    print()
    demonstrate_audio_segment_example()
    demonstrate_video_segment_example()
    
    print("=" * 60)
    print("总结")
    print("=" * 60)
    print()
    print("修复说明:")
    print("  1. 添加了 _is_meaningful_object() 辅助函数")
    print("  2. 对复杂类型（TimeRange、ClipSettings等）使用该函数检查")
    print("  3. 空的 CustomNamespace 对象会被正确识别并过滤")
    print("  4. 避免了 Pydantic 验证错误")
    print()
    print("核心逻辑:")
    print("  - None 值 → False（不包含）")
    print("  - 空对象 {} → False（不包含）")
    print("  - 所有值为 None 的对象 → False（不包含）")
    print("  - 至少有一个有效值的对象 → True（包含）")
    print()


if __name__ == "__main__":
    main()
