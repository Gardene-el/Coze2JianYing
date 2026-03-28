import { DEFAULT_GUI_SETTINGS } from '@/const/store'
import type { EffectivePaths, GuiSettings } from '@/types/store'
import { createLogger } from '@/utils/logger'
import { pathResolverService } from '@/utils/pathResolver'

import { ControllerModule, IpcMethod } from './index'

const logger = createLogger('controllers:GuiSettingsCtr')

/**
 * IPC controller for persisting GUI settings in electron-store.
 *
 * Channel prefix: `guiSettings.*`  (matches groupName = 'guiSettings')
 *
 * Exposed channels:
 *   guiSettings.getGuiSettings          — read the full GuiSettings object
 *   guiSettings.setGuiSettings          — merge a partial patch into the stored GuiSettings
 *   guiSettings.resolveEffectivePaths   — compute effective output / assets paths (fs check)
 *   guiSettings.detectDefaultDraftFolder — auto-detect JianyingPro draft folder
 */
export default class GuiSettingsCtr extends ControllerModule {
  static override readonly groupName = 'guiSettings'

  /** IPC: guiSettings.getGuiSettings */
  @IpcMethod()
  getGuiSettings(): GuiSettings {
    return this.app.storeManager.get('guiSettings') ?? DEFAULT_GUI_SETTINGS
  }

  /** IPC: guiSettings.setGuiSettings — merges patch into existing value */
  @IpcMethod()
  setGuiSettings(patch: Partial<GuiSettings>): void {
    const current = this.app.storeManager.get('guiSettings') ?? DEFAULT_GUI_SETTINGS
    const merged: GuiSettings = { ...current, ...patch }
    this.app.storeManager.set('guiSettings', merged)
    logger.debug('GuiSettings updated:', Object.keys(patch))
  }

  /**
   * IPC: guiSettings.resolveEffectivePaths
   *
   * Runs an `fs.statSync` check on the configured draft folder and returns
   * the effective output / assets base paths.  Empty string means Python
   * should use its own `config.drafts_dir` / `config.assets_dir` fallback.
   */
  @IpcMethod()
  resolveEffectivePaths(settings: GuiSettings): EffectivePaths {
    return pathResolverService.resolveEffectivePaths(settings)
  }

  /**
   * IPC: guiSettings.detectDefaultDraftFolder
   *
   * Auto-detects the JianyingPro draft folder from well-known Windows paths.
   * Returns the first valid directory, or `null` if none found.
   */
  @IpcMethod()
  detectDefaultDraftFolder(): string | null {
    return pathResolverService.detectDefaultDraftFolder()
  }
}
