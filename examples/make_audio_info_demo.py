#!/usr/bin/env python3
"""
Demo for make_audio_info tool

Demonstrates how to use the make_audio_info tool to generate audio configuration strings
that can be used with add_audios.
"""

import os
import sys
import json

# Add project path
sys.path.append('/home/runner/work/CozeJianYingAssistent/CozeJianYingAssistent')


def demo_make_audio_info():
    """Demonstrate the make_audio_info tool functionality"""
    
    print("=" * 70)
    print("MAKE AUDIO INFO TOOL DEMO")
    print("=" * 70)
    
    # Mock the runtime module
    import types
    from typing import Generic, TypeVar
    
    T = TypeVar('T')
    
    class MockArgsType(Generic[T]):
        pass
    
    runtime_mock = types.ModuleType('runtime')
    runtime_mock.Args = MockArgsType
    sys.modules['runtime'] = runtime_mock
    
    from tools.make_audio_info.handler import handler, Input
    
    # Mock Args class
    class MockArgs:
        def __init__(self, input_data):
            self.input = input_data
            self.logger = None
    
    # Example 1: Basic background music
    print("\n" + "=" * 70)
    print("Example 1: Background Music (BGM)")
    print("=" * 70)
    
    bgm_input = Input(
        audio_url="https://example.com/background_music.mp3",
        start=0,
        end=60000,  # 60 seconds
        volume=0.3,  # Lower volume for background
        fade_in=2000,  # 2 second fade in
        fade_out=3000  # 3 second fade out
    )
    
    result = handler(MockArgs(bgm_input))
    print(f"\nStatus: {result["message"]}")
    print(f"Generated JSON string:")
    print(result["audio_info_string"])
    
    # Parse and display nicely
    parsed = json.loads(result["audio_info_string"])
    print(f"\nParsed configuration:")
    print(json.dumps(parsed, indent=2, ensure_ascii=False))
    
    # Example 2: Narration/Voice-over
    print("\n" + "=" * 70)
    print("Example 2: Narration/Voice-over")
    print("=" * 70)
    
    narration_input = Input(
        audio_url="https://example.com/narration.mp3",
        start=5000,  # Start at 5 seconds
        end=55000,   # End at 55 seconds
        volume=1.0   # Full volume for narration
    )
    
    result = handler(MockArgs(narration_input))
    print(f"\nStatus: {result["message"]}")
    print(f"Generated JSON string:")
    print(result["audio_info_string"])
    
    # Example 3: Audio with effects
    print("\n" + "=" * 70)
    print("Example 3: Audio with Voice Effect")
    print("=" * 70)
    
    effect_input = Input(
        audio_url="https://example.com/voice_with_effect.mp3",
        start=10000,
        end=30000,
        volume=0.9,
        effect_type="变声",  # Voice change effect
        effect_intensity=0.8,
        speed=1.2  # 20% faster
    )
    
    result = handler(MockArgs(effect_input))
    print(f"\nStatus: {result["message"]}")
    print(f"Generated JSON string:")
    print(result["audio_info_string"])
    
    parsed = json.loads(result["audio_info_string"])
    print(f"\nParsed configuration:")
    print(json.dumps(parsed, indent=2, ensure_ascii=False))
    
    # Example 4: Trimmed audio (using material_range)
    print("\n" + "=" * 70)
    print("Example 4: Trimmed Audio Segment")
    print("=" * 70)
    print("Using a specific portion of a longer audio file")
    
    trimmed_input = Input(
        audio_url="https://example.com/long_song.mp3",
        start=0,
        end=20000,  # Display for 20 seconds on timeline
        material_start=45000,  # Start from 45 seconds of the audio file
        material_end=65000,    # End at 65 seconds of the audio file
        volume=0.5,
        fade_in=1000,
        fade_out=1000
    )
    
    result = handler(MockArgs(trimmed_input))
    print(f"\nStatus: {result["message"]}")
    print(f"Generated JSON string:")
    print(result["audio_info_string"])
    
    parsed = json.loads(result["audio_info_string"])
    print(f"\nParsed configuration:")
    print(json.dumps(parsed, indent=2, ensure_ascii=False))
    print(f"\nNote: This uses seconds 45-65 from the original audio file,")
    print(f"      but displays at timeline position 0-20 seconds")
    
    # Example 5: Sound effect
    print("\n" + "=" * 70)
    print("Example 5: Short Sound Effect")
    print("=" * 70)
    
    sfx_input = Input(
        audio_url="https://example.com/notification.mp3",
        start=15000,
        end=15500,  # Very short duration (0.5 seconds)
        volume=0.8
    )
    
    result = handler(MockArgs(sfx_input))
    print(f"\nStatus: {result["message"]}")
    print(f"Generated JSON string:")
    print(result["audio_info_string"])
    
    # Example 6: Collecting multiple audio configs
    print("\n" + "=" * 70)
    print("Example 6: Creating Multiple Audio Configs for Workflow")
    print("=" * 70)
    print("This demonstrates how to prepare audio configs for add_audios")
    
    # Create multiple audio configs
    audio_configs = []
    
    # Background music
    result1 = handler(MockArgs(Input(
        audio_url="https://example.com/bgm.mp3",
        start=0,
        end=60000,
        volume=0.3,
        fade_in=2000
    )))
    audio_configs.append(result1["audio_info_string"])
    
    # Narration
    result2 = handler(MockArgs(Input(
        audio_url="https://example.com/narration.mp3",
        start=5000,
        end=55000,
        volume=1.0
    )))
    audio_configs.append(result2["audio_info_string"])
    
    # Sound effect
    result3 = handler(MockArgs(Input(
        audio_url="https://example.com/effect.mp3",
        start=20000,
        end=20500,
        volume=0.9
    )))
    audio_configs.append(result3["audio_info_string"])
    
    print(f"\nCreated {len(audio_configs)} audio configuration strings:")
    for i, config in enumerate(audio_configs, 1):
        print(f"\nAudio {i}:")
        print(f"  {config}")
    
    print(f"\nThese can now be passed as an array to add_audios:")
    print(f"  audio_infos = {json.dumps(audio_configs, indent=4, ensure_ascii=False)}")
    
    # Example 7: Default values demonstration
    print("\n" + "=" * 70)
    print("Example 7: Understanding Default Values")
    print("=" * 70)
    print("Default values are NOT included in the output to keep it compact")
    
    minimal_input = Input(
        audio_url="https://example.com/audio.mp3",
        start=0,
        end=10000,
        volume=1.0,  # Default value
        fade_in=0,   # Default value
        speed=1.0    # Default value
    )
    
    result = handler(MockArgs(minimal_input))
    print(f"\nInput has volume=1.0, fade_in=0, speed=1.0 (all defaults)")
    print(f"Generated JSON string:")
    print(result["audio_info_string"])
    print(f"\nNotice: Only required fields are included!")
    
    parsed = json.loads(result["audio_info_string"])
    print(f"\nParsed configuration:")
    print(json.dumps(parsed, indent=2, ensure_ascii=False))
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("""
The make_audio_info tool helps you:
1. Generate compact JSON strings for audio configurations
2. Include only non-default parameters to save space
3. Prepare data for use with the add_audios tool
4. Handle various audio scenarios: BGM, narration, effects, etc.

Common workflow:
1. Call make_audio_info multiple times to create different audio configs
2. Collect the returned JSON strings into an array
3. Pass the array to add_audios to add all audios to your draft

Key parameters:
- Required: audio_url, start, end
- Volume control: volume (0.0-2.0)
- Fade effects: fade_in, fade_out (milliseconds)
- Audio effects: effect_type, effect_intensity
- Speed control: speed (0.5-2.0)
- Trimming: material_start, material_end
    """)


if __name__ == "__main__":
    try:
        demo_make_audio_info()
        print("\n✅ Demo completed successfully!")
    except Exception as e:
        print(f"\n❌ Demo failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
