#!/usr/bin/env python3
"""
Test the add_images tool functionality

Tests the complete workflow of adding image segments to existing drafts,
including input validation, image info parsing, and output format verification.
"""

import os
import json
import uuid
import shutil
import tempfile


def test_add_images_basic():
    """Test basic add_images functionality"""
    print("=== Testing add_images basic functionality ===")
    
    # Import the add_images handler with mock runtime
    import sys
    sys.path.append('/home/runner/work/Coze2JianYing/Coze2JianYing')
    
    # Mock the runtime module
    import types
    from typing import Generic, TypeVar
    
    T = TypeVar('T')
    
    class MockArgsType(Generic[T]):
        pass
    
    runtime_mock = types.ModuleType('runtime')
    runtime_mock.Args = MockArgsType
    sys.modules['runtime'] = runtime_mock
    
    from coze_plugin.tools.add_images.handler import handler, Input, parse_image_infos
    from coze_plugin.tools.create_draft.handler import handler as create_handler, Input as CreateInput
    
    # Create a mock Args class
    class MockArgs:
        def __init__(self, input_data):
            self.input = input_data
            self.logger = None
    
    # Step 1: Create a draft first
    create_input = CreateInput(
        draft_name="测试图片草稿",
        width=1920,
        height=1080,
        fps=30
    )
    
    create_result = create_handler(MockArgs(create_input))
    assert create_result.success, f"Failed to create draft: {create_result.message}"
    draft_id = create_result.draft_id
    print(f"✅ Created test draft: {draft_id}")
    
    # Step 2: Prepare image infos
    image_infos = [
        {
            "image_url": "https://s.coze.cn/t/W9CvmtJHJWI/",
            "start": 0,
            "end": 3936000,
            "width": 1440,
            "height": 1080
        },
        {
            "image_url": "https://s.coze.cn/t/iGLRGx6JvZ0/",
            "start": 3936000,
            "end": 7176000,
            "width": 1440,
            "height": 1080,
            "in_animation": "轻微放大",
            "in_animation_duration": 100000
        }
    ]
    
    image_infos_str_list = [json.dumps(info) for info in image_infos]
    
    # Step 3: Test add_images
    add_input = Input(
        draft_id=draft_id,
        image_infos=image_infos_str_list
    )
    
    result = handler(MockArgs(add_input))
    
    # Verify result
    assert result.success, f"add_images failed: {result.message}"
    assert len(result.segment_ids) == 2, f"Expected 2 segments, got {len(result.segment_ids)}"
    
    print(f"✅ Successfully added {len(result.segment_ids)} images")
    print(f"✅ Segment IDs: {result.segment_ids}")
    
    # Step 4: Verify segment_infos format
