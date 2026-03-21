import { createLogger } from '@/utils/logger';

import { ControllerModule, IpcMethod } from './index';

const logger = createLogger('controllers:BackendCtr');

const DEFAULT_PORT = 20211;

export interface BackendStatus {
  port: number;
  running: boolean;
}

/**
 * IPC controller for managing the Python backend process.
 *
 * Channel prefix: `backend.*`  (matches groupName = 'backend')
 *
 * Exposed channels:
 *   backend.getPort    — read the stored port (from electron-store)
 *   backend.setPort    — persist a new port (takes effect on next restart)
 *   backend.getStatus  — {running, port} of the live process
 *   backend.start      — spawn / re-spawn the Python process
 *   backend.stop       — kill the Python process
 */
export default class BackendCtr extends ControllerModule {
  static override readonly groupName = 'backend';

  /** IPC: backend.getPort */
  @IpcMethod()
  getPort(): number {
    return this.app.storeManager.get('backendPort') ?? DEFAULT_PORT;
  }

  /** IPC: backend.setPort — persists; takes effect after next start() */
  @IpcMethod()
  setPort(port: number): void {
    this.app.storeManager.set('backendPort', port);
    logger.info(`Backend port updated to ${port} (takes effect on restart)`);
  }

  /** IPC: backend.getStatus */
  @IpcMethod()
  getStatus(): BackendStatus {
    return {
      port: this.app.pythonBackendManager.port,
      running: this.app.pythonBackendManager.isRunning,
    };
  }

  /** IPC: backend.start — reads current stored port, spawns Python */
  @IpcMethod()
  async start(): Promise<BackendStatus> {
    logger.info('start() requested via IPC');
    const port = this.app.storeManager.get('backendPort') ?? DEFAULT_PORT;
    await this.app.pythonBackendManager.start(port);
    return { port, running: true };
  }

  /** IPC: backend.stop — kills Python process */
  @IpcMethod()
  stop(): BackendStatus {
    logger.info('stop() requested via IPC');
    this.app.pythonBackendManager.stop();
    return { port: this.app.pythonBackendManager.port, running: false };
  }
}
