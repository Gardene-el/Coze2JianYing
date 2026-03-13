import { TITLE_BAR_HEIGHT } from "@lobechat/desktop-bridge";
import { Flexbox } from "@lobehub/ui";
import { type FC } from "react";

import { electronStylish } from "@/styles/electron";

import { useWatchThemeUpdate } from "../system/useWatchThemeUpdate";

/**
 * A minimal TitleBar for secondary Electron windows (e.g. onboarding, dialogs).
 * Provides only a draggable area and theme-sync; no navigation or window controls.
 *
 * Mirrors lobehub/src/features/Electron/titlebar/SimpleTitleBar.tsx.
 */
const SimpleTitleBar: FC = () => {
  useWatchThemeUpdate();
  return (
    <Flexbox
      horizontal
      align="center"
      className={electronStylish.draggable}
      height={TITLE_BAR_HEIGHT}
      justify="center"
      width="100%"
    />
  );
};

export default SimpleTitleBar;
