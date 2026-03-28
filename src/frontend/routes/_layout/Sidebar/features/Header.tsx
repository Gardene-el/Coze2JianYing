import { createStaticStyles } from 'antd-style'

const styles = createStaticStyles(({ css }) => ({
  header: css`
    min-height: 12px;
  `,
}))

const SidebarHeader = () => {
  // Placeholder to keep header slot aligned with lobehub style split.
  return <div className={styles.header} />
}

export default SidebarHeader
