/** 可持久化的 UI 状态（对齐 lobehub INITIAL_STATUS 模式） */
export interface SystemStatus {
  /** 当前展开的侧边栏分组 key 列表 */
  expandedSidebarGroups: string[]
}

export const INITIAL_STATUS: SystemStatus = {
  expandedSidebarGroups: ['auto', 'manual', 'legacy'],
}

export interface GlobalState {
  status: SystemStatus
}

export const initialGlobalState: GlobalState = {
  status: INITIAL_STATUS,
}
