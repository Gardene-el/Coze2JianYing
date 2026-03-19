import apiClient from "../client";
import type {
  ScriptFormatResponse,
  ScriptValidateResponse,
  ScriptExecuteResponse,
} from "../types";

export const guiScriptAPI = {
  format: (script: string) =>
    apiClient
      .post<ScriptFormatResponse>("/gui/script/format", { script })
      .then((r) => r.data),

  validate: (script: string) =>
    apiClient
      .post<ScriptValidateResponse>("/gui/script/validate", { script })
      .then((r) => r.data),

  execute: (script: string) =>
    apiClient
      .post<ScriptExecuteResponse>(
        "/gui/script/execute",
        { script },
        { timeout: 0 },
      )
      .then((r) => r.data),
};
