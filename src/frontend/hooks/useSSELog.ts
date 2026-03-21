/**
 * 连接 /gui/logs/stream SSE 端点，将日志行写入 log store
 */
import { useEffect, useRef } from "react";

import { useLogStore } from "@/store/log/store";
import { useSettingsStore } from "@/store/settings/store";

export function useSSELog() {
  const appendLog = useLogStore((s) => s.appendLog);
  const setStreaming = useLogStore((s) => s.setStreaming);
  const apiPort = useSettingsStore((s) => s.apiPort);
  const esRef = useRef<EventSource | null>(null);

  const sseUrl = `${
    import.meta.env.VITE_API_BASE ?? `http://localhost:${apiPort || 20211}`
  }/gui/logs/stream`;

  useEffect(() => {
    let es: EventSource;

    const connect = () => {
      es = new EventSource(sseUrl);
      esRef.current = es;

      es.onopen = () => setStreaming(true);

      es.onmessage = (event) => {
        if (event.data) appendLog(event.data);
      };

      es.onerror = () => {
        setStreaming(false);
        es.close();
        // 5 秒后重连
        setTimeout(connect, 5000);
      };
    };

    connect();

    return () => {
      esRef.current?.close();
      setStreaming(false);
    };
  }, [appendLog, setStreaming, sseUrl]);
}
