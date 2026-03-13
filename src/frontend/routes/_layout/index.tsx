import { DraggablePanel } from "@lobehub/ui";
import { Layout } from "antd";
import { createStyles } from "antd-style";
import { useCallback, useState } from "react";
import { Outlet } from "react-router-dom";

import TitleBar from "@/features/Electron/titlebar/TitleBar";

import DesktopLayoutContainer from "./DesktopLayoutContainer";
import LogPanel from "./LogPanel";
import Sidebar from "./Sidebar";

const { Content, Footer } = Layout;

const SIDEBAR_WIDTH_KEY = "c2j-sidebar-width";
const DEFAULT_SIDEBAR_WIDTH = 260;

const isElectron = typeof window !== "undefined" && !!window.electron;

const useStyles = createStyles(({ token, css }) => ({
  layout: css`
    /* width: 100% 对抗父容器 ThemeProvider.div 上的 align-items: center，防止布局收缩为侧边栏宽度 */
    width: 100%;
    height: 100dvh;
    max-height: 100dvh;
    overflow: hidden;
    background: ${token.colorBgLayout};
  `,
  /** 侧边栏样式：为 DraggablePanel 提供高度和背景色 */
  panel: css`
    height: 100%;
    background: ${token.colorBgLayout};
  `,
  content: css`
    /* 在 DesktopLayoutContainer Flexbox 列中自动伸长；min-height: 0 允许垂直滚动 */
    flex: 1;
    min-height: 0;
    overflow-y: auto;
    padding: 24px;
  `,
  footer: css`
    flex: none;
    padding: 0;
    background: transparent;
  `,
}));

const MainLayout = () => {
  const { styles: dynStyles } = useStyles();

  /** localStorage 持久化侧边栏宽度，与 LobeChat globalStore.leftPanelWidth 对齐 */
  const [sidebarWidth] = useState(() => {
    const stored = localStorage.getItem(SIDEBAR_WIDTH_KEY);
    return stored ? parseInt(stored, 10) : DEFAULT_SIDEBAR_WIDTH;
  });

  const handleSizeChange = useCallback(
    (_: unknown, size?: { width?: number | string }) => {
      const w =
        typeof size?.width === "string"
          ? parseInt(size.width, 10)
          : size?.width;
      if (!w || w < 64) return;
      localStorage.setItem(SIDEBAR_WIDTH_KEY, String(w));
    },
    [],
  );

  return (
    <Layout className={dynStyles.layout} style={{ flexDirection: "column" }}>
      {/* Electron 无边框窗口：自定义标题栏（含导航按钮 + Win 原生按钮占位） */}
      {isElectron && <TitleBar />}
      {/* 侧边栏 + 内容区水平排列 */}
      <Layout style={{ flex: 1, overflow: "hidden", flexDirection: "row" }}>
        {/* 可拖拽调宽的导航侧边栏，对齐 LobeChat NavPanelDraggable */}
        <DraggablePanel
          className={dynStyles.panel}
          defaultSize={{ width: sidebarWidth, height: "100%" }}
          expandable={false}
          maxWidth={400}
          minWidth={220}
          placement="left"
          showBorder={false}
          onSizeChange={handleSizeChange}
        >
          <Sidebar />
        </DraggablePanel>
        <DesktopLayoutContainer>
          <Content className={dynStyles.content}>
            <Outlet />
          </Content>
          <Footer className={dynStyles.footer}>
            <LogPanel />
          </Footer>
        </DesktopLayoutContainer>
      </Layout>
    </Layout>
  );
};

export default MainLayout;
