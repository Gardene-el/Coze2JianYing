import { createWithEqualityFn } from "zustand/traditional";
import { subscribeWithSelector } from "zustand/middleware";

import { devtools } from "@/store/middleware/devtools";
import { initialServiceState, type ServiceState } from "./initialState";
import {
  createServiceManageSlice,
  type ServiceManageAction,
} from "./actions/manage";
import { createNgrokSlice, type NgrokAction } from "./actions/ngrok";
import {
  createCloudflareSlice,
  type CloudflareAction,
} from "./actions/cloudflare";

export type ServiceStore = ServiceState &
  ServiceManageAction &
  NgrokAction &
  CloudflareAction;

export const useServiceStore = createWithEqualityFn<ServiceStore>()(
  subscribeWithSelector(
    devtools(
      (...args) => ({
        ...initialServiceState,
        ...createServiceManageSlice(...args),
        ...createNgrokSlice(...args),
        ...createCloudflareSlice(...args),
      }),
      { name: "coze2jianying/service" },
    ),
  ),
);
