/**
 * 直接移植自 lobehub/src/hooks/useIsDark.ts
 */
import { useTheme } from "antd-style";

export const useIsDark = () => {
  const { isDarkMode } = useTheme();
  return isDarkMode;
};
