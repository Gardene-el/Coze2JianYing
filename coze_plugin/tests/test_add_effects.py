#!/usr/bin/env python3
"""
Test for add_effects tool and integration with make_effect_info

Tests:
1. add_effects with array objects
2. add_effects with array of strings
3. Integration: make_effect_info → add_effects
4. Error handling
"""

import os
import json
import uuid
import shutil
import sys
import importlib.util

# Add project path at the beginning to avoid conflicts
sys.path.insert(0, '/home/runner/work/CozeJianYingAssistent/CozeJianYingAssistent')


def load_module(name, path):
    """Load a module using importlib to avoid package conflicts"""
    # Mock runtime module if not already done
    if 'runtime' not in sys.modules:
        import types
        from typing import Generic, TypeVar
        
        T = TypeVar('T')
        
        class MockArgsType(Generic[T]):
            pass
        
        runtime_mock = types.ModuleType('runtime')
        runtime_mock.Args = MockArgsType
        sys.modules['runtime'] = runtime_mock
    
    # Load the module directly
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    
    return module


def setup_test_draft():
    """Create a test draft for testing"""
    create_draft_module = load_module(
        "create_draft_handler",
        "/home/runner/work/CozeJianYingAssistent/CozeJianYingAssistent/tools/create_draft/handler.py"
    )
    
    class MockArgs:
        def __init__(self, input_data):
            self.input = input_data
            self.logger = None
    
    draft_name = f"test_effects_{uuid.uuid4().hex[:8]}"
    input_data = create_draft_module.Input(draft_name=draft_name)
    result = create_draft_module.handler(MockArgs(input_data))
    
    if not result.success:
        raise Exception(f"Failed to create test draft: {result.message}")
    
    return result.draft_id


def test_add_effects_basic():
    """Test basic add_effects functionality"""
    print("=== Testing add_effects basic functionality ===")
    
    add_effects_module = load_module(
        "add_effects_handler",
        "/home/runner/work/CozeJianYingAssistent/CozeJianYingAssistent/tools/add_effects/handler.py"
    )
    handler = add_effects_module.handler
    Input = add_effects_module.Input
    
    class MockArgs:
        def __init__(self, input_data):
            self.input = input_data
            self.logger = None
    
    # Create test draft
    draft_id = setup_test_draft()
    print(f"Created test draft: {draft_id}")
    
    # Test 1: Add effects with array of objects
    print("\nTest 1: Array of objects")
    effect_infos = [
        {
            "effect_type": "模糊",
            "start": 0,
            "end": 3000,
            "intensity": 0.7
        },
        {
            "effect_type": "锐化",
            "start": 3000,
            "end": 6000,
            "intensity": 0.9
        }
    ]
    
    input_data = Input(
        draft_id=draft_id,
        effect_infos=effect_infos
    )
    result = handler(MockArgs(input_data))
    
    assert result.success, f"Should succeed: {result.message}"
    assert len(result.segment_ids) == 2, "Should create 2 segments"
    assert len(result.segment_infos) == 2, "Should return 2 segment infos"
    print(f"✅ Added {len(result.segment_ids)} effects")
    print(f"   Segment IDs: {result.segment_ids}")
    
    # Test 2: Verify draft config
    print("\nTest 2: Verify draft config")
    draft_folder = os.path.join("/tmp", "jianying_assistant", "drafts", draft_id)
    config_file = os.path.join(draft_folder, "draft_config.json")
    
    with open(config_file, 'r', encoding='utf-8') as f:
        draft_config = json.load(f)
    
    assert "tracks" in draft_config, "Draft should have tracks"
    assert len(draft_config["tracks"]) > 0, "Should have at least one track"
    
    # Find effect track
    effect_track = None
    for track in draft_config["tracks"]:
        if track.get("track_type") == "effect":
            effect_track = track
            break
    
    assert effect_track is not None, "Should have an effect track"
    assert len(effect_track["segments"]) == 2, "Effect track should have 2 segments"
    
    # Verify first segment
    segment1 = effect_track["segments"][0]
    assert segment1["effect_type"] == "模糊"
    assert segment1["time_range"]["start"] == 0
    assert segment1["time_range"]["end"] == 3000
    assert segment1["properties"]["intensity"] == 0.7
    
    print(f"✅ Draft config verified")
    print(f"   Track type: {effect_track['track_type']}")
    print(f"   Segments: {len(effect_track['segments'])}")
    
    print("\n✅ All add_effects basic tests passed!")
    return True


def test_add_effects_array_strings():
    """Test add_effects with array of strings"""
    print("\n=== Testing add_effects with array of strings ===")
    
    add_effects_module = load_module(
        "add_effects_handler2",
        "/home/runner/work/CozeJianYingAssistent/CozeJianYingAssistent/tools/add_effects/handler.py"
    )
    handler = add_effects_module.handler
    Input = add_effects_module.Input
    
    class MockArgs:
        def __init__(self, input_data):
            self.input = input_data
            self.logger = None
    
    # Create test draft
    draft_id = setup_test_draft()
    
    # Test: Array of JSON strings
    print("\nTest: Array of JSON strings")
    effect_strings = [
        '{"effect_type":"模糊","start":0,"end":2000,"intensity":0.6}',
        '{"effect_type":"马赛克","start":2000,"end":4000,"position_x":0.5,"position_y":0.5}'
    ]
    
    input_data = Input(
        draft_id=draft_id,
        effect_infos=effect_strings
    )
    result = handler(MockArgs(input_data))
    
    assert result.success, f"Should succeed: {result.message}"
    assert len(result.segment_ids) == 2, "Should create 2 segments"
    print(f"✅ Array of strings works")
    print(f"   Segment IDs: {result.segment_ids}")
    
    print("\n✅ All add_effects array string tests passed!")
    return True


