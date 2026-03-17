import { createStyles } from "antd-style";

export const useNavItemStyles = createStyles(({ css, token }) => ({
  item: css`
    display: flex;
    align-items: center;
    gap: 8px;
    border-radius: 8px;
    margin-inline: 8px;
    width: calc(100% - 16px);
    padding: 0 12px;
    height: 40px;
    cursor: pointer;
    color: ${token.colorText};
    font-size: 14px;
    transition:
      background-color 0.15s ease,
      color 0.15s ease;
    user-select: none;

    &:hover {
      background-color: ${token.colorBgTextHover};
    }
  `,
  active: css`
    background-color: ${token.colorPrimaryBg};
    color: ${token.colorPrimary};
    font-weight: 500;

    &:hover {
      background-color: ${token.colorPrimaryBgHover};
    }
  `,
  icon: css`
    display: flex;
    align-items: center;
    font-size: 16px;
    flex-shrink: 0;
  `,
}));
