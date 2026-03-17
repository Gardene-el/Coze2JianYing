import type { StateCreator } from "zustand";

import { ngrokTunnelService } from "@/services/tunnels/ngrok";
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
      const data = await ngrokTunnelService.startTunnel(port, {
        authToken: authtoken,
        region,
      });
      const url = data.publicUrl ?? "";
      set({ ngrokRunning: true, ngrokUrl: url });
      return url;
    } finally {
      set({ ngrokLoading: false });
    }
  },

  stopNgrok: async () => {
    set({ ngrokLoading: true });
    try {
      await ngrokTunnelService.stopTunnel();
      set({ ngrokRunning: false, ngrokUrl: "" });
    } finally {
      set({ ngrokLoading: false });
    }
  },

  fetchNgrokStatus: async () => {
    try {
      const data = await ngrokTunnelService.getStatus();
      set({ ngrokRunning: data.isRunning, ngrokUrl: data.publicUrl ?? "" });
    } catch {
      // 静默处理
    }
  },
});
