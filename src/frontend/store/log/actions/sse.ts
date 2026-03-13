import type { StateCreator } from "zustand";

import type { LogEntry, LogState } from "../initialState";

const MAX_ENTRIES = 500;
let _counter = 0;

/** 解析 Python logging 格式的一行日志 */
function parseLine(raw: string): LogEntry {
  // 格式: 2026-03-12 10:00:00 - name - LEVEL - message
  const m = raw.match(
    /^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - .+ - (DEBUG|INFO|WARNING|ERROR|CRITICAL) - (.+)$/,
  );
  return {
    id: ++_counter,
    timestamp: m?.[1] ?? new Date().toLocaleTimeString(),
    level: (m?.[2] ?? "INFO") as LogEntry["level"],
    message: m?.[3] ?? raw,
    raw,
  };
}

export interface SseAction {
  appendLog: (raw: string) => void;
  clearLogs: () => void;
  setStreaming: (v: boolean) => void;
  setAutoScroll: (v: boolean) => void;
}

export const createSseSlice: StateCreator<
  LogState & SseAction,
  [],
  [],
  SseAction
> = (set) => ({
  appendLog: (raw) =>
    set((state) => {
      const entries = [...state.entries, parseLine(raw)];
      // 超出上限时丢弃最老的
      return {
        entries:
          entries.length > MAX_ENTRIES ? entries.slice(-MAX_ENTRIES) : entries,
      };
    }),

  clearLogs: () => set({ entries: [] }),

  setStreaming: (v) => set({ isStreaming: v }),

  setAutoScroll: (v) => set({ autoScroll: v }),
});
