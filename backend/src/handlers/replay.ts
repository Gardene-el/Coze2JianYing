import { errorResponse, successResponse } from "../middleware/response";
import type { Env, RecordedCall } from "../types";

// ============================================================
// Replay handler
// GET /replay/{virtual_draft_id}
//
// 返回该 draft 关联的全量调用日志，按 created_at 升序排列。
// 关联逻辑（精确匹配，不依赖 LIKE 推断）：
//   1. owner_draft_id = draft_id
//   2. draft_segment_assoc 中属于该 draft 的所有 segment
//   3. owner_segment_id IN (segment_ids)
// ============================================================

export async function handleReplay(
  request: Request,
  env: Env,
  virtualDraftId: string,
): Promise<Response> {
  if (!virtualDraftId) {
    return errorResponse("Missing virtual_draft_id", 400, 400, request, env);
  }

  const db = env.DB;

  // ── Step 1：所有 draft 级调用（精确 owner 匹配） ───────────
  const draftResult = await db
    .prepare(
      `SELECT * FROM recorded_calls
       WHERE owner_draft_id = ?1
       ORDER BY created_at ASC`,
    )
    .bind(virtualDraftId)
    .all<RecordedCall>();

  // ── Step 2：找出通过 add_segment 关联的 segment_id ────────
  const assocResult = await db
    .prepare(
      `SELECT virtual_segment_id FROM draft_segment_assoc
       WHERE virtual_draft_id = ?1`,
    )
    .bind(virtualDraftId)
    .all<{ virtual_segment_id: string }>();

  const segmentIds = assocResult.results.map((r) => r.virtual_segment_id);

  // ── Step 3：所有 segment 级别的调用（精确 owner 匹配） ─────
  const segmentCalls: RecordedCall[] = [];

  if (segmentIds.length > 0) {
    // 为避免 D1 单次绑定参数上限（~100），分批处理（每批最多 80 个 segment）
    const BATCH = 80;
    for (let i = 0; i < segmentIds.length; i += BATCH) {
      const batch = segmentIds.slice(i, i + BATCH);
      const placeholders = batch.map(() => "?").join(", ");

      const result = await db
        .prepare(
          `SELECT * FROM recorded_calls
           WHERE owner_segment_id IN (${placeholders})`,
        )
        .bind(...batch)
        .all<RecordedCall>();

      segmentCalls.push(...result.results);
    }
  }

  // ── Step 4：合并去重，按 created_at 升序排列 ──────────────
  const allCalls = [...draftResult.results, ...segmentCalls];
  const unique = dedupe(allCalls);
  unique.sort((a, b) => a.created_at - b.created_at);

  return successResponse(
    {
      virtual_draft_id: virtualDraftId,
      total: unique.length,
      segment_ids: segmentIds,
      calls: unique,
    },
    request,
    env,
  );
}

// ── 工具函数 ──────────────────────────────────────────────────

function dedupe(calls: RecordedCall[]): RecordedCall[] {
  const seen = new Map<string, RecordedCall>();
  for (const c of calls) {
    if (!seen.has(c.id)) seen.set(c.id, c);
  }
  return Array.from(seen.values());
}
