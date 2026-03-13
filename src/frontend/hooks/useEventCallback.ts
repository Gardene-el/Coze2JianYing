/**
 * 直接移植自 lobehub/src/hooks/useEventCallback.ts
 * 返回稳定引用的回调函数（避免无意义的 re-render）
 */
import { useCallback, useInsertionEffect, useRef } from "react";

type AnyFunction = (...args: never[]) => unknown;

export function useEventCallback<Fn extends AnyFunction>(fn: Fn): Fn {
  const ref = useRef<Fn>(fn);

  useInsertionEffect(() => {
    ref.current = fn;
  });

  return useCallback(
    (...args: Parameters<Fn>) => ref.current(...args),
    [],
  ) as Fn;
}
