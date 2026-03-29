import apiClient from '../client'

export interface ReplayExecuteResponse {
  ok: boolean
  calls_executed: number
  message?: string
}

/**
 * 粘贴id执行服务 — 将 Worker 录制数据转发给本地 Python 后端执行。
 * 调用前需确保后端已启动（useEnsureBackend）。
 */
export const guiReplayAPI = {
  execute: (workerUrl: string, draftId: string) =>
    apiClient
      .post<ReplayExecuteResponse>(
        '/gui/replay/execute',
        { worker_url: workerUrl, draft_id: draftId },
        { timeout: 0 },
      )
      .then((r) => r.data),
}
