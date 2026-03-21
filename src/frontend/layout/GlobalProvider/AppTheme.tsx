"use client";

import "antd/dist/reset.css";

import { TITLE_BAR_HEIGHT } from "@lobechat/desktop-bridge";
import { type NeutralColors, type PrimaryColors } from "@lobehub/ui";
import { ConfigProvider, FontLoader, ThemeProvider } from "@lobehub/ui";
import { message as antdMessage } from "antd";
import { AppConfigContext } from "antd/es/app/context";
import { createStaticStyles, cx, useTheme } from "antd-style";
import * as motion from "motion/react-m";
import { type ReactNode, memo, useEffect, useMemo } from "react";

import AntdStaticMethods from "@/components/AntdStaticMethods";
import { useIsDark } from "@/hooks/useIsDark";
import { GlobalStyle } from "@/styles";

/** isDesktop — 与 antdOverride.ts 保持一致，对齐 @lobechat/const isDesktop */
const isDesktop = typeof window !== "undefined" && !!window.electron;

// createStaticStyles 在 antd-style 中直接返回样式对象（非 hook），模块级立即求值
const appContainerStyles = createStaticStyles(({ css, cssVar }) => ({
  app: css`
    position: relative;

    overscroll-behavior: none;
    display: flex;
    flex-direction: column;
    align-items: center;

    height: 100%;
    min-height: 100dvh;
    max-height: 100dvh;

    @media (device-width >= 576px) {
      overflow: hidden;
    }
  `,
  scrollbar: css`
    scrollbar-color: ${cssVar.colorFill} transparent;
    scrollbar-width: thin;

    #lobe-mobile-scroll-container {
      scrollbar-width: none;

      ::-webkit-scrollbar {
        width: 0;
        height: 0;
      }
    }
  `,
  scrollbarPolyfill: css`
    ::-webkit-scrollbar {
      width: 0.75em;
      height: 0.75em;
    }

    ::-webkit-scrollbar-thumb {
      border-radius: 10px;
    }

    :hover::-webkit-scrollbar-thumb {
      border: 3px solid transparent;
      background-color: ${cssVar.colorText};
      background-clip: content-box;
    }

    ::-webkit-scrollbar-track {
      background-color: transparent;
    }
  `,
}));

export interface AppThemeProps {
  children?: ReactNode;
  customFontFamily?: string;
  customFontURL?: string;
  defaultNeutralColor?: NeutralColors;
  defaultPrimaryColor?: PrimaryColors;
}

const AppTheme = memo<AppThemeProps>(
  ({
    children,
    defaultPrimaryColor,
    defaultNeutralColor,
    customFontURL,
    customFontFamily,
  }) => {
    const antdTheme = useTheme();

    // next-themes 负责 data-theme 属性同步和 localStorage 持久化，此处直接读取
    const isDark = useIsDark();
    const currentAppearance = isDark ? "dark" : "light";

    // Electron 桌面：将消息通知顶部偏移 titlebar（仅桌面端）
    const messageTop = isDesktop ? TITLE_BAR_HEIGHT + 8 : undefined;
    const appConfig = useMemo(
      () => (messageTop === undefined ? {} : { message: { top: messageTop } }),
      [messageTop],
    );

    useEffect(() => {
      if (messageTop === undefined) return;
      antdMessage.config({ top: messageTop });
    }, [messageTop]);

    const resolvedFontFamily = customFontFamily || undefined;
    const resolvedFontURL = customFontURL || undefined;

    // D-15: 直接三元计算，对齐 lobehub 模式（去除 useMemo）
    const fontFamilyToken = resolvedFontFamily
      ? `${resolvedFontFamily},${antdTheme.fontFamily}`
      : undefined;

    return (
      <AppConfigContext value={appConfig}>
        <ThemeProvider
          appearance={currentAppearance}
          className={cx(
            appContainerStyles.app,
            appContainerStyles.scrollbar,
            appContainerStyles.scrollbarPolyfill,
          )}
          defaultAppearance={currentAppearance}
          defaultThemeMode={currentAppearance}
          customTheme={{
            neutralColor: defaultNeutralColor,
            primaryColor: defaultPrimaryColor,
          }}
          theme={{
            cssVar: { key: "lobe-vars" },
            token: {
              fontFamily: fontFamilyToken,
              motion: true,
              motionUnit: 0.05,
            },
          }}
        >
          {!!resolvedFontURL && <FontLoader url={resolvedFontURL} />}
          <GlobalStyle />
          <AntdStaticMethods />
          <ConfigProvider motion={motion}>{children}</ConfigProvider>
        </ThemeProvider>
      </AppConfigContext>
    );
  },
);

AppTheme.displayName = "AppTheme";

export default AppTheme;
