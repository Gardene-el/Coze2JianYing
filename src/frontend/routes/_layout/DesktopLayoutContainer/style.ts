import { createStaticStyles } from 'antd-style'

/** 与 AppTheme / antdOverride 保持一致的 isDesktop 判断 */
const isDesktop = typeof window !== 'undefined' && !!window.electron

// 顶部 padding: Electron 紧贴 TitleBar → 0；Web 保留 8px
const paddingTop = isDesktop ? '0' : '8px'

/**
 * DesktopLayoutContainer 样式 — 对齐 LobeChat
 *
 * outerContainer: 侧边栏始终展开 → padding-left/top 为 0，right/bottom 保留 8px
 * innerContainer: 圆角边框内容盒
 */
export const containerStyles = createStaticStyles(({ css, cssVar }) => ({
  innerContainer: css`
    position: relative;
    overflow: hidden;
    border: 1px solid var(--container-border-color, ${cssVar.colorBorder});
    border-radius: var(--container-border-radius, ${cssVar.borderRadius});
    background: ${cssVar.colorBgContainer};
  `,
  outerContainer: css`
    flex: 1;
    min-width: 0;
    position: relative;
    overflow: hidden;

    /*
     * 顶部/左侧紧贴 TitleBar / 侧边栏，不需要间距。
     * 右侧/底部保留 8px，与 LobeChat DeskopLayoutContainer 对齐。
     * 直接硬编码，避免 CSS 变量在 CSS-in-JS insertion order 下的覆盖不稳定。
     */
    padding-top: ${paddingTop};
    padding-right: 8px;
    padding-bottom: 8px;
    padding-left: 0;
  `,
}))