def test_add_effects_integration():
    """Test integration: make_effect_info → add_effects"""
    print("\n=== Testing integration: make_effect_info → add_effects ===")
    
    make_effect_module = load_module(
        "make_effect_info_handler2",
        "/home/runner/work/CozeJianYingAssistent/CozeJianYingAssistent/tools/make_effect_info/handler.py"
    )
    add_effects_module = load_module(
        "add_effects_handler3",
        "/home/runner/work/CozeJianYingAssistent/CozeJianYingAssistent/tools/add_effects/handler.py"
    )
    
    class MockArgs:
        def __init__(self, input_data):
            self.input = input_data
            self.logger = None
    
    # Create test draft
    draft_id = setup_test_draft()
    print(f"Created test draft: {draft_id}")
    
    # Step 1: Generate effect info strings with make_effect_info
    print("\nStep 1: Generate effect info strings")
    
    effect1 = make_effect_module.handler(MockArgs(make_effect_module.Input(
        effect_type="模糊",
        start=0,
        end=3000,
        intensity=0.7
    )))
    assert effect1.success
    print(f"  Effect 1: {effect1.effect_info_string}")
    
    effect2 = make_effect_module.handler(MockArgs(make_effect_module.Input(
        effect_type="锐化",
        start=3000,
        end=6000,
        intensity=0.9
    )))
    assert effect2.success
    print(f"  Effect 2: {effect2.effect_info_string}")
    
    # Step 2: Collect into array
    print("\nStep 2: Collect strings into array")
    effect_infos_array = [
        effect1.effect_info_string,
        effect2.effect_info_string
    ]
    print(f"  Array length: {len(effect_infos_array)}")
    
    # Step 3: Pass to add_effects
    print("\nStep 3: Pass array of strings to add_effects")
    result = add_effects_module.handler(MockArgs(add_effects_module.Input(
        draft_id=draft_id,
        effect_infos=effect_infos_array
    )))
    
    assert result.success, f"Should succeed: {result.message}"
    assert len(result.segment_ids) == 2
    print(f"✅ Successfully added {len(result.segment_ids)} effects")
    print(f"  Segment IDs: {result.segment_ids}")
    
    # Step 4: Verify in draft config
    print("\nStep 4: Verify effect parameters")
    draft_folder = os.path.join("/tmp", "jianying_assistant", "drafts", draft_id)
    config_file = os.path.join(draft_folder, "draft_config.json")
    
    with open(config_file, 'r', encoding='utf-8') as f:
        draft_config = json.load(f)
    
    effect_track = None
    for track in draft_config["tracks"]:
        if track.get("track_type") == "effect":
            effect_track = track
            break
    
    assert effect_track is not None
    segments = effect_track["segments"]
    
    # Verify effect 1
    assert segments[0]["effect_type"] == "模糊"
    assert segments[0]["properties"]["intensity"] == 0.7
    
    # Verify effect 2
    assert segments[1]["effect_type"] == "锐化"
    assert segments[1]["properties"]["intensity"] == 0.9
    
    print(f"✅ All parameters correctly transferred")
    
    print("\n✅ Integration test passed!")
    return True


def test_add_effects_error_handling():
    """Test error handling"""
    print("\n=== Testing add_effects error handling ===")
    
    add_effects_module = load_module(
        "add_effects_handler4",
        "/home/runner/work/CozeJianYingAssistent/CozeJianYingAssistent/tools/add_effects/handler.py"
    )
    handler = add_effects_module.handler
    Input = add_effects_module.Input
    
    class MockArgs:
        def __init__(self, input_data):
            self.input = input_data
            self.logger = None
    
    # Test 1: Invalid draft_id
    print("\nTest 1: Invalid draft_id")
    input_data = Input(
        draft_id="invalid-uuid",
        effect_infos=[{"effect_type": "模糊", "start": 0, "end": 3000}]
    )
    result = handler(MockArgs(input_data))
    
    assert not result.success
    print(f"✅ Invalid draft_id handled: {result.message}")
    
    # Test 2: Non-existent draft
    print("\nTest 2: Non-existent draft")
    input_data = Input(
        draft_id=str(uuid.uuid4()),
        effect_infos=[{"effect_type": "模糊", "start": 0, "end": 3000}]
    )
    result = handler(MockArgs(input_data))
    
    assert not result.success
    print(f"✅ Non-existent draft handled: {result.message}")
    
    # Test 3: Missing required field
    print("\nTest 3: Missing required field")
    draft_id = setup_test_draft()
    input_data = Input(
        draft_id=draft_id,
        effect_infos=[{"start": 0, "end": 3000}]  # Missing effect_type
    )
    result = handler(MockArgs(input_data))
    
    assert not result.success
    print(f"✅ Missing field handled: {result.message}")
    
    # Test 4: Empty effect_infos
    print("\nTest 4: Empty effect_infos")
    input_data = Input(
        draft_id=draft_id,
        effect_infos=[]
    )
    result = handler(MockArgs(input_data))
    
    assert not result.success
    print(f"✅ Empty array handled: {result.message}")
    
    print("\n✅ All error handling tests passed!")
    return True


if __name__ == "__main__":
    print("Starting add_effects and integration tests...\n")
    
    results = []
    
    try:
        results.append(test_add_effects_basic())
        results.append(test_add_effects_array_strings())
        results.append(test_add_effects_integration())
        results.append(test_add_effects_error_handling())
        
        print(f"\n{'='*50}")
        print(f"Test Summary: {sum(results)}/{len(results)} test suites passed")
        print(f"{'='*50}")
        
        if all(results):
            print("\n🎉 All add_effects tests passed!")
            sys.exit(0)
        else:
            print("\n❌ Some tests failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Test execution failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
