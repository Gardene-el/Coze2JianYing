import type {
  CloudflareTunnelSettings,
  StartTunnelPayload,
  TunnelSettingsPayload,
  TunnelStatus,
} from '@c2jy/tunnel-core'
import { TUNNEL_CHANNELS } from '@c2jy/tunnel-core'

const invoke = <T>(channel: string, ...args: unknown[]): Promise<T> => {
  if (!window.electronAPI) throw new Error('electronAPI unavailable (non-Electron environment)')
  return window.electronAPI.invoke(channel, ...args) as Promise<T>
}

export const cloudflareTunnelService = {
  getSettings: (): Promise<CloudflareTunnelSettings | null> =>
    invoke(TUNNEL_CHANNELS.getSettings, {
      provider: 'cloudflare',
    } satisfies { provider: 'cloudflare' }),

  getStatus: (): Promise<TunnelStatus> =>
    invoke(TUNNEL_CHANNELS.getStatus, {
      provider: 'cloudflare',
    } satisfies { provider: 'cloudflare' }),

  saveSettings: (settings: CloudflareTunnelSettings): Promise<void> =>
    invoke(TUNNEL_CHANNELS.saveSettings, {
      provider: 'cloudflare',
      settings,
    } satisfies TunnelSettingsPayload),

  startTunnel: (
    port: number,
    overrides?: Partial<CloudflareTunnelSettings>,
  ): Promise<TunnelStatus> =>
    invoke(TUNNEL_CHANNELS.startTunnel, {
      port,
      provider: 'cloudflare',
      settings: overrides,
    } satisfies StartTunnelPayload),

  stopTunnel: (): Promise<TunnelStatus> =>
    invoke(TUNNEL_CHANNELS.stopTunnel, {
      provider: 'cloudflare',
    } satisfies { provider: 'cloudflare' }),
}
