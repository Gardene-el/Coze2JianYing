import { DEFAULT_GUI_SETTINGS } from '@/const/store'
import { createLogger } from '@/utils/logger'
import { pathResolverService } from '@/utils/pathResolver'

import { ControllerModule, IpcMethod } from './index'

const logger = createLogger('controllers:BackendCtr')

const DEFAULT_PORT = 20211

export interface BackendStatus {
  port: number
  running: boolean
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
  static override readonly groupName = 'backend'

  /** IPC: backend.getPort */
  @IpcMethod()
  getPort(): number {
    return this.app.storeManager.get('backendPort') ?? DEFAULT_PORT
  }

  /** IPC: backend.setPort — persists; takes effect after next start() */
  @IpcMethod()
  setPort(port: number): void {
    this.app.storeManager.set('backendPort', port)
    logger.info(`Backend port updated to ${port} (takes effect on restart)`)
  }

  /** IPC: backend.getStatus */
  @IpcMethod()
  getStatus(): BackendStatus {
    return {
      port: this.app.pythonBackendManager.port,
      running: this.app.pythonBackendManager.isRunning,
    }
  }

  /** IPC: backend.start — reads current stored port, spawns Python */
  @IpcMethod()
  async start(): Promise<BackendStatus> {
    logger.info('start() requested via IPC')
    const port = this.app.storeManager.get('backendPort') ?? DEFAULT_PORT
    await this.app.pythonBackendManager.start(port)

    // After Python is ready, push the persisted GUI settings into Python memory.
    // This handles the case where loadSettings() ran before Python was started
    // (the HTTP PUT failed silently), ensuring draft_folder is always available.
    this.pushGuiSettingsToPython(port).catch((err) => {
      logger.warn('Failed to push GUI settings to Python after start:', err)
    })

    return { port, running: true }
  }

  /**
   * Reads GUI settings from Electron store, resolves effective paths (fs check),
   * and pushes them to the Python backend via PUT /gui/settings.
   */
  private async pushGuiSettingsToPython(port: number): Promise<void> {
    const guiSettings = this.app.storeManager.get('guiSettings') ?? DEFAULT_GUI_SETTINGS
    const effectivePaths = pathResolverService.resolveEffectivePaths(guiSettings)
    const payload = { draft_folder: effectivePaths.draftFolder }
    logger.info(`Pushing GUI settings to Python: draft_folder="${effectivePaths.draftFolder}"`)
    const res = await fetch(`http://127.0.0.1:${port}/gui/settings`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!res.ok) {
      throw new Error(`PUT /gui/settings failed: ${res.status} ${res.statusText}`)
    }
  }

  /** IPC: backend.stop — kills Python process */
  @IpcMethod()
  stop(): BackendStatus {
    logger.info('stop() requested via IPC')
    this.app.pythonBackendManager.stop()
    return { port: this.app.pythonBackendManager.port, running: false }
  }
}
