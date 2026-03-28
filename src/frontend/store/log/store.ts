import { subscribeWithSelector } from 'zustand/middleware'
import { createWithEqualityFn } from 'zustand/traditional'

import { devtools } from '@/store/middleware/devtools'
import { createSseSlice, type SseAction } from './actions/sse'
import { initialLogState, type LogState } from './initialState'

export type LogStore = LogState & SseAction

export const useLogStore = createWithEqualityFn<LogStore>()(
  subscribeWithSelector(
    devtools(
      (...args) => ({
        ...initialLogState,
        ...createSseSlice(...args),
      }),
      { name: 'coze2jianying/log' },
    ),
  ),
)
