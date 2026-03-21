/** 所有 /gui/* API 的响应类型 */

export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  message?: string;
}

/** 仅包含 Python backend 实际使用的字段（草稿路径 + 传输开关 + 预计算的有效路径） */
export interface SettingsPayload {
  draft_folder?: string;
  effective_assets_base_path?: string;
  effective_output_path?: string;
  transfer_enabled?: boolean;
}

export interface ServiceStatusResponse {
  running: boolean;
  port: number;
}

export interface DetectPathResponse {
  path: string | null;
}

export interface GenerateDraftResponse {
  paths: string[];
}

export interface ScriptFormatResponse {
  formatted: string;
}

export interface ScriptValidateResponse {
  valid: boolean;
  error?: string;
}

export interface ScriptExecuteResponse {
  ok: boolean;
}

export interface ScriptExecutePayload {
  script: string;
}
