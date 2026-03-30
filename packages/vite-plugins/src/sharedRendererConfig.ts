import react from '@vitejs/plugin-react'
import { nodePolyfills } from 'vite-plugin-node-polyfills'
import tsconfigPaths from 'vite-tsconfig-paths'

import { viteEmotionSpeedy } from './emotionSpeedy'
import { viteNodeModuleStub } from './nodeModuleStub'
import { vitePlatformResolve } from './platformResolve'

/**
 * Shared manualChunks — groups leaf-node modules to reduce chunk file count.
 */
function sharedManualChunks(id: string): string | undefined {
  // i18n locale JSON/TS files
  const localeMatch = id.match(/\/locales\/([^/]+)\/([^/.]+)/)
  if (localeMatch) {
    const [, locale] = localeMatch
    if (locale === 'default') return 'i18n-default'
    return `i18n-${locale}`
  }

  if (!id.includes('node_modules')) return

  // Lucide icons
  if (id.includes('lucide-react')) return 'vendor-icons'

  // es-toolkit
  if (id.includes('es-toolkit')) return 'vendor-es-toolkit'

  // emotion (CSS-in-JS runtime)
  if (id.includes('@emotion/')) return 'vendor-emotion'

  // antd / @ant-design
  if (id.includes('antd') || id.includes('@ant-design')) return 'vendor-antd'

  // react ecosystem
  if (id.includes('react-dom') || id.includes('react-router')) return 'vendor-react'
}

export const sharedRollupOutput = {
  chunkFileNames: (chunkInfo: { name: string }) => {
    const { name } = chunkInfo
    if (name.startsWith('i18n-')) return 'i18n/[name]-[hash].js'
    if (name.startsWith('vendor-')) return 'vendor/[name]-[hash].js'
    return 'assets/[name]-[hash].js'
  },
  manualChunks: sharedManualChunks,
}

type Platform = 'web' | 'mobile' | 'desktop'

const _isDev = process.env.NODE_ENV !== 'production'

interface SharedRendererOptions {
  platform: Platform
  tsconfigPaths?: boolean
}

export function sharedRendererPlugins(options: SharedRendererOptions) {
  const defaultTsconfigPaths = options.tsconfigPaths ?? true
  return [
    viteEmotionSpeedy(),
    nodePolyfills({ include: ['buffer'] }),
    viteNodeModuleStub(),
    vitePlatformResolve(options.platform),
    defaultTsconfigPaths && tsconfigPaths({ projects: ['.'] }),
    react(),
  ]
}

export function sharedRendererDefine(options: { isElectron: boolean; isMobile: boolean }) {
  const nextPublicDefine = Object.fromEntries(
    Object.entries(process.env)
      .filter(([key]) => key.toUpperCase().startsWith('NEXT_PUBLIC_'))
      .map(([key, value]) => [`process.env.${key}`, JSON.stringify(value)]),
  )

  return {
    __CI__: process.env.CI === 'true' ? 'true' : 'false',
    __DEV__: process.env.NODE_ENV !== 'production' ? 'true' : 'false',
    __ELECTRON__: JSON.stringify(options.isElectron),
    __MOBILE__: JSON.stringify(options.isMobile),
    ...nextPublicDefine,
    // Keep a safe fallback so generic `process.env` access won't crash in browser runtime.
    'process.env': '{}',
  }
}

/**
 * Optimized deps list for coze2jianying (stripped of lobehub-only packages)
 */
export const sharedOptimizeDeps = {
  include: [
    'react',
    'react-dom',
    'react-dom/client',
    'react-router-dom',
    'antd',
    '@ant-design/icons',
    '@lobehub/ui',
    '@lobehub/ui > @emotion/react',
    'antd-style',
    'zustand',
    'zustand/middleware',
    'axios',
    '@lobechat/electron-client-ipc',
  ],
}
