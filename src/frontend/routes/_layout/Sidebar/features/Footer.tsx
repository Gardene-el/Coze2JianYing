import { FluentEmoji } from "@lobehub/ui";
import { createStyles } from "antd-style";

const useStyles = createStyles(({ token, css }) => ({
  footer: css`
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px 16px 20px;

    font-size: 15px;
    font-weight: 700;
    color: ${token.colorText};
  `,
}));

const SidebarFooter = () => {
  const { styles } = useStyles();

  return (
    <div className={styles.footer}>
      <FluentEmoji emoji="📸" size={48} type="anim" />
      <span>COZE2JIANYING</span>
    </div>
  );
};

export default SidebarFooter;
