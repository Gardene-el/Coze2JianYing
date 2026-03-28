import { ActionIcon, DropdownMenu, type DropdownMenuProps, Icon } from '@lobehub/ui'
import { Monitor, Moon, Sun } from 'lucide-react'
import { useTheme as useNextThemesTheme } from 'next-themes'
import { type FC, useMemo } from 'react'

const themeIcons = {
  dark: Moon,
  light: Sun,
  system: Monitor,
}

const ThemeButton: FC<{
  placement?: DropdownMenuProps['placement']
  size?: number
}> = ({ placement, size }) => {
  const { setTheme, theme } = useNextThemesTheme()

  const items = useMemo<DropdownMenuProps['items']>(
    () => [
      {
        icon: <Icon icon={themeIcons.system} />,
        key: 'system',
        label: '跟随系统',
        onClick: () => setTheme('system'),
      },
      {
        icon: <Icon icon={themeIcons.light} />,
        key: 'light',
        label: '浅色',
        onClick: () => setTheme('light'),
      },
      {
        icon: <Icon icon={themeIcons.dark} />,
        key: 'dark',
        label: '深色',
        onClick: () => setTheme('dark'),
      },
    ],
    [setTheme],
  )

  return (
    <DropdownMenu items={items} placement={placement}>
      <ActionIcon
        icon={themeIcons[(theme as 'dark' | 'light' | 'system') || 'system']}
        size={size ?? { blockSize: 32, size: 16 }}
      />
    </DropdownMenu>
  )
}

export default ThemeButton
