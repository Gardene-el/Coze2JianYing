import { createStaticStyles } from 'antd-style'

export const tutorialDocsStyles = createStaticStyles(({ css, cssVar }) => ({
  /** 最外层容器：填充父级 Content，纵向 flex 布局 */
  root: css`
    display: flex;
    flex-direction: column;
    height: 100%;
    overflow: hidden;
  `,
  /** 固定头部：Segmented 导航居中 */
  header: css`
    flex-shrink: 0;
    display: flex;
    justify-content: center;
    padding: 16px 24px;
    border-bottom: 1px solid ${cssVar.colorBorderSecondary};
  `,
  /** 子路由内容区域，flex-1 + 隐藏溢出，各子页面独立管控滚动 */
  content: css`
    flex: 1;
    min-height: 0;
    overflow: hidden;
  `,
}))
