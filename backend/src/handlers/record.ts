import { errorResponse, successResponse } from "../middleware/response";
import type { Env, RecordedCall } from "../types";

// ============================================================
// 静态路径常量
// ============================================================

/** 产生 draft_id 的路径（create_draft） */
const CREATE_DRAFT_PATH = "/drafts/create_draft";

/** 产生 segment_id 的路径（create_*_segment） */
const CREATE_SEGMENT_PATHS = new Set([
  "/segments/create_video_segment",
  "/segments/create_audio_segment",
  "/segments/create_text_segment",
  "/segments/create_sticker_segment",
]);

/** basic API 中 /segments/{segment_id}/add_* 的动作 */
const BASIC_SEGMENT_ADD_ACTIONS = new Set([
  "add_audio_effect",
  "add_audio_fade",
  "add_audio_keyframe",
  "add_sticker_keyframe",
  "add_text_animation",
  "add_text_bubble",
  "add_text_effect",
  "add_text_keyframe",
  "add_video_animation",
  "add_video_background_filling",
  "add_video_effect",
  "add_video_fade",
  "add_video_filter",
  "add_video_keyframe",
  "add_video_mask",
  "add_video_transition",
]);

/** basic API 中 /drafts/{draft_id}/* 的其他动作 */
const BASIC_DRAFT_ACTIONS = new Set([
  "save_draft",
  "add_track",
  "add_effect",
  "add_filter",
]);

/** easy API 中 /drafts/{draft_id}/* 且直接返回空对象的动作 */
const EASY_DRAFT_EMPTY_ACTIONS = new Set(["add_masks", "add_keyframes"]);

/** 路径最后一段即为 action 名 */
function actionFromPath(pathname: string): string {
  const parts = pathname.split("/").filter(Boolean);
  return parts[parts.length - 1];
}

/** 生成带毫秒时间戳前缀的唯一 ID：<ms>-<uuid> */
function genUniqueId(): string {
  return `${Date.now()}-${crypto.randomUUID()}`;
}

/** 向 D1 插入一条调用记录 */
async function insertCall(
  db: D1Database,
  params: Omit<RecordedCall, "method">,
): Promise<void> {
  await db
    .prepare(
      `INSERT INTO recorded_calls (
        id,
        action,
        method,
        path,
        payload_json,
        owner_draft_id,
        owner_segment_id,
        produced_virtual_id,
        produced_id_type,
        created_at
      )
       VALUES (?, ?, 'POST', ?, ?, ?, ?, ?, ?, ?)`,
    )
    .bind(
      params.id,
      params.action,
      params.path,
      params.payload_json,
      params.owner_draft_id,
      params.owner_segment_id,
      params.produced_virtual_id,
      params.produced_id_type,
      params.created_at,
    )
    .run();
}

// ============================================================
// 主入口
// ============================================================

