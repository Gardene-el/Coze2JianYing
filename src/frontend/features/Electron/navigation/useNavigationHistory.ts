import { useCallback, useEffect, useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

/**
 * Simple in-page navigation history hook for the Electron desktop app.
 * Provides browser-like back/forward using an in-memory stack.
 * Mirrors the API of lobehub/src/features/Electron/navigation/useNavigationHistory.ts
 * without the dependency on electron-client-ipc or useElectronStore.
 */
export const useNavigationHistory = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const historyRef = useRef<string[]>([location.pathname + location.search]);
  const indexRef = useRef(0);
  /** Set to true while we're performing a programmatic back/forward navigation
   * so the location-change effect does not push a new history entry. */
  const isNavigatingRef = useRef(false);

  const [canGoBack, setCanGoBack] = useState(false);
  const [canGoForward, setCanGoForward] = useState(false);

  // Track real navigations (user-driven route changes) and push them onto the stack.
  useEffect(() => {
    if (isNavigatingRef.current) {
      isNavigatingRef.current = false;
      return;
    }

    const currentUrl = location.pathname + location.search;

    // Don't duplicate the current entry.
    if (historyRef.current[indexRef.current] === currentUrl) return;

    // Discard any forward entries when the user navigates to a new page.
    historyRef.current = historyRef.current.slice(0, indexRef.current + 1);
    historyRef.current.push(currentUrl);
    indexRef.current = historyRef.current.length - 1;

    setCanGoBack(indexRef.current > 0);
    setCanGoForward(false);
  }, [location.pathname, location.search]);

  const goBack = useCallback(() => {
    if (indexRef.current <= 0) return;
    isNavigatingRef.current = true;
    indexRef.current--;
    setCanGoBack(indexRef.current > 0);
    setCanGoForward(true);
    navigate(historyRef.current[indexRef.current]);
  }, [navigate]);

  const goForward = useCallback(() => {
    if (indexRef.current >= historyRef.current.length - 1) return;
    isNavigatingRef.current = true;
    indexRef.current++;
    setCanGoBack(true);
    setCanGoForward(indexRef.current < historyRef.current.length - 1);
    navigate(historyRef.current[indexRef.current]);
  }, [navigate]);

  return { canGoBack, canGoForward, goBack, goForward };
};
