import apiClient from '../client'
import type { DetectPathResponse, SettingsPayload } from '../types'

export const guiSettingsAPI = {
  /** 向 Python backend 推送内存对齐数据（仅 draft_folder + transfer_enabled）。 */
  put: (payload: SettingsPayload) => apiClient.put('/gui/settings', payload).then((r) => r.data),

  detectPath: () =>
    apiClient.post<DetectPathResponse>('/gui/settings/detect-path').then((r) => r.data),
}
