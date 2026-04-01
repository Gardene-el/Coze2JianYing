import { createStaticStyles } from 'antd-style'

export const stickerBrowserStyles = createStaticStyles(({ css, cssVar }) => ({
  root: css`
    display: flex;
    flex-direction: column;
    height: 100%;
    overflow: hidden;
  `,
  toolbar: css`
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px 24px 12px;
    flex-shrink: 0;
    border-bottom: 1px solid ${cssVar.colorBorderSecondary};
  `,
  stats: css`
    font-size: 13px;
    opacity: 0.55;
    flex-shrink: 0;
    white-space: nowrap;
  `,
  content: css`
    flex: 1;
    overflow-y: auto;
    padding: 16px 24px;
    scrollbar-width: thin;
    scrollbar-color: ${cssVar.colorFill} transparent;
  `,
  grid: css`
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    padding-bottom: 8px;
  `,
  tag: css`
    margin: 0 !important;
    cursor: pointer;
    user-select: text;
    transition: opacity 0.15s ease, background-color 0.15s ease;
    max-width: 200px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;

    &:hover {
      opacity: 0.7;
    }
  `,
  pagination: css`
    display: flex;
    justify-content: center;
    padding: 16px 0 8px;
    flex-shrink: 0;
  `,
}))
