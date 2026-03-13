/**
 * 全局初始化 — 在 SPA 入口最顶层执行
 * 对应 lobehub/src/initialize.ts
 */

// 确保 Zustand devtools 在开发环境生效
if (import.meta.env.DEV) {
  // @ts-expect-error — 在 window 上挂载供 devtools 识别
  window.__ZUSTAND_DEVTOOLS__ = true;
}
