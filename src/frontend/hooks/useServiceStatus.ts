/**
 * 定期轮询 /gui/service/status，同步到 service store
 */
import { useEffect } from "react";

import { useServiceStore } from "@/store/service/store";

const POLL_INTERVAL = 5000;

export function useServiceStatus() {
  const fetchStatus = useServiceStore((s) => s.fetchStatus);
  const fetchNgrokStatus = useServiceStore((s) => s.fetchNgrokStatus);

  useEffect(() => {
    // 立即拉取一次
    void fetchStatus();
    void fetchNgrokStatus();

    const id = setInterval(() => {
      void fetchStatus();
      void fetchNgrokStatus();
    }, POLL_INTERVAL);

    return () => clearInterval(id);
  }, [fetchStatus, fetchNgrokStatus]);
}
