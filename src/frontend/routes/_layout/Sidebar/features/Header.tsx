import { createStyles } from "antd-style";

const useStyles = createStyles(({ css }) => ({
  header: css`
    min-height: 12px;
  `,
}));

const SidebarHeader = () => {
  const { styles } = useStyles();

  // Placeholder to keep header slot aligned with lobehub style split.
  return <div className={styles.header} />;
};

export default SidebarHeader;
