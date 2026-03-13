/**
 * 连接 /gui/logs/stream SSE 端点，将日志行写入 log store
 */
import { useEffect, useRef } from "react";

import { useLogStore } from "@/store/log/store";

const SSE_URL = `${import.meta.env.VITE_API_BASE ?? "http://localhost:20210"}/gui/logs/stream`;

export function useSSELog() {
  const appendLog = useLogStore((s) => s.appendLog);
  const setStreaming = useLogStore((s) => s.setStreaming);
  const esRef = useRef<EventSource | null>(null);

  useEffect(() => {
    let es: EventSource;

    const connect = () => {
      es = new EventSource(SSE_URL);
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
  }, [appendLog, setStreaming]);
}
