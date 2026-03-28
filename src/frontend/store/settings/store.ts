import { subscribeWithSelector } from 'zustand/middleware'
import { createWithEqualityFn } from 'zustand/traditional'

import { devtools } from '@/store/middleware/devtools'
import { createSettingsPersistSlice, type SettingsPersistAction } from './actions/persist'
import { initialSettingsState, type SettingsState } from './initialState'

export type SettingsStore = SettingsState & SettingsPersistAction

export const useSettingsStore = createWithEqualityFn<SettingsStore>()(
  subscribeWithSelector(
    devtools(
      (...args) => ({
        ...initialSettingsState,
        ...createSettingsPersistSlice(...args),
      }),
      { name: 'coze2jianying/settings' },
    ),
  ),
)
