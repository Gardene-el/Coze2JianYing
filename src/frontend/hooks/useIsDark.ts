/**
 * 直接移植自 lobehub/src/hooks/useIsDark.ts
 * 改用 next-themes resolvedTheme 取代 antd-style isDarkMode，对齐 lobehub 实现。
 */
import { useTheme as useNextThemesTheme } from "next-themes";

export const useIsDark = (): boolean => {
  const { resolvedTheme } = useNextThemesTheme();
  return resolvedTheme === "dark";
};
