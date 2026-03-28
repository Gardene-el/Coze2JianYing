import { useTheme } from 'next-themes'
import { useEffect } from 'react'

const isDesktop = typeof window !== 'undefined' && !!window.electron

/**
 * 监听 next-themes 的主题值变化，将 theme 变更通过 IPC 转发给 Electron 主进程，
 * 使 Windows 原生标题栏控件和 macOS 窗口阴影保持同步。
 *
 * 对齐 lobehub/src/features/Electron/system/useWatchThemeUpdate.ts
 */
export const useWatchThemeUpdate = () => {
  const { theme } = useTheme()

  useEffect(() => {
    if (!isDesktop) return
    if (!theme) return

    window.electronAPI
      ?.invoke('system.updateThemeModeHandler', theme as 'dark' | 'light' | 'system')
      .catch(() => {
        // Ignore — running in non-electron or IPC not yet ready.
      })
  }, [theme])
}
