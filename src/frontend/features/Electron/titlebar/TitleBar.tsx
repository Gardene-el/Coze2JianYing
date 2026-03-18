import { TITLE_BAR_HEIGHT } from "@lobechat/desktop-bridge";
import { Flexbox } from "@lobehub/ui";
import { memo, useMemo } from "react";

import ThemeButton from "@/components/ThemeButton";
import { electronStylish } from "@/styles/electron";

import { useWatchThemeUpdate } from "../system/useWatchThemeUpdate";
import NavigationBar from "./NavigationBar";
import WinControl from "./WinControl";

/** Detect macOS via the platform info injected by the Electron preload. */
const isMac =
  typeof window !== "undefined" &&
  (window.lobeEnv?.platform === "darwin" ||
    navigator.platform.toLowerCase().startsWith("mac"));

/**
 * Main TitleBar for the Electron desktop window.
 *
 * Layout (horizontal flex, height = TITLE_BAR_HEIGHT):
 *   [← →]  (NavigationBar, width aligned to sidebar)
 *   <spacer flex=1>
 *   [     ] (WinControl placeholder — Windows only, 132 px)
 *
 * The outer container carries -webkit-app-region:drag; clickable child
 * elements carry -webkit-app-region:no-drag via electronStylish.nodrag.
 *
 * Mirrors lobehub/src/features/Electron/titlebar/TitleBar.tsx without the
 * dependencies on electron-client-ipc, useElectronStore, TabBar, or Connection.
 */
const TitleBar = memo(() => {
  useWatchThemeUpdate();

  const showWinControl = !isMac;

  const padding = useMemo(
    () => (showWinControl ? "0 12px 0 8px" : "0 12px"),
    [showWinControl],
  );

  return (
    <Flexbox
      horizontal
      align="center"
      className={electronStylish.draggable}
      height={TITLE_BAR_HEIGHT}
      justify="space-between"
      style={{ minHeight: TITLE_BAR_HEIGHT, padding }}
      width="100%"
    >
      <Flexbox horizontal align="center" className={electronStylish.nodrag} gap={2}>
        <NavigationBar />
        <ThemeButton placement="bottomLeft" size={16} />
      </Flexbox>
      <Flexbox flex={1} />
      {showWinControl && <WinControl />}
    </Flexbox>
  );
});

export default TitleBar;
