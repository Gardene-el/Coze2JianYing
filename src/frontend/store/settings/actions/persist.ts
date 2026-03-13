import type { NeutralColors, PrimaryColors } from "@lobehub/ui";
import type { StateCreator } from "zustand";

import { guiSettingsAPI } from "@/services/gui/settings";
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
    set({
      draftFolder: data.draft_folder ?? "",
      apiPort: data.api_port ?? "20211",
      ngrokAuthToken: data.ngrok_auth_token ?? "",
      ngrokRegion: data.ngrok_region ?? "us",
      relayWorkerUrl: data.relay_worker_url ?? "",
      themeMode: (data.theme_mode ?? "system").toLowerCase(),
      transferEnabled: data.transfer_enabled ?? false,
      primaryColor: (data.primary_color ?? undefined) as
        | PrimaryColors
        | undefined,
      neutralColor: (data.neutral_color ?? undefined) as
        | NeutralColors
        | undefined,
      animationMode: (data.animation_mode ?? "agile") as AnimationMode,
      customFontFamily: data.custom_font_family ?? "",
      customFontURL: data.custom_font_url ?? "",
      loaded: true,
    });
  },

  saveSettings: async (patch) => {
    set({ isSaving: true, ...patch });
    try {
      const current = get();
      await guiSettingsAPI.put({
        draft_folder: current.draftFolder,
        api_port: current.apiPort,
        ngrok_auth_token: current.ngrokAuthToken,
        ngrok_region: current.ngrokRegion,
        relay_worker_url: current.relayWorkerUrl,
        theme_mode: current.themeMode,
        transfer_enabled: current.transferEnabled,
        primary_color: current.primaryColor,
        neutral_color: current.neutralColor,
        animation_mode: current.animationMode,
        custom_font_family: current.customFontFamily,
        custom_font_url: current.customFontURL,
      });
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
