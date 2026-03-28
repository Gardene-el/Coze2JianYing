import { join } from 'node:path'

import { app } from 'electron'

export const mainDir = join(__dirname)

export const preloadDir = join(mainDir, '../preload')

// In packaged mode: reads from inside the asar (files config maps assets/electron/resources → resources/)
// In dev mode: reads directly from the workspace assets directory
export const resourcesDir = app.isPackaged
  ? join(mainDir, '../../resources')
  : join(mainDir, '../../../../assets/electron/resources')

// In packaged mode: build/ assets are only used during build, not at runtime
// In dev mode: reads from workspace assets directory (e.g. icon-dev.ico for window icon)
export const buildDir = app.isPackaged
  ? join(mainDir, '../../build')
  : join(mainDir, '../../../../assets/electron/build')

export const binDir = app.isPackaged
  ? join(process.resourcesPath, 'bin')
  : join(mainDir, '../../resources/bin')

const appPath = app.getAppPath()

export const rendererDir = join(appPath, 'dist', 'renderer')

export const userDataDir = app.getPath('userData')

export const appStorageDir = join(userDataDir, 'coze2jianying-storage')

// Legacy local database directory used in older desktop versions
export const legacyLocalDbDir = join(appStorageDir, 'lobehub-local-db')

// ------  Application storage directory ---- //

// Local storage files (simulating S3)
export const FILE_STORAGE_DIR = 'file-storage'
// Plugin installation directory
export const INSTALL_PLUGINS_DIR = 'plugins'

// Desktop file service
export const LOCAL_STORAGE_URL_PREFIX = '/lobe-desktop-file'
