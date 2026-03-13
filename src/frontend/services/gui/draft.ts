import apiClient from "../client";
import type { GenerateDraftResponse } from "../types";

export const guiDraftAPI = {
  generate: (content: string) =>
    apiClient
      .post<GenerateDraftResponse>("/gui/draft/generate", { content })
      .then((r) => r.data),
};
