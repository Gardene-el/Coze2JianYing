/** Worker 直连回放服务 — 直接向 Cloudflare Worker 发出请求，不经过本地 Python 后端 */

export interface WorkerRecordedCall {
  id: string;
  action: string;
  method: string;
  path: string;
  payload_json: string | null;
  owner_draft_id: string | null;
  owner_segment_id: string | null;
  produced_virtual_id: string | null;
  produced_id_type: string | null;
  created_at: number;
}

export interface WorkerReplayResult {
  virtual_draft_id: string;
  total: number;
  segment_ids: string[];
  calls: WorkerRecordedCall[];
}

export const workerReplayAPI = {
  get: async (
    workerUrl: string,
    draftId: string,
  ): Promise<WorkerReplayResult> => {
    const base = workerUrl.replace(/\/$/, "");
    const res = await fetch(`${base}/replay/${encodeURIComponent(draftId)}`);
    if (!res.ok) {
      const text = await res.text().catch(() => "");
      throw new Error(`Worker 响应 ${res.status}${text ? `: ${text}` : ""}`);
    }
    const json = (await res.json()) as {
      code: number;
      message: string;
    } & WorkerReplayResult;
    if (json.code !== 0) throw new Error(json.message ?? "Worker 返回错误");
    return json;
  },
};
