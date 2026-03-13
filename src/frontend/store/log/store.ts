import { createWithEqualityFn } from "zustand/traditional";
import { subscribeWithSelector } from "zustand/middleware";

import { devtools } from "@/store/middleware/devtools";
import { initialLogState, type LogState } from "./initialState";
import { createSseSlice, type SseAction } from "./actions/sse";

export type LogStore = LogState & SseAction;

export const useLogStore = createWithEqualityFn<LogStore>()(
  subscribeWithSelector(
    devtools(
      (...args) => ({
        ...initialLogState,
        ...createSseSlice(...args),
      }),
      { name: "coze2jianying/log" },
    ),
  ),
);
