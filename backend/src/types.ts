// ============================================================
// 环境变量与共享类型
// ============================================================

export interface Env {
  /** D1 数据库绑定 */
  DB: D1Database;
  /** 可选：若设置，所有请求必须携带 Authorization: Bearer <RELAY_SECRET> */
  RELAY_SECRET?: string;
  /** 录制 TTL（秒），超时记录可被清理，默认 604800 (7天) */
  RECORD_TTL_SECONDS?: string;
  /** 允许的 CORS 来源，逗号分隔 */
  CORS_ORIGINS?: string;
}

/** D1 中 recorded_calls 表的行结构 */
export interface RecordedCall {
  id: string;
  action: string;
  method: string;
  path: string;
  payload_json: string | null;
  owner_draft_id: string | null;
  owner_segment_id: string | null;
  produced_virtual_id: string | null;
  produced_id_type: string | null; // 'draft' | 'segment'
  created_at: number;
}

/** D1 中 draft_segment_assoc 表的行结构 */
export interface DraftSegmentAssoc {
  virtual_draft_id: string;
  virtual_segment_id: string;
}

// 响应工厂已移至 middleware/response.ts
