import { shallow } from "zustand/shallow";
import { createWithEqualityFn } from "zustand/traditional";
import { subscribeWithSelector } from "zustand/middleware";

import { devtools } from "@/store/middleware/devtools";
import { initialGlobalState, type GlobalState } from "./initialState";
import { createSidebarSlice, type SidebarAction } from "./actions/sidebar";

export type GlobalStore = GlobalState & SidebarAction;

export const useGlobalStore = createWithEqualityFn<GlobalStore>()(
  subscribeWithSelector(
    devtools(
      (...args) => ({
        ...initialGlobalState,
        ...createSidebarSlice(...args),
      }),
      { name: "coze2jianying/global" },
    ),
  ),
  shallow,
);
