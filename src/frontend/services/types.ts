/** 所有 /gui/* API 的响应类型 */

export interface ApiResponse<T = unknown> {
  success: boolean
  data?: T
  message?: string
}

/** 仅包含 Python backend 实际使用的字段 */
export interface SettingsPayload {
  draft_folder?: string
}

export interface ServiceStatusResponse {
  running: boolean
  port: number
}

export interface DetectPathResponse {
  path: string | null
}

export interface GenerateDraftResponse {
  paths: string[]
}

export interface ScriptFormatResponse {
  formatted: string
}

export interface ScriptValidateResponse {
  valid: boolean
  error?: string
}

export interface ScriptExecuteResponse {
  ok: boolean
}

export interface ScriptExecutePayload {
  script: string
}
