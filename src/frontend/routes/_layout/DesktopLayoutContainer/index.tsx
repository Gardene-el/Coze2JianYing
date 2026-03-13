/**
 * DesktopLayoutContainer — 对齐 LobeChat
 *
 * 为主内容区（Content + LogPanel）提供圆角边框容器，padding 已在 style.ts 硬编码。
 */
import { Flexbox } from "@lobehub/ui";
import { useTheme } from "antd-style";
import { type FC, type PropsWithChildren, useMemo } from "react";

import { useIsDark } from "@/hooks/useIsDark";

import { containerStyles } from "./style";

const DesktopLayoutContainer: FC<PropsWithChildren> = ({ children }) => {
  const theme = useTheme();
  const isDark = useIsDark();

  /**
   * 边框颜色：亮色用更强的 colorBorder，暗色用较弱的 colorBorderSecondary——对齐 LobeChat。
   * 圆角使用 borderRadiusLG。
   */
  const innerCssVariables = useMemo<Record<string, string>>(
    () => ({
      "--container-border-color": isDark
        ? theme.colorBorderSecondary
        : theme.colorBorder,
      "--container-border-radius": `${theme.borderRadiusLG}px`,
    }),
    [
      isDark,
      theme.colorBorderSecondary,
      theme.colorBorder,
      theme.borderRadiusLG,
    ],
  );

  return (
    <Flexbox
      className={containerStyles.outerContainer}
      height={"100%"}
      width={"100%"}
    >
      <Flexbox
        className={containerStyles.innerContainer}
        height={"100%"}
        width={"100%"}
        style={innerCssVariables}
      >
        {children}
      </Flexbox>
    </Flexbox>
  );
};

DesktopLayoutContainer.displayName = "DesktopLayoutContainer";

export default DesktopLayoutContainer;
