import type { App } from '@/core/App'

import { WindowsMenu } from './impls/windows'
import type { IMenuPlatform } from './types'

export type { IMenuPlatform, MenuOptions } from './types'

export const createMenuImpl = (app: App): IMenuPlatform => {
  return new WindowsMenu(app)
}