export async function handleRecord(
  request: Request,
  env: Env,
): Promise<Response> {
  const url = new URL(request.url);
  const pathname = url.pathname;
  const action = actionFromPath(pathname);
  const callId = crypto.randomUUID();
  const now = Date.now();

  // 读取原始 body（只读一次）
  const rawBody = await request.text();
  const payload = rawBody.length > 0 ? rawBody : null;

  // ── 1. create_draft ───────────────────────────────────────
  //    无前置依赖，产生 virtual draft_id 并立即返回
  if (pathname === CREATE_DRAFT_PATH) {
    const virtualDraftId = genUniqueId();
    await insertCall(db(env), {
      id: callId,
      action,
      path: pathname,
      payload_json: payload,
      owner_draft_id: virtualDraftId,
      owner_segment_id: null,
      produced_virtual_id: virtualDraftId,
      produced_id_type: "draft",
      created_at: now,
    });
    return successResponse({ draft_id: virtualDraftId }, request, env);
  }

  // ── 2. create_*_segment ───────────────────────────────────
  //    无前置依赖，产生 virtual segment_id 并立即返回
  if (CREATE_SEGMENT_PATHS.has(pathname)) {
    const virtualSegId = genUniqueId();
    await insertCall(db(env), {
      id: callId,
      action,
      path: pathname,
      payload_json: payload,
      owner_draft_id: null,
      owner_segment_id: virtualSegId,
      produced_virtual_id: virtualSegId,
      produced_id_type: "segment",
      created_at: now,
    });
    return successResponse({ segment_id: virtualSegId }, request, env);
  }

  // ── 3. /drafts/{draft_id}/add_segment ─────────────────────
  //    关键：同时写入 assoc 表，建立 draft ↔ segment 关联
  const addSegmentMatch = pathname.match(/^\/drafts\/([^/]+)\/add_segment$/);
  if (addSegmentMatch) {
    const virtualDraftId = addSegmentMatch[1];
    if (!payload) {
      return errorResponse(
        "Missing request body for add_segment",
        400,
        4001,
        request,
        env,
      );
    }

    let body: Record<string, unknown>;
    try {
      body = JSON.parse(payload) as Record<string, unknown>;
    } catch {
      return errorResponse(
        "Invalid JSON body for add_segment",
        400,
        4002,
        request,
        env,
      );
    }

    const virtualSegId =
      typeof body.segment_id === "string" ? body.segment_id : null;
    if (!virtualSegId) {
      return errorResponse(
        "Missing segment_id in add_segment body",
        400,
        4003,
        request,
        env,
      );
    }

    // 记录调用
    await insertCall(db(env), {
      id: callId,
      action,
      path: pathname,
      payload_json: payload,
      owner_draft_id: virtualDraftId,
      owner_segment_id: null,
      produced_virtual_id: null,
      produced_id_type: null,
      created_at: now,
    });

    // 写入关联关系
    await env.DB.prepare(
      `INSERT OR IGNORE INTO draft_segment_assoc (virtual_draft_id, virtual_segment_id)
       VALUES (?, ?)`,
    )
      .bind(virtualDraftId, virtualSegId)
      .run();

    return successResponse({}, request, env);
  }

  // ── 4. Basic API: /drafts/{draft_id}/* ────────────────────
  //    补齐 basic 中除 add_segment 外的 draft 级动作。
  const basicDraftActionMatch = pathname.match(/^\/drafts\/([^/]+)\/([^/]+)$/);
  if (
    basicDraftActionMatch &&
    BASIC_DRAFT_ACTIONS.has(basicDraftActionMatch[2])
  ) {
    await insertCall(db(env), {
      id: callId,
      action,
      path: pathname,
      payload_json: payload,
      owner_draft_id: basicDraftActionMatch[1],
      owner_segment_id: null,
      produced_virtual_id: null,
      produced_id_type: null,
      created_at: now,
    });
    return successResponse({}, request, env);
  }

  // ── 5. Basic API: /segments/{segment_id}/add_* ────────────
  //    仅针对 basic 中的 segment 级 add 动作，直接记录并返回空成功。
  const basicSegmentAddMatch = pathname.match(/^\/segments\/([^/]+)\/([^/]+)$/);
  if (
    basicSegmentAddMatch &&
    BASIC_SEGMENT_ADD_ACTIONS.has(basicSegmentAddMatch[2])
  ) {
    await insertCall(db(env), {
      id: callId,
      action,
      path: pathname,
      payload_json: payload,
      owner_draft_id: null,
      owner_segment_id: basicSegmentAddMatch[1],
      produced_virtual_id: null,
      produced_id_type: null,
      created_at: now,
    });
    return successResponse({}, request, env);
  }

  // ── 6. Easy API (draft-based): /drafts/{draft_id}/add_masks|add_keyframes ─
  //    这两个动作以路径中的 draft_id 为锚点，行为上与 add_effect 类似。
  const easyDraftEmptyActionMatch = pathname.match(
    /^\/drafts\/([^/]+)\/([^/]+)$/,
  );
  if (
    easyDraftEmptyActionMatch &&
    EASY_DRAFT_EMPTY_ACTIONS.has(easyDraftEmptyActionMatch[2])
  ) {
    await insertCall(db(env), {
      id: callId,
      action,
      path: pathname,
      payload_json: payload,
      owner_draft_id: easyDraftEmptyActionMatch[1],
      owner_segment_id: null,
      produced_virtual_id: null,
      produced_id_type: null,
      created_at: now,
    });
    return successResponse({}, request, env);
  }

  // ── 7. Easy API (draft-based): /drafts/{draft_id}/add_videos 等 ─
  //    路径形如 /drafts/{id}/add_*，通过 action 名识别。
  //    add_masks 和 add_keyframes 已在上一分支按 draft 锚点处理。
  const EASY_DRAFT_ACTIONS: Record<
    string,
    (b: Record<string, unknown>) => Record<string, unknown>
  > = {
    add_videos: (b) => ({ segment_ids: genIds(arrayLen(b.video_infos)) }),
    add_audios: (b) => ({ segment_ids: genIds(arrayLen(b.audio_infos)) }),
    add_captions: (b) => ({
      segment_ids: genIds(arrayLen(b.captions)),
    }),
    add_images: (b) => ({
      segment_ids: genIds(arrayLen(b.image_infos)),
    }),
    add_effects: (b) => ({ segment_ids: genIds(arrayLen(b.effect_infos)) }),
  };
  const easyDraftActionMatch = pathname.match(/^\/drafts\/([^/]+)\/([^/]+)$/);
  if (easyDraftActionMatch && action in EASY_DRAFT_ACTIONS) {
    // 先解析 body，计算实际数量
    let body: Record<string, unknown> = {};
    try {
      body = JSON.parse(payload ?? "{}") as Record<string, unknown>;
    } catch {
      /* ignore */
    }
    const responseData = EASY_DRAFT_ACTIONS[action](body);
    const segIds: string[] = Array.isArray(responseData.segment_ids)
      ? (responseData.segment_ids as string[])
      : [];

    // 1. 记录 easy API 调用本身
    await insertCall(db(env), {
      id: callId,
      action,
      path: pathname,
      payload_json: payload,
      owner_draft_id: easyDraftActionMatch[1],
      owner_segment_id: null,
      produced_virtual_id: null,
      produced_id_type: null,
      created_at: now,
    });

    // 2. 提取 draft_id（路径形如 /drafts/{draft_id}/add_*）
    const virtualDraftId = easyDraftActionMatch[1];

    // 3. 为每个虚拟 segment_id 建立记录 + assoc，使回放能追踪到它们
    if (virtualDraftId && segIds.length > 0) {
      const batchInserts = segIds.map((segId) =>
        db(env)
          .prepare(
            `INSERT INTO recorded_calls (
               id,
               action,
               method,
               path,
               payload_json,
               owner_draft_id,
               owner_segment_id,
               produced_virtual_id,
               produced_id_type,
               created_at
             )
             VALUES (?, ?, 'POST', ?, ?, ?, ?, ?, ?, ?)`,
          )
          .bind(
            crypto.randomUUID(),
            `easy_${action}_segment`,
            pathname,
            null,
            null,
            segId,
            segId,
            "segment",
            now,
          ),
      );
      const assocInserts = segIds.map((segId) =>
        db(env)
          .prepare(
            `INSERT OR IGNORE INTO draft_segment_assoc (virtual_draft_id, virtual_segment_id)
             VALUES (?, ?)`,
          )
          .bind(virtualDraftId, segId),
      );
      await db(env).batch([...batchInserts, ...assocInserts]);
    }

    return successResponse(responseData, request, env);
  }

  return errorResponse(
    `Unsupported path: ${pathname}`,
    400,
    4004,
    request,
    env,
  );
}

// ── 辅助函数 ──────────────────────────────────────────────────

function db(env: Env): D1Database {
  return env.DB;
}

function arrayLen(value: unknown): number {
  if (Array.isArray(value)) return value.length;
  if (typeof value === "string") {
    try {
      const parsed: unknown = JSON.parse(value);
      if (Array.isArray(parsed)) return parsed.length;
    } catch {
      /* ignore */
    }
  }
  return 1;
}

function genIds(count: number): string[] {
  return Array.from({ length: count }, () => genUniqueId());
}
