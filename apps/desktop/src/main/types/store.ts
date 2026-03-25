import type {
  NetworkProxySettings,
  UpdateChannel,
} from '@lobechat/electron-client-ipc';
import type { TunnelProviderSettings } from '@c2jy/tunnel-core';

export interface GuiSettings {
  draftFolder: string;
}

export interface EffectivePaths {
  /** Resolved draft output path.  Empty string = use Python's config.drafts_dir fallback. */
  outputPath: string;
  /** Resolved assets base path.  Empty string = use Python's config.assets_dir fallback. */
  assetsBasePath: string;
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
