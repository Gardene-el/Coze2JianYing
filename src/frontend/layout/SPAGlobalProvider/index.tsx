import { TooltipGroup } from "@lobehub/ui";
import { StyleProvider } from "antd-style";
import { domMax, LazyMotion } from "motion/react";
import {
  lazy,
  memo,
  type PropsWithChildren,
  Suspense,
  useLayoutEffect,
} from "react";

import AppTheme from "@/layout/GlobalProvider/AppTheme";

// Lazy-loaded global UI hosts — aligns with lobehub SPAGlobalProvider
const ModalHost = lazy(() =>
  import("@lobehub/ui").then((m) => ({ default: m.ModalHost })),
);
const ToastHost = lazy(() =>
  import("@lobehub/ui").then((m) => ({ default: m.ToastHost })),
);
const ContextMenuHost = lazy(() =>
  import("@lobehub/ui").then((m) => ({ default: m.ContextMenuHost })),
);

/**
 * 注入初始 body 背景色，防止深色/浅色模式切换时的闪屏。
 * 对齐 LobeChat StyleRegistry（Next.js SSR 版）逻辑。
 */
function injectBodyBackground() {
  const isDark =
    document.documentElement.getAttribute("data-theme") === "dark" ||
    (document.documentElement.getAttribute("data-theme") == null &&
      window.matchMedia("(prefers-color-scheme: dark)").matches);

  // Electron 窗口背景透明；Web fallback 用纯色
  const isElectron = typeof window !== "undefined" && !!window.electron;

  if (isElectron) {
    document.body.style.background = isDark
      ? "color-mix(in srgb, #000 90%, transparent)"
      : "color-mix(in srgb, #f8f8f8 70%, transparent)";
  } else {
    document.body.style.backgroundColor = isDark ? "#000" : "#f8f8f8";
  }
}

/**
 * SPAGlobalProvider — 对齐 lobehub/src/layout/SPAGlobalProvider
 *
 * 层级：AppTheme → LazyMotion(domMax) → TooltipGroup → StyleProvider(speedy) → children
 *       + Suspense: ModalHost / ToastHost / ContextMenuHost
 */
const SPAGlobalProvider = memo<PropsWithChildren>(({ children }) => {
  // 移除加载屏 + 注入初始背景色，防止白屏/黑屏闪烁
  useLayoutEffect(() => {
    document.getElementById("loading-screen")?.remove();
    injectBodyBackground();
  }, []);

  return (
    <AppTheme>
      <LazyMotion features={domMax}>
        <TooltipGroup layoutAnimation={false}>
          <StyleProvider speedy={import.meta.env.PROD}>
            {children}
          </StyleProvider>
        </TooltipGroup>
        <Suspense>
          <ModalHost />
          <ToastHost />
          <ContextMenuHost />
        </Suspense>
      </LazyMotion>
    </AppTheme>
  );
});

SPAGlobalProvider.displayName = "SPAGlobalProvider";

export default SPAGlobalProvider;
