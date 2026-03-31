import { createStaticStyles } from 'antd-style'

export const enumExplorerStyles = createStaticStyles(({ css, cssVar }) => ({
  /** 最外层水平分栏容器 */
  root: css`
    display: flex;
    height: 100%;
    overflow: hidden;
  `,
  /** 左侧枚举分类侧栏（宽度由 CSS 变量 --enum-sidebar-w 动态控制） */
  sidebar: css`
    width: var(--enum-sidebar-w, 280px);
    flex-shrink: 0;
    border-right: 1px solid ${cssVar.colorBorderSecondary};
    overflow-y: auto;
    scrollbar-width: thin;
    scrollbar-color: ${cssVar.colorFill} transparent;
    position: relative;
  `,
  /** 侧栏内容区 padding */
  sidebarInner: css`
    padding: 12px 8px;
  `,
  /** 拖拽手柄：贴在侧栏右边缘 */
  resizeHandle: css`
    position: absolute;
    top: 0;
    right: 0;
    width: 4px;
    height: 100%;
    cursor: col-resize;
    z-index: 10;
    transition: background-color 0.15s ease;

    &:hover,
    &[data-dragging="true"] {
      background-color: ${cssVar.colorPrimary};
    }
  `,
  /** 右侧内容区域 */
  content: css`
    flex: 1;
    min-width: 0;
    overflow-y: auto;
    scrollbar-width: thin;
    scrollbar-color: ${cssVar.colorFill} transparent;
  `,
  /** 内容区内部 padding + 最大宽度 */
  contentInner: css`
    padding: 24px;
    max-width: 960px;
  `,
  /** 枚举值网格布局 */
  valueGrid: css`
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    padding: 4px 0 8px;
  `,
  /** 单个枚举值标签 */
  valueTag: css`
    margin: 0 !important;
    cursor: pointer;
    user-select: text;
    transition:
      opacity 0.15s ease,
      background-color 0.15s ease;

    &:hover {
      opacity: 0.7;
    }
  `,
  /** 函数名 Accordion 标题文本 */
  fnTitle: css`
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.02em;
  `,
  /** 枚举类型条目（可点击叶节点） */
  enumItem: css`
    display: flex;
    width: 100%;
    align-items: center;
    justify-content: space-between;
    padding: 4px 8px 4px 12px;
    border: none;
    border-radius: 4px;
    background: none;
    color: inherit;
    font: inherit;
    cursor: pointer;
    font-size: 13px;
    transition: background-color 0.15s;
    user-select: none;

    &:hover {
      background-color: ${cssVar.colorFillSecondary};
    }
  `,
  /** 枚举类型条目：选中态 */
  enumItemActive: css`
    background-color: ${cssVar.colorFillSecondary};
    font-weight: 500;
  `,
  /** 枚举值数量标签 */
  enumCount: css`
    opacity: 0.45;
    font-size: 11px;
    flex-shrink: 0;
    margin-left: 4px;
  `,
  /** 标题行 */
  titleRow: css`
    margin-bottom: 4px;
  `,
  /** 标题 */
  title: css`
    margin: 0;
  `,
  /** 标题中的枚举类名 */
  titleSub: css`
    opacity: 0.45;
    font-weight: 400;
    font-size: 13px;
    margin-left: 8px;
  `,
  /** 统计行 */
  statsRow: css`
    margin-bottom: 16px;
    font-size: 13px;
    opacity: 0.65;
  `,
  /** 免费分区分割线 */
  sectionDivider: css`
    margin: 8px 0;
  `,
  /** VIP分区分割线 */
  sectionDividerVip: css`
    margin: 16px 0 8px;
  `,
  /** VIP图标 */
  crownIcon: css`
    color: #faad14;
  `,
}))
