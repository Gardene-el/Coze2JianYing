/**
 * Stub types for electron-liquid-glass — a macOS Tahoe-only native module.
 * This package is only installed by electron-builder install-app-deps on macOS.
 * On other platforms it uses a dynamic require inside a try-catch, so this stub
 * is sufficient to satisfy the TypeScript compiler.
 */

interface LiquidGlass {
  addView: (windowHandle: Buffer) => number
  removeView: (viewId: number) => void
  unstable_setVariant: (viewId: number, variant: number) => void
}

declare const liquidGlass: LiquidGlass
export default liquidGlass
