/**
 * Zustand devtools 中间件封装
 * 参考 lobehub/src/store/middleware/devtools.ts 模式
 */
import { devtools as zustandDevtools } from 'zustand/middleware'

export const devtools: typeof zustandDevtools = (fn, options) =>
  zustandDevtools(fn, {
    enabled: import.meta.env.DEV,
    ...options,
  })
