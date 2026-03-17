import type { NeutralColors, PrimaryColors } from "@lobehub/ui";
import type { StateCreator } from "zustand";

import { guiSettingsAPI } from "@/services/gui/settings";
import { ngrokTunnelService } from "@/services/tunnels/ngrok";
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
    set({
      animationMode: (data.animation_mode ?? "agile") as AnimationMode,
      apiPort: data.api_port ?? "20211",
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
      relayWorkerUrl: data.relay_worker_url ?? "",
      themeMode: (data.theme_mode ?? "system").toLowerCase(),
      transferEnabled: data.transfer_enabled ?? false,
    });
  },

  saveSettings: async (patch) => {
    set({ isSaving: true, ...patch });
    try {
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
          relay_worker_url: current.relayWorkerUrl,
          theme_mode: current.themeMode,
          transfer_enabled: current.transferEnabled,
        }),
      ];
      // ngrok settings are persisted in electron-store via IPC
      if (window.electronAPI) {
        saves.push(
          ngrokTunnelService.saveSettings({
            authToken: current.ngrokAuthToken,
            region: current.ngrokRegion as string,
          }),
        );
      }
      await Promise.all(saves);
    } finally {
      set({ isSaving: false });
    }
  },

  detectDraftPath: async () => {
    const data = await guiSettingsAPI.detectPath();
    if (data.path) {
      set({ draftFolder: data.path });
    }
    return data.path ?? "";
  },
});
