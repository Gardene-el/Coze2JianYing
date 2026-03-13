import apiClient from "../client";

export const guiReplayAPI = {
  get: (draftId: string) =>
    apiClient
      .get<Record<string, unknown>>(`/gui/replay/${draftId}`)
      .then((r) => r.data),
};
