import type {
  NetworkProxySettings,
  UpdateChannel,
} from '@lobechat/electron-client-ipc';
import type { TunnelProviderSettings } from '@c2jy/tunnel-core';

export interface GuiSettings {
  draftFolder: string;
}

export interface EffectivePaths {
  /** Resolved draft folder path.  Empty string = use Python's config.drafts_dir fallback. */
  draftFolder: string;
}

export interface ElectronMainStore {
  backendPort: number;
  guiSettings: GuiSettings;
  locale: string;
  networkProxy: NetworkProxySettings;
  shortcuts: Record<string, string>;
  storagePath: string;
  themeMode: 'dark' | 'light' | 'system';
  tunnelSettings?: TunnelProviderSettings;
  updateChannel: UpdateChannel;
  workerUrl: string;
}

export type StoreKey = keyof ElectronMainStore;
