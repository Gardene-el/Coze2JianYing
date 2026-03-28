import type { StateCreator } from 'zustand'

import type { GlobalState, SystemStatus } from '../initialState'

export interface SidebarAction {
  /** 通用 UI 状态更新（对齐 lobehub updateSystemStatus 模式） */
  updateSystemStatus: (patch: Partial<SystemStatus>) => void
}

export const createSidebarSlice: StateCreator<
  GlobalState & SidebarAction,
  [],
  [],
  SidebarAction
> = (set, get) => ({
  updateSystemStatus: (patch) => {
    set({ status: { ...get().status, ...patch } })
  },
})
