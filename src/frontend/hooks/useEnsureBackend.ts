import { useCallback, useEffect, useRef, useState } from 'react';

import { guiServiceAPI } from '@/services/gui/service';

/**
 * Ensures the Python backend is running before a tool operation begins,
 * and automatically stops it when the component unmounts — but only if
 * this hook instance was the one that started it.
 *
 * This guarantees that tool pages (DraftGenerator, ScriptExecutor, etc.)
 * are independent: they start the backend on demand and clean up after
 * themselves, without interfering with the CloudService (直连模式) page
 * which manages the backend manually.
 *
 * Usage:
 *   const { ensureReady, isPreparing, isReady } = useEnsureBackend();
 *   // In your handler, before calling any Python API:
 *   await ensureReady();
 */
export function useEnsureBackend() {
  const [isReady, setIsReady] = useState(false);
  const [isPreparing, setIsPreparing] = useState(false);

  // Ref-based guards — safe to read in async callbacks without stale-closure issues.
  const isReadyRef = useRef(false);
  const preparingRef = useRef(false);
  // True only if THIS hook instance called start() — determines unmount cleanup.
  const weStartedBackend = useRef(false);

  const ensureReady = useCallback(async () => {
    // Idempotent: skip if already ready or a concurrent prepare is in flight.
    if (isReadyRef.current || preparingRef.current) return;

    preparingRef.current = true;
    setIsPreparing(true);

    try {
      const { running } = await guiServiceAPI.getStatus();
      if (!running) {
        await guiServiceAPI.start();
        weStartedBackend.current = true;
      }
      isReadyRef.current = true;
      setIsReady(true);
    } finally {
      preparingRef.current = false;
      setIsPreparing(false);
    }
    // Errors are intentionally not caught here — callers display the error message.
  }, []);

  useEffect(() => {
    return () => {
      // On unmount: only stop the backend if we started it.
      // This prevents tool pages from killing the CloudService (直连模式) backend.
      if (weStartedBackend.current) {
        void guiServiceAPI.stop();
      }
    };
  }, []);

  return { ensureReady, isPreparing, isReady };
}
