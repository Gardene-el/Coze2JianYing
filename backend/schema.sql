-- ============================================================
-- Coze2JianYing Relay — D1 Schema
-- ============================================================

-- 录制的每一次 API 调用
CREATE TABLE IF NOT EXISTS recorded_calls (
    -- 调用自身的唯一 ID
    id              TEXT PRIMARY KEY,
    -- 接口动作名，如 "create_video_segment"、"add_video_fade"
    action          TEXT NOT NULL,
    -- HTTP 方法
    method          TEXT NOT NULL DEFAULT 'POST',
    -- 请求路径（含虚拟 ID），如 /segments/virt-xxx/add_video_fade
    path            TEXT NOT NULL,
    -- 原始请求 body（JSON 字符串），可能含虚拟 ID
    payload_json    TEXT,
    -- 调用归属：该调用明确属于哪个 draft（精确匹配，不依赖 LIKE）
    owner_draft_id  TEXT,
    -- 调用归属：该调用明确属于哪个 segment（精确匹配，不依赖 LIKE）
    owner_segment_id TEXT,
    -- 若该调用产生了新的虚拟对象，则记录该对象 ID
    produced_virtual_id TEXT,
    -- 产生对象类型：'draft' | 'segment'
    produced_id_type TEXT,
    -- Unix 毫秒时间戳，用于排序
    created_at      INTEGER NOT NULL
);

-- draft ↔ segment 关联关系
-- 由 /drafts/{draft_id}/add_segment 调用写入
CREATE TABLE IF NOT EXISTS draft_segment_assoc (
    virtual_draft_id    TEXT NOT NULL,
    virtual_segment_id  TEXT NOT NULL,
    PRIMARY KEY (virtual_draft_id, virtual_segment_id)
);

-- ── 索引 ────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_calls_path        ON recorded_calls(path);
CREATE INDEX IF NOT EXISTS idx_calls_created_at  ON recorded_calls(created_at);
CREATE INDEX IF NOT EXISTS idx_calls_owner_draft ON recorded_calls(owner_draft_id);
CREATE INDEX IF NOT EXISTS idx_calls_owner_segment ON recorded_calls(owner_segment_id);
CREATE INDEX IF NOT EXISTS idx_calls_produced    ON recorded_calls(produced_id_type, produced_virtual_id);
CREATE INDEX IF NOT EXISTS idx_assoc_draft       ON draft_segment_assoc(virtual_draft_id);
