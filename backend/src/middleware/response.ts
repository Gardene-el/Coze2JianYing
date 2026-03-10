// ============================================================
// 响应中间件 —— 统一格式与 Python ResponseMiddleware 对齐
//
// 成功：{ code: 0, message: "ok", ...data }
// 失败：{ code: <非0>, message: "..." }
// 错误默认返回真实 HTTP 状态码，便于网关/监控/重试策略识别。
// ============================================================

import type { Env } from "../types";

const DEFAULT_CORS_ORIGINS = [
  "https://coze.com",
  "https://www.coze.com",
  "https://coze.cn",
  "https://www.coze.cn",
  "http://localhost:3000",
];

function normalizeAllowedOrigins(raw?: string): string[] {
  if (!raw || raw.trim().length === 0) return DEFAULT_CORS_ORIGINS;
  const origins = raw
    .split(",")
    .map((o) => o.trim())
    .filter(Boolean);
  return origins.length > 0 ? origins : DEFAULT_CORS_ORIGINS;
}

function resolveAllowOrigin(request?: Request, env?: Env): string {
  const allowed = normalizeAllowedOrigins(env?.CORS_ORIGINS);
  const origin = request?.headers.get("Origin")?.trim();
  if (!origin) return allowed[0];
  return allowed.includes(origin) ? origin : allowed[0];
}

export function corsHeaders(
  request?: Request,
  env?: Env,
): Record<string, string> {
  return {
    "Access-Control-Allow-Origin": resolveAllowOrigin(request, env),
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
    Vary: "Origin",
  };
}

export const CORS_HEADERS = {
  "Access-Control-Allow-Origin": DEFAULT_CORS_ORIGINS[0],
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization",
  Vary: "Origin",
};

export function successResponse(
  data: Record<string, unknown>,
  request?: Request,
  env?: Env,
): Response {
  return new Response(JSON.stringify({ code: 0, message: "ok", ...data }), {
    status: 200,
    headers: {
      "Content-Type": "application/json",
      ...corsHeaders(request, env),
    },
  });
}

export function errorResponse(
  message: string,
  httpStatus = 500,
  code = 500,
  request?: Request,
  env?: Env,
): Response {
  return new Response(JSON.stringify({ code, message }), {
    status: httpStatus,
    headers: {
      "Content-Type": "application/json",
      ...corsHeaders(request, env),
    },
  });
}
