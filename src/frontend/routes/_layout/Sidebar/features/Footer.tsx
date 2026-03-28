import { FluentEmoji } from '@lobehub/ui'
import { createStaticStyles } from 'antd-style'

const styles = createStaticStyles(({ css, cssVar }) => ({
  footer: css`
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px 16px 20px;

    font-size: 15px;
    font-weight: 700;
    color: ${cssVar.colorText};
  `,
}))

const SidebarFooter = () => {
  return (
    <div className={styles.footer}>
      <FluentEmoji emoji="📸" size={48} type="anim" />
      <span>扣子2剪映</span>
    </div>
  )
}

export default SidebarFooter
