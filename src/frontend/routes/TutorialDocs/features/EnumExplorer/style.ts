import { createStaticStyles } from 'antd-style'

export const enumExplorerStyles = createStaticStyles(({ css, cssVar }) => ({
  /** 最外层水平分栏容器 */
  root: css`
    display: flex;
    height: 100%;
    overflow: hidden;
  `,
  /** 左侧枚举分类侧栏 */
  sidebar: css`
    width: 220px;
    flex-shrink: 0;
    border-right: 1px solid ${cssVar.colorBorderSecondary};
    overflow-y: auto;
    scrollbar-width: thin;
    scrollbar-color: ${cssVar.colorFill} transparent;
  `,
  /** 侧栏内容区 padding */
  sidebarInner: css`
    padding: 12px 8px;
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
    max-width: 800px;
  `,
}))
