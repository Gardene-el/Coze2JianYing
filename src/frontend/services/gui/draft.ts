import apiClient from "../client";
import type { GenerateDraftResponse } from "../types";

export const guiDraftAPI = {
  generate: (content: string) =>
    apiClient
      .post<GenerateDraftResponse>(
        "/gui/draft/generate",
        { content },
        { timeout: 0 },
      )
      .then((r) => r.data),
};
