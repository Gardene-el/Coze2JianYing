import { subscribeWithSelector } from 'zustand/middleware'
import { createWithEqualityFn } from 'zustand/traditional'

import { devtools } from '@/store/middleware/devtools'
import { type CloudflareAction, createCloudflareSlice } from './actions/cloudflare'
import { createServiceManageSlice, type ServiceManageAction } from './actions/manage'
import { createNgrokSlice, type NgrokAction } from './actions/ngrok'
import { initialServiceState, type ServiceState } from './initialState'

export type ServiceStore = ServiceState & ServiceManageAction & NgrokAction & CloudflareAction

export const useServiceStore = createWithEqualityFn<ServiceStore>()(
  subscribeWithSelector(
    devtools(
      (...args) => ({
        ...initialServiceState,
        ...createServiceManageSlice(...args),
        ...createNgrokSlice(...args),
        ...createCloudflareSlice(...args),
      }),
      { name: 'coze2jianying/service' },
    ),
  ),
)
