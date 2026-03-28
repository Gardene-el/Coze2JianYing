import type {
  NgrokSettings,
  StartTunnelPayload,
  TunnelSettingsPayload,
  TunnelStatus,
} from '@c2jy/tunnel-core'
import { TUNNEL_CHANNELS } from '@c2jy/tunnel-core'

const invoke = <T>(channel: string, ...args: unknown[]): Promise<T> => {
  if (!window.electronAPI) throw new Error('electronAPI unavailable (non-Electron environment)')
  return window.electronAPI.invoke(channel, ...args) as Promise<T>
}

export const ngrokTunnelService = {
  getSettings: (): Promise<NgrokSettings | null> =>
    invoke(TUNNEL_CHANNELS.getSettings, { provider: 'ngrok' } satisfies {
      provider: 'ngrok'
    }),

  getStatus: (): Promise<TunnelStatus> =>
    invoke(TUNNEL_CHANNELS.getStatus, { provider: 'ngrok' } satisfies {
      provider: 'ngrok'
    }),

  saveSettings: (settings: NgrokSettings): Promise<void> =>
    invoke(TUNNEL_CHANNELS.saveSettings, {
      provider: 'ngrok',
      settings,
    } satisfies TunnelSettingsPayload),

  startTunnel: (port: number, overrides?: Partial<NgrokSettings>): Promise<TunnelStatus> =>
    invoke(TUNNEL_CHANNELS.startTunnel, {
      port,
      provider: 'ngrok',
      settings: overrides,
    } satisfies StartTunnelPayload),

  stopTunnel: (): Promise<TunnelStatus> =>
    invoke(TUNNEL_CHANNELS.stopTunnel, { provider: 'ngrok' } satisfies {
      provider: 'ngrok'
    }),
}
