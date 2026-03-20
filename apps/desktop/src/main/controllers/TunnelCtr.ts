import type {
  NgrokSettings,
  StartTunnelPayload,
  TunnelProviderPayload,
  TunnelSettingsPayload,
  TunnelStatus,
} from '@c2jy/tunnel-core';

import { createLogger } from '@/utils/logger';

import { ControllerModule, IpcMethod } from './index';
import { tunnelRegistry } from '../modules/tunnels/TunnelRegistry';

const logger = createLogger('controllers:TunnelCtr');

export default class TunnelCtr extends ControllerModule {
  static override readonly groupName = 'tunnel';

  /** IPC: tunnel.getStatus */
  @IpcMethod()
  async getStatus({ provider }: TunnelProviderPayload): Promise<TunnelStatus> {
    logger.debug(`getStatus(${provider})`);
    return tunnelRegistry.get(provider).getStatus();
  }

  /**
   * IPC: tunnel.startTunnel
   * Merges persisted settings with any overrides supplied by the caller.
   */
  @IpcMethod()
  async startTunnel({ provider, port, settings: overrides }: StartTunnelPayload): Promise<TunnelStatus> {
    logger.info(`startTunnel(${provider}, port=${port})`);

    const stored = this.app.storeManager.get('tunnelSettings') ?? {};
    const base = (stored[provider] ?? {}) as Partial<NgrokSettings>;
    const merged = { ...base, ...overrides } as NgrokSettings;

    const publicUrl = await tunnelRegistry.get(provider).startTunnel(port, merged);
    return { isRunning: true, publicUrl };
  }

  /** IPC: tunnel.stopTunnel */
  @IpcMethod()
  async stopTunnel({ provider }: TunnelProviderPayload): Promise<TunnelStatus> {
    logger.info(`stopTunnel(${provider})`);
    await tunnelRegistry.get(provider).stopTunnel();
    return { isRunning: false };
  }

  /** IPC: tunnel.getSettings */
  @IpcMethod()
  async getSettings({ provider }: TunnelProviderPayload) {
    logger.debug(`getSettings(${provider})`);
    const stored = this.app.storeManager.get('tunnelSettings') ?? {};
    return stored[provider] ?? null;
  }

  /** IPC: tunnel.saveSettings */
  @IpcMethod()
  async saveSettings({ provider, settings }: TunnelSettingsPayload): Promise<void> {
    logger.info(`saveSettings(${provider})`);
    const current = this.app.storeManager.get('tunnelSettings') ?? {};
    this.app.storeManager.set('tunnelSettings', { ...current, [provider]: settings });
  }

  /** IPC: tunnel.getWorkerUrl */
  @IpcMethod()
  async getWorkerUrl(): Promise<string> {
    logger.debug('getWorkerUrl');
    return this.app.storeManager.get('workerUrl') ?? '';
  }

  /** IPC: tunnel.setWorkerUrl */
  @IpcMethod()
  async setWorkerUrl(url: string): Promise<void> {
    logger.debug(`setWorkerUrl(${url})`);
    this.app.storeManager.set('workerUrl', url);
  }
}
