import type { StateCreator } from "zustand";

import { guiNgrokAPI } from "@/services/gui/ngrok";
import type { ServiceState } from "../initialState";

export interface NgrokAction {
  startNgrok: (
    authtoken: string,
    region: string,
    port: number,
  ) => Promise<string>;
  stopNgrok: () => Promise<void>;
  fetchNgrokStatus: () => Promise<void>;
}

export const createNgrokSlice: StateCreator<
  ServiceState & NgrokAction,
  [],
  [],
  NgrokAction
> = (set) => ({
  startNgrok: async (authtoken, region, port) => {
    set({ ngrokLoading: true });
    try {
      const data = await guiNgrokAPI.start({ authtoken, region, port });
      const url = data.public_url ?? "";
      set({ ngrokRunning: true, ngrokUrl: url });
      return url;
    } finally {
      set({ ngrokLoading: false });
    }
  },

  stopNgrok: async () => {
    set({ ngrokLoading: true });
    try {
      await guiNgrokAPI.stop();
      set({ ngrokRunning: false, ngrokUrl: "" });
    } finally {
      set({ ngrokLoading: false });
    }
  },

  fetchNgrokStatus: async () => {
    try {
      const data = await guiNgrokAPI.getStatus();
      set({ ngrokRunning: data.running, ngrokUrl: data.public_url ?? "" });
    } catch {
      // 静默处理
    }
  },
});
