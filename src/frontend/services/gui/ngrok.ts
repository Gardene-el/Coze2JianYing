import apiClient from "../client";
import type { NgrokStartPayload, NgrokStatusResponse } from "../types";

export const guiNgrokAPI = {
  getStatus: () =>
    apiClient.get<NgrokStatusResponse>("/gui/ngrok/status").then((r) => r.data),

  start: (payload: NgrokStartPayload) =>
    apiClient
      .post<NgrokStatusResponse>("/gui/ngrok/start", payload)
      .then((r) => r.data),

  stop: () => apiClient.post("/gui/ngrok/stop").then((r) => r.data),
};
