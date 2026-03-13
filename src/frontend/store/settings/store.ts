import { createWithEqualityFn } from "zustand/traditional";
import { subscribeWithSelector } from "zustand/middleware";

import { devtools } from "@/store/middleware/devtools";
import { initialSettingsState, type SettingsState } from "./initialState";
import {
  createSettingsPersistSlice,
  type SettingsPersistAction,
} from "./actions/persist";

export type SettingsStore = SettingsState & SettingsPersistAction;

export const useSettingsStore = createWithEqualityFn<SettingsStore>()(
  subscribeWithSelector(
    devtools(
      (...args) => ({
        ...initialSettingsState,
        ...createSettingsPersistSlice(...args),
      }),
      { name: "coze2jianying/settings" },
    ),
  ),
);
