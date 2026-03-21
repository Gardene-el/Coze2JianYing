import type { NeutralColors, PrimaryColors } from "@lobehub/ui";
import type { StateCreator } from "zustand";

import { guiSettingsAPI } from "@/services/gui/settings";
import { setApiBaseUrl } from "@/services/client";
import { ngrokTunnelService } from "@/services/tunnels/ngrok";
import { BACKEND_CHANNELS, TUNNEL_CHANNELS } from "@c2jy/tunnel-core";
import type { AnimationMode, SettingsState } from "../initialState";

export interface SettingsPersistAction {
  loadSettings: () => Promise<void>;
  saveSettings: (patch: Partial<SettingsState>) => Promise<void>;
  detectDraftPath: () => Promise<string>;
}

export const createSettingsPersistSlice: StateCreator<
  SettingsState & SettingsPersistAction,
  [],
  [],
  SettingsPersistAction
> = (set, get) => ({
  loadSettings: async () => {
    const data = await guiSettingsAPI.get();
    // ngrok settings come from electron-store via IPC (Electron only)
    const ngrokStored = window.electronAPI
      ? await ngrokTunnelService.getSettings().catch(() => null)
      : null;
    // relay worker URL comes from electron-store via IPC (Electron only)
    const workerUrl = window.electronAPI
      ? await window.electronAPI
          .invoke(TUNNEL_CHANNELS.getWorkerUrl)
          .catch(() => "")
      : "";
    // backend port comes from electron-store via IPC (Electron only)
    const backendPort: number = window.electronAPI
      ? await window.electronAPI
          .invoke<number>(BACKEND_CHANNELS.getPort)
          .catch(() => 20211)
      : 20211;
    // Align axios baseURL with the stored port so all HTTP calls use the right port
    setApiBaseUrl(backendPort);
    set({
      animationMode: (data.animation_mode ?? "agile") as AnimationMode,
      apiPort: String(backendPort),
      customFontFamily: data.custom_font_family ?? "",
      customFontURL: data.custom_font_url ?? "",
      draftFolder: data.draft_folder ?? "",
      loaded: true,
      neutralColor: (data.neutral_color ?? undefined) as
        | NeutralColors
        | undefined,
      ngrokAuthToken: ngrokStored?.authToken ?? "",
      ngrokRegion: ngrokStored?.region ?? "us",
      primaryColor: (data.primary_color ?? undefined) as
        | PrimaryColors
        | undefined,
      relayWorkerUrl: (workerUrl as string) || get().relayWorkerUrl,
      transferEnabled: data.transfer_enabled ?? false,
    });
  },

  saveSettings: async (patch) => {
    set({ ...patch });
    const current = get();
    const saves: Promise<unknown>[] = [
      guiSettingsAPI.put({
        animation_mode: current.animationMode,
        api_port: current.apiPort,
        custom_font_family: current.customFontFamily,
        custom_font_url: current.customFontURL,
        draft_folder: current.draftFolder,
        neutral_color: current.neutralColor,
        primary_color: current.primaryColor,
        transfer_enabled: current.transferEnabled,
      }),
    ];
    // ngrok + worker URL + backend port are persisted in electron-store via IPC
    if (window.electronAPI) {
      saves.push(
        ngrokTunnelService.saveSettings({
          authToken: current.ngrokAuthToken,
          region: current.ngrokRegion as string,
        }),
      );
      saves.push(
        window.electronAPI.invoke(
          TUNNEL_CHANNELS.setWorkerUrl,
          current.relayWorkerUrl,
        ),
      );
      saves.push(
        window.electronAPI.invoke(
          BACKEND_CHANNELS.setPort,
          Number(current.apiPort),
        ),
      );
    }
    await Promise.all(saves);
  },

  detectDraftPath: async () => {
    const data = await guiSettingsAPI.detectPath();
    if (data.path) {
      set({ draftFolder: data.path });
    }
    return data.path ?? "";
  },
});
