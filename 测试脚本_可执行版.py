# 测试脚本 - 修正版本（带引号）
# 这是一个用于测试脚本执行器的示例脚本

# API 调用: create_draft
# 构造 request 对象
req_f71ad170 = CreateDraftRequest(draft_name="demo", width=1920, height=1080, fps=30)

resp_f71ad170 = await create_draft(req_f71ad170)

draft_f71ad170 = resp_f71ad170.draft_id

print(f"✓ Created draft: {draft_f71ad170}")


# API 调用: add_track (音频轨道)
req_audio = AddTrackRequest(track_type="audio", track_name=None)
resp_audio = await add_track(draft_f71ad170, req_audio)
print(f"✓ Added audio track")


# API 调用: add_track (视频轨道)
req_video = AddTrackRequest(track_type="video", track_name=None)
resp_video = await add_track(draft_f71ad170, req_video)
print(f"✓ Added video track")


# API 调用: create_audio_segment
req_segment = CreateAudioSegmentRequest(
    material_url="https://gardene-el.github.io/Coze2JianYing/assets/audio.mp3",
    target_timerange=TimeRange(start=0, duration=5000000),
    source_timerange=None,
    speed=1,
    volume=1,
    change_pitch=False
)

resp_segment = await create_audio_segment(req_segment)
segment_id = resp_segment.segment_id
print(f"✓ Created audio segment: {segment_id}")


# API 调用: add_segment
req_add = AddSegmentToDraftRequest(segment_id=segment_id, track_index=None)
resp_add = await add_segment(draft_f71ad170, req_add)
print(f"✓ Added segment to draft")


# API 调用: save_draft
resp_save = await save_draft(draft_f71ad170)
print(f"✓ Draft saved successfully!")
print(f"\n完成！草稿 ID: {draft_f71ad170}")
