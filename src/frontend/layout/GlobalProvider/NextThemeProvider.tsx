/**
 * 移植自 lobehub/src/layout/GlobalProvider/NextThemeProvider.tsx
 *
 * 将 next-themes 包裹在应用最外层，管理 themeMode 的 localStorage 持久化和
 * HTML data-theme 属性同步，取代原先依赖 Python 后端 JSON 文件的方案。
 */
import { ThemeProvider as NextThemesProvider } from "next-themes";
import { type ReactNode } from "react";

interface NextThemeProviderProps {
  children: ReactNode;
}

export default function NextThemeProvider({
  children,
}: NextThemeProviderProps) {
  return (
    <NextThemesProvider
      disableTransitionOnChange
      enableSystem
      attribute="data-theme"
      defaultTheme="system"
      forcedTheme={undefined}
    >
      {children}
    </NextThemesProvider>
  );
}
