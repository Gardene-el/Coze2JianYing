import { BACKEND_CHANNELS, GUI_SETTINGS_CHANNELS, TUNNEL_CHANNELS } from '@c2jy/tunnel-core'
import type { StateCreator } from 'zustand'
import { setApiBaseUrl } from '@/services/client'
import { guiSettingsAPI } from '@/services/gui/settings'
import { cloudflareTunnelService } from '@/services/tunnels/cloudflare'
import { ngrokTunnelService } from '@/services/tunnels/ngrok'
import type { SettingsState } from '../initialState'

export interface SettingsPersistAction {
  loadSettings: () => Promise<void>
  saveSettings: (patch: Partial<SettingsState>) => Promise<void>
  detectDraftPath: () => Promise<string>
}

export const createSettingsPersistSlice: StateCreator<
  SettingsState & SettingsPersistAction,
  [],
  [],
  SettingsPersistAction
> = (set, get) => ({
  loadSettings: async () => {
    // ── Step 1: resolve the actual backend port and fix axios baseURL FIRST
    // so that every subsequent HTTP call goes to 127.0.0.1 (not localhost/::1)
    const backendPort = window.electronAPI
      ? ((await window.electronAPI.invoke(BACKEND_CHANNELS.getPort).catch(() => 20211)) as number)
      : 20211
    setApiBaseUrl(backendPort)

    // ── Step 2: read persisted GUI settings from Electron store via IPC
    //    (replaces the old guiSettingsAPI.get() HTTP call)
    const stored = window.electronAPI
      ? await window.electronAPI.invoke(GUI_SETTINGS_CHANNELS.get).catch(() => null)
      : null

    // ── Step 3: read ngrok / cloudflare / workerUrl from Electron store
    const ngrokStored = window.electronAPI
      ? await ngrokTunnelService.getSettings().catch(() => null)
      : null
    const cloudflareStored = window.electronAPI
      ? await cloudflareTunnelService.getSettings().catch(() => null)
      : null
    const workerUrl = window.electronAPI
      ? await window.electronAPI.invoke(TUNNEL_CHANNELS.getWorkerUrl).catch(() => '')
      : ''

    const gui = stored as {
      draftFolder?: string
    } | null

    set({
      apiPort: String(backendPort),
      draftFolder: gui?.draftFolder ?? '',
      loaded: true,
      ngrokAuthToken: ngrokStored?.authToken ?? '',
      ngrokRegion: ngrokStored?.region ?? 'us',
      cloudflareTunnelToken: cloudflareStored?.token ?? '',
      cloudflareTunnelPublicUrl: cloudflareStored?.publicUrl ?? '',
      relayWorkerUrl: (workerUrl as string) || get().relayWorkerUrl,
    })

    // ── Step 4: validate draft folder in main process (fs check), then push
    //    to Python memory.
    const current = get()
    const guiSettings = {
      draftFolder: current.draftFolder,
    }
    const effectivePaths = window.electronAPI
      ? await window.electronAPI
          .invoke(GUI_SETTINGS_CHANNELS.resolveEffectivePaths, guiSettings)
          .catch(() => ({ draftFolder: '' }))
      : { draftFolder: '' }
    guiSettingsAPI
      .put({
        draft_folder: (effectivePaths as { draftFolder: string }).draftFolder,
      })
      .catch(() => {
        /* non-fatal */
      })
  },

  saveSettings: async (patch) => {
    set({ ...patch })
    const current = get()

    // Validate draft folder in main process (fs check), then push to Python memory.
    const guiSettings = {
      draftFolder: current.draftFolder,
    }
    const effectivePaths = window.electronAPI
      ? await window.electronAPI
          .invoke(GUI_SETTINGS_CHANNELS.resolveEffectivePaths, guiSettings)
          .catch(() => ({ draftFolder: '' }))
      : { draftFolder: '' }

    // Push draft_folder into Python memory (best-effort, non-fatal).
    // Python uses this value for in-progress tasks; the authoritative
    // persistence is in the Electron store via IPC below.
    guiSettingsAPI
      .put({
        draft_folder: (effectivePaths as { draftFolder: string }).draftFolder,
      })
      .catch(() => {
        /* non-fatal */
      })

    const saves: Promise<unknown>[] = []

    if (window.electronAPI) {
      // Persist GUI settings into Electron store
      saves.push(
        window.electronAPI.invoke(GUI_SETTINGS_CHANNELS.set, {
          draftFolder: current.draftFolder,
        }),
      )
      saves.push(
        ngrokTunnelService.saveSettings({
          authToken: current.ngrokAuthToken,
          region: current.ngrokRegion as string,
        }),
      )
      saves.push(
        cloudflareTunnelService.saveSettings({
          token: current.cloudflareTunnelToken,
          publicUrl: current.cloudflareTunnelPublicUrl,
        }),
      )
      saves.push(window.electronAPI.invoke(TUNNEL_CHANNELS.setWorkerUrl, current.relayWorkerUrl))
      saves.push(window.electronAPI.invoke(BACKEND_CHANNELS.setPort, Number(current.apiPort)))
    }
    await Promise.all(saves)
  },

  detectDraftPath: async () => {
    // In Electron, detect via main-process IPC (uses app.getPath('home') — more reliable).
    // In web mode, fall back to the Python HTTP endpoint.
    const detected = window.electronAPI
      ? await window.electronAPI
          .invoke(GUI_SETTINGS_CHANNELS.detectDefaultDraftFolder)
          .catch(() => null)
      : await guiSettingsAPI
          .detectPath()
          .then((d) => d.path ?? null)
          .catch(() => null)
    if (detected) {
      set({ draftFolder: detected as string })
    }
    return (detected as string | null) ?? ''
  },
})
