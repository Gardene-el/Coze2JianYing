import apiClient from "../client";
import type { ServiceStatusResponse } from "../types";

export const guiServiceAPI = {
  getStatus: () =>
    apiClient
      .get<ServiceStatusResponse>("/gui/service/status")
      .then((r) => r.data),

  start: (port?: number) =>
    apiClient.post("/gui/service/start", { port }).then((r) => r.data),

  stop: () => apiClient.post("/gui/service/stop").then((r) => r.data),
};
