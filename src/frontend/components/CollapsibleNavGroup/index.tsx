import { AccordionItem, Flexbox } from '@lobehub/ui'
import { createStaticStyles } from 'antd-style'
import type { Key, ReactNode } from 'react'

const styles = createStaticStyles(({ css }) => ({
  icon: css`
    display: flex;
    align-items: center;
    font-size: 14px;
  `,
  title: css`
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
  `,
}))

interface CollapsibleNavGroupProps {
  groupKey: Key
  title: string
  icon?: ReactNode
  children: ReactNode
}

const CollapsibleNavGroup = ({ groupKey, title, icon, children }: CollapsibleNavGroupProps) => {
  return (
    <AccordionItem
      itemKey={groupKey}
      paddingBlock={4}
      paddingInline={8}
      title={
        <Flexbox align="center" gap={8} horizontal>
          {icon && <span className={styles.icon}>{icon}</span>}
          <span className={styles.title}>{title}</span>
        </Flexbox>
      }
    >
      {children}
    </AccordionItem>
  )
}

export default CollapsibleNavGroup
