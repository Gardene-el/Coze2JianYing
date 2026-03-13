/** 所有 /gui/* API 的响应类型 */

export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  message?: string;
}

export interface SettingsPayload {
  draft_folder?: string;
  api_port?: string;
  ngrok_auth_token?: string;
  ngrok_region?: string;
  relay_worker_url?: string;
  theme_mode?: string;
  transfer_enabled?: boolean;
  // ——— 主题定制（对齐 LobeChat）———
  primary_color?: string;
  neutral_color?: string;
  animation_mode?: string;
  custom_font_family?: string;
  custom_font_url?: string;
}

export interface ServiceStatusResponse {
  running: boolean;
  port: number;
}

export interface NgrokStartPayload {
  authtoken: string;
  region: string;
  port: number;
}

export interface NgrokStatusResponse {
  running: boolean;
  public_url?: string;
}

export interface NgrokStartResponse {
  public_url: string;
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
