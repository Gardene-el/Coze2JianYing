/**
 * Coze2JianYing Relay — Cloudflare Worker 主入口
 *
 * 录制阶段（Coze → Worker）：
 *   POST /drafts/create_draft                     → 返回虚拟 draft_id
 *   POST /segments/create_*_segment               → 返回虚拟 segment_id
 *   POST /drafts/{draft_id}/add_segment           → 记录 + 写 assoc 表
 *   POST /drafts/{draft_id}/*                     → 记录
 *   POST /segments/{segment_id}/*                 → 记录
 *   POST /drafts/{draft_id}/add_*                 → 记录
 *
 * 回放阶段（本地端 → Worker）：
 *   GET  /replay/{virtual_draft_id}               → 返回有序调用日志
 *
 * 辅助：
 *   GET  /pending/{virtual_draft_id}              → 返回未回放的调用条数
 *   GET  /health                                  → 服务健康检查
 */

import { AutoRouter, type IRequest, cors } from "itty-router";
import { handleRecord } from "./handlers/record";
import { handleReplay } from "./handlers/replay";
import { withAuth } from "./middleware/auth";
import { errorResponse, successResponse } from "./middleware/response";
import type { Env } from "./types";

// ── 定期清理 ─────────────────────────────────────────────────
/**
 * 删除 created_at 早于 (now - RECORD_TTL_SECONDS) 的所有调用记录，
 * 同时清理已失去关联对象的 draft_segment_assoc 孤行。
 * 由 Cron Trigger 或 /admin/cleanup 调用。
 */
async function handleCleanup(
  env: Env,
): Promise<{ deleted_calls: number; deleted_assoc: number }> {
  const ttlMs = Number(env.RECORD_TTL_SECONDS ?? 604800) * 1000;
  const cutoff = Date.now() - ttlMs;

  // 1. 删除过期的调用记录
  const callsResult = await env.DB.prepare(
    "DELETE FROM recorded_calls WHERE created_at < ?1",
  )
    .bind(cutoff)
    .run();

  // 2. 删除孤立的 assoc 行（draft 或 segment 任一已被清理）
  const assocResult = await env.DB.prepare(
    `DELETE FROM draft_segment_assoc
     WHERE virtual_draft_id   NOT IN (
       SELECT produced_virtual_id
       FROM recorded_calls
       WHERE produced_virtual_id IS NOT NULL
     )
        OR virtual_segment_id NOT IN (
       SELECT produced_virtual_id
       FROM recorded_calls
       WHERE produced_virtual_id IS NOT NULL
     )`,
  ).run();

  return {
    deleted_calls: callsResult.meta.changes ?? 0,
    deleted_assoc: assocResult.meta.changes ?? 0,
  };
}

const { preflight, corsify } = cors();

// ── 路由 ─────────────────────────────────────────────────────
const router = AutoRouter<IRequest, [Env, ExecutionContext]>({
  before: [preflight, withAuth],
  finally: [corsify],
  catch: (err: unknown) =>
    errorResponse(err instanceof Error ? err.message : "Internal Error", 500),
});

router
  // 健康检查
  .get("/health", (req: IRequest, env: Env) =>
    successResponse({ status: "ok", timestamp: Date.now() }, req, env),
  )

  // 回放：返回指定 draft_id 的全量有序调用日志
  .get("/replay/:draftId", (req: IRequest, env: Env) =>
    handleReplay(req, env, req.params.draftId),
  )

  // 查询：已录制的调用条数
  .get("/pending/:draftId", (req: IRequest, env: Env) =>
    handlePending(req, env, req.params.draftId),
  )

  // 手动触发清理（调试 / 应急用）
  .post("/admin/cleanup", async (_req: IRequest, env: Env) => {
    const result = await handleCleanup(env);
    return successResponse(
      {
        ...result,
        ttl_seconds: Number(env.RECORD_TTL_SECONDS ?? 604800),
      },
      _req,
      env,
    );
  })

  // 录制：所有 Coze → Worker 的 POST 调用
  .post("*", (req: IRequest, env: Env) => handleRecord(req, env));

// ── 导出（fetch + scheduled）────────────────────────────────
export default {
  async fetch(
    request: Request,
    env: Env,
    ctx: ExecutionContext,
  ): Promise<Response> {
    return router.fetch(request, env, ctx);
  },

  // Cron Trigger 回调（wrangler.toml [triggers].crons 配置触发频率）
  async scheduled(
    _controller: ScheduledController,
    env: Env,
    ctx: ExecutionContext,
  ): Promise<void> {
    ctx.waitUntil(
      handleCleanup(env).then((r) =>
        console.log(
          `[cleanup] deleted calls=${r.deleted_calls} assoc=${r.deleted_assoc}`,
        ),
      ),
    );
  },
} satisfies ExportedHandler<Env>;

// ── 辅助 handler ───────────────────────────────────────────

async function handlePending(
  request: Request,
  env: Env,
  virtualDraftId: string,
): Promise<Response> {
  const totalResult = await env.DB.prepare(
    `SELECT COUNT(DISTINCT id) as count
       FROM recorded_calls
      WHERE owner_draft_id = ?1
         OR owner_segment_id IN (
           SELECT virtual_segment_id
             FROM draft_segment_assoc
            WHERE virtual_draft_id = ?1
         )`,
  )
    .bind(virtualDraftId)
    .first<{ count: number }>();

  return successResponse(
    {
      virtual_draft_id: virtualDraftId,
      total_recorded: totalResult?.count ?? 0,
    },
    request,
    env,
  );
}
