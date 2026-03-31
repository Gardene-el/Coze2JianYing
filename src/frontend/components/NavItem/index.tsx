import { cx } from 'antd-style'
import type { ReactNode } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

import { navItemStyles } from './style'

interface NavItemProps {
  to: string
  icon: ReactNode
  label: string
}

const NavItem = ({ to, icon, label }: NavItemProps) => {
  const navigate = useNavigate()
  const { pathname } = useLocation()

  const isActive = pathname === to || pathname.startsWith(`${to}/`)

  return (
    <button
      type="button"
      className={cx(navItemStyles.item, { [navItemStyles.active]: isActive })}
      onClick={() => navigate(to)}
    >
      <span className={navItemStyles.icon}>{icon}</span>
      <span>{label}</span>
    </button>
  )
}

export default NavItem
