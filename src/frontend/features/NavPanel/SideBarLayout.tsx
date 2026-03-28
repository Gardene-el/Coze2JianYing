import { Flexbox, ScrollShadow } from '@lobehub/ui'
import type { ReactNode } from 'react'

interface SidebarLayoutProps {
  body?: ReactNode
  footer?: ReactNode
  header?: ReactNode
}

const SideBarLayout = ({ header, body, footer }: SidebarLayoutProps) => {
  return (
    <Flexbox gap={4} style={{ height: '100%', overflow: 'hidden' }}>
      {header}
      <ScrollShadow size={2} style={{ flex: 1, minHeight: 0 }}>
        {body}
      </ScrollShadow>
      {footer}
    </Flexbox>
  )
}

export default SideBarLayout
