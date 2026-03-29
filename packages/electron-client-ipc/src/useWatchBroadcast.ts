'use client'

import { useEffect, useLayoutEffect, useRef } from 'react'

import type { MainBroadcastEventKey, MainBroadcastParams } from './events'

interface ElectronAPI {
  ipcRenderer: {
    on: (event: MainBroadcastEventKey, listener: (e: unknown, data: unknown) => void) => void
    removeListener: (
      event: MainBroadcastEventKey,
      listener: (e: unknown, data: unknown) => void,
    ) => void
  }
}

declare global {
  interface Window {
    electron: ElectronAPI
  }
}

export const useWatchBroadcast = <T extends MainBroadcastEventKey>(
  event: T,
  handler: (data: MainBroadcastParams<T>) => void,
) => {
  const handlerRef = useRef<typeof handler>(handler)

  useLayoutEffect(() => {
    handlerRef.current = handler
  }, [handler])

  useEffect(() => {
    if (!window.electron) return

    const listener = (_e: unknown, data: MainBroadcastParams<T>) => {
      handlerRef.current(data)
    }

    window.electron.ipcRenderer.on(event, listener)

    return () => {
      window.electron.ipcRenderer.removeListener(event, listener)
    }
  }, [event])
}
