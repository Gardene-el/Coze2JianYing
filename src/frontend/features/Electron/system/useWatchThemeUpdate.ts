import { useTheme } from "antd-style";
import { useEffect } from "react";

const isDesktop = typeof window !== "undefined" && !!window.electron;

/**
 * Watches antd-style's dark-mode token and forwards theme changes to the
 * Electron main process via the IPC bridge so that the native titlebar
 * overlay controls (Windows) and the window shadow (macOS) stay in sync.
 *
 * Mirrors lobehub/src/features/Electron/system/useWatchThemeUpdate.ts
 * without next-themes / electron-client-ipc dependencies.
 */
export const useWatchThemeUpdate = () => {
  const { isDarkMode } = useTheme();

  useEffect(() => {
    if (!isDesktop) return;
    const themeMode = isDarkMode ? "dark" : "light";
    window.electronAPI
      ?.invoke("system.updateThemeModeHandler", themeMode)
      .catch(() => {
        // Ignore — running in non-electron or IPC not yet ready.
      });
  }, [isDarkMode]);
};
