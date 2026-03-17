import type { GlobalStore } from "../store";
import { INITIAL_STATUS } from "../initialState";

export const systemStatusSelectors = {
  /** 返回当前所有展开的分组 key 数组（带默认值，对齐 lobehub sessionGroupKeys 模式） */
  expandedSidebarGroups: (s: GlobalStore): string[] =>
    s.status.expandedSidebarGroups ?? INITIAL_STATUS.expandedSidebarGroups,

  /** 返回指定分组是否处于展开状态（curry 形式，适合 useGlobalStore 订阅） */
  isGroupExpanded:
    (key: string) =>
    (s: GlobalStore): boolean =>
      (
        s.status.expandedSidebarGroups ?? INITIAL_STATUS.expandedSidebarGroups
      ).includes(key),
};
