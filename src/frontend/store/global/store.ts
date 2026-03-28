import { subscribeWithSelector } from 'zustand/middleware'
import { shallow } from 'zustand/shallow'
import { createWithEqualityFn } from 'zustand/traditional'

import { devtools } from '@/store/middleware/devtools'
import { createSidebarSlice, type SidebarAction } from './actions/sidebar'
import { type GlobalState, initialGlobalState } from './initialState'

export type GlobalStore = GlobalState & SidebarAction

export const useGlobalStore = createWithEqualityFn<GlobalStore>()(
  subscribeWithSelector(
    devtools(
      (...args) => ({
        ...initialGlobalState,
        ...createSidebarSlice(...args),
      }),
      { name: 'coze2jianying/global' },
    ),
  ),
  shallow,
)
