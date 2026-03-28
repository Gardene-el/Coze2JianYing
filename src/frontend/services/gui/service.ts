import { BACKEND_CHANNELS } from '@c2jy/tunnel-core'

import type { ServiceStatusResponse } from '../types'

const invoke = <T>(channel: string, ...args: unknown[]): Promise<T> => {
  if (!window.electronAPI) throw new Error('electronAPI unavailable (non-Electron environment)')
  return window.electronAPI.invoke(channel, ...args) as Promise<T>
}

const _noElectron = (): Promise<ServiceStatusResponse> =>
  Promise.resolve({ port: 20211, running: false })

/**
 * Backend process management via IPC (Electron only).
 * Falls back to no-op responses when running in a plain browser context.
 */
export const guiServiceAPI = {
  getStatus: (): Promise<ServiceStatusResponse> =>
    window.electronAPI ? invoke<ServiceStatusResponse>(BACKEND_CHANNELS.getStatus) : _noElectron(),

  start: (): Promise<ServiceStatusResponse> =>
    window.electronAPI ? invoke<ServiceStatusResponse>(BACKEND_CHANNELS.start) : _noElectron(),

  stop: (): Promise<ServiceStatusResponse> =>
    window.electronAPI ? invoke<ServiceStatusResponse>(BACKEND_CHANNELS.stop) : _noElectron(),
}
