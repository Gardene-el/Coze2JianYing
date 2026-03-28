import { SideBarLayout } from '@/features/NavPanel'

import SidebarBody from './features/Body'
import SidebarFooter from './features/Footer'
import SidebarHeader from './features/Header'

const SidebarContent = () => {
  return (
    <SideBarLayout body={<SidebarBody />} footer={<SidebarFooter />} header={<SidebarHeader />} />
  )
}

export default SidebarContent
