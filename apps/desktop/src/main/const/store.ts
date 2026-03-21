/**
 * Application settings storage related constants
 */
import type { NetworkProxySettings } from '@lobechat/electron-client-ipc';

import { appStorageDir } from '@/const/dir';
import { UPDATE_CHANNEL } from '@/modules/updater/configs';
import { DEFAULT_SHORTCUTS_CONFIG } from '@/shortcuts';
import type { ElectronMainStore, GuiSettings } from '@/types/store';

/**
 * Storage name
 */
export const STORE_NAME = 'coze2jianying-settings';

export const defaultProxySettings: NetworkProxySettings = {
  enableProxy: false,
  proxyBypass: 'localhost, 127.0.0.1, ::1',
  proxyPort: '',
  proxyRequireAuth: false,
  proxyServer: '',
  proxyType: 'http',
};

/**
 * Storage default values
 */
export const DEFAULT_GUI_SETTINGS: GuiSettings = {
  draftFolder: '',
  transferEnabled: false,
};

export const STORE_DEFAULTS: ElectronMainStore = {
  backendPort: 20211,
  guiSettings: DEFAULT_GUI_SETTINGS,
  locale: 'auto',
  networkProxy: defaultProxySettings,
  shortcuts: DEFAULT_SHORTCUTS_CONFIG,
  storagePath: appStorageDir,
  themeMode: 'system',
  updateChannel: UPDATE_CHANNEL,
  workerUrl: 'https://coze2jianying.pages.dev',
};
