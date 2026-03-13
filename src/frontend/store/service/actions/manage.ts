import type { StateCreator } from "zustand";

import { guiServiceAPI } from "@/services/gui/service";
import type { ServiceState } from "../initialState";

export interface ServiceManageAction {
  fetchStatus: () => Promise<void>;
  startService: () => Promise<void>;
  stopService: () => Promise<void>;
}

export const createServiceManageSlice: StateCreator<
  ServiceState & ServiceManageAction & NgrokAction,
  [],
  [],
  ServiceManageAction
> = (set) => ({
  fetchStatus: async () => {
    try {
      const data = await guiServiceAPI.getStatus();
      set({ isRunning: data.running, port: data.port });
    } catch {
      // 服务可能还没启动，静默处理
    }
  },

  startService: async () => {
    set({ isLoading: true });
    try {
      await guiServiceAPI.start();
      set({ isRunning: true });
    } finally {
      set({ isLoading: false });
    }
  },

  stopService: async () => {
    set({ isLoading: true });
    try {
      await guiServiceAPI.stop();
      set({ isRunning: false, ngrokRunning: false, ngrokUrl: "" });
    } finally {
      set({ isLoading: false });
    }
  },
});

// forward-declare NgrokAction to avoid circular import
import type { NgrokAction } from "./ngrok";
