import apiClient from "../client";
import type { DetectPathResponse, SettingsPayload } from "../types";

export const guiSettingsAPI = {
  get: () =>
    apiClient.get<SettingsPayload>("/gui/settings").then((r) => r.data),

  put: (payload: SettingsPayload) =>
    apiClient.put("/gui/settings", payload).then((r) => r.data),

  detectPath: () =>
    apiClient
      .post<DetectPathResponse>("/gui/settings/detect-path")
      .then((r) => r.data),
};
