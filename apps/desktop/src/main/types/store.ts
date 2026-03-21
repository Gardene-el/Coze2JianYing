import type {
  DataSyncConfig,
  NetworkProxySettings,
  UpdateChannel,
} from '@lobechat/electron-client-ipc';
import type { TunnelProviderSettings } from '@c2jy/tunnel-core';

export interface ElectronMainStore {
  backendPort: number;
  dataSyncConfig: DataSyncConfig;
  encryptedTokens: {
    accessToken?: string;
    expiresAt?: number;
    lastRefreshAt?: number;
    refreshToken?: string;
  };
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
