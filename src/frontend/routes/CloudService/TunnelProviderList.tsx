/**
 * TunnelProviderList — left rail listing all tunnel providers.
 * Mirrors LobeHub's ProviderMenu/List pattern: a simple vertical Menu where
 * each item shows the provider name, optional description, and a running-state
 * indicator dot on the right.
 */

import type { TunnelProvider } from '@c2jy/tunnel-core'
import { TUNNEL_PROVIDER_LIST } from '@c2jy/tunnel-core'
import type { MenuProps } from 'antd'
import { Badge, Menu } from 'antd'
import { useServiceStore } from '@/store/service/store'

interface TunnelProviderListProps {
  onSelect: (provider: TunnelProvider) => void
}

const TunnelProviderList = ({ onSelect }: TunnelProviderListProps) => {
  const selectedTunnelProvider = useServiceStore((s) => s.selectedTunnelProvider)
  const ngrokRunning = useServiceStore((s) => s.ngrokRunning)
  const cloudflareRunning = useServiceStore((s) => s.cloudflareRunning)

  const runningMap: Record<TunnelProvider, boolean> = {
    ngrok: ngrokRunning,
    cloudflare: cloudflareRunning,
  }

  const items: MenuProps['items'] = TUNNEL_PROVIDER_LIST.map((meta) => ({
    key: meta.id,
    label: (
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: 8,
        }}
      >
        <div style={{ minWidth: 0 }}>
          <div style={{ fontWeight: 500, fontSize: 13 }}>{meta.name}</div>
          <div
            style={{
              fontSize: 11,
              color: 'var(--ant-color-text-description)',
              whiteSpace: 'normal',
              lineHeight: 1.3,
            }}
          >
            {meta.description}
          </div>
        </div>
        {runningMap[meta.id] && <Badge status="success" style={{ flexShrink: 0 }} />}
      </div>
    ),
  }))

  const handleSelect: MenuProps['onSelect'] = ({ key }) => {
    onSelect(key as TunnelProvider)
  }

  return (
    <Menu
      mode="inline"
      selectedKeys={selectedTunnelProvider ? [selectedTunnelProvider] : []}
      onSelect={handleSelect}
      items={items}
      style={{ width: 200, borderInlineEnd: 'none', userSelect: 'none' }}
    />
  )
}

export default TunnelProviderList
