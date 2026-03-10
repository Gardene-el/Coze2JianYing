// ============================================================
// 认证中间件 —— 仅 POST 请求需要携带 Bearer token
//
// GET /health /replay /pending 全部公开，无需认证。
// RELAY_SECRET 为空时跳过校验（本地开发用）。
// ============================================================

import type { IRequest } from "itty-router";
import type { Env } from "../types";
import { errorResponse } from "./response";

export function withAuth(req: IRequest, env: Env): Response | undefined {
  if (req.method !== "POST") return;
  if (!env.RELAY_SECRET) return;
  const auth = req.headers.get("Authorization") ?? "";
  if (auth !== `Bearer ${env.RELAY_SECRET}`) {
    return errorResponse("Unauthorized", 401, 401, req, env);
  }
}
