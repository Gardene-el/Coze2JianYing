import type { StateCreator } from 'zustand'

import { cloudflareTunnelService } from '@/services/tunnels/cloudflare'
import type { ServiceState } from '../initialState'

export interface CloudflareAction {
  startCloudflare: (token: string, publicUrl: string, port: number) => Promise<string>
  stopCloudflare: () => Promise<void>
  fetchCloudflareStatus: () => Promise<void>
}

export const createCloudflareSlice: StateCreator<
  ServiceState & CloudflareAction,
  [],
  [],
  CloudflareAction
> = (set) => ({
  startCloudflare: async (token, publicUrl, port) => {
    set({ cloudflareLoading: true })
    try {
      const data = await cloudflareTunnelService.startTunnel(port, {
        token,
        publicUrl,
      })
      const url = data.publicUrl ?? ''
      set({ cloudflareRunning: true, cloudflareUrl: url })
      return url
    } finally {
      set({ cloudflareLoading: false })
    }
  },

  stopCloudflare: async () => {
    set({ cloudflareLoading: true })
    try {
      await cloudflareTunnelService.stopTunnel()
      set({ cloudflareRunning: false, cloudflareUrl: '' })
    } finally {
      set({ cloudflareLoading: false })
    }
  },

  fetchCloudflareStatus: async () => {
    try {
      const data = await cloudflareTunnelService.getStatus()
      set({
        cloudflareRunning: data.isRunning,
        cloudflareUrl: data.publicUrl ?? '',
      })
    } catch {
      // 静默处理
    }
  },
})
