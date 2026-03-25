/**
 * Path resolver service for GUI settings.
 *
 * This service owns the "effective path" decision logic that used to live in
 * Python's `settings_manager.get_effective_output_path()` /
 * `get_effective_assets_path()` / `detect_default_draft_folder()`.
 *
 * Running in the Electron main process means we have full Node.js `fs` access
 * and can call `app.getPath()` — both unavailable in the renderer.
 *
 * Results are pushed to Python via `PUT /gui/settings` so the Python layer
 * only needs `sm.get("effective_output_path")` — zero decision logic.
 */
import { statSync } from 'node:fs';
import { dirname, join } from 'node:path';

import { app } from 'electron';

import type { GuiSettings } from '@/types/store';

export interface EffectivePaths {
  /** Resolved output (draft) path.  Empty string = Python should use its own fallback. */
  outputPath: string;
  /** Resolved assets base path.  Empty string = Python should use its own fallback. */
  assetsBasePath: string;
}

/** Candidate JianyingPro draft folder templates (Windows only). */
const JIANYING_DRAFT_TEMPLATES = [
  String.raw`C:\Users\{username}\AppData\Local\JianyingPro\User Data\Projects\com.lveditor.draft`,
  String.raw`C:\Users\{username}\AppData\Roaming\JianyingPro\User Data\Projects\com.lveditor.draft`,
];

export class PathResolverService {
  // ─── private helpers ──────────────────────────────────────────────────────

  private isValidDir(p: string): boolean {
    if (!p) return false;
    try {
      return statSync(p).isDirectory();
    } catch {
      return false;
    }
  }

  // ─── public API ───────────────────────────────────────────────────────────

  /**
   * Compute the effective draft output path.
   *
   * Returns the configured `draftFolder` when transfer is enabled and the
   * directory actually exists.  Otherwise returns `""` to signal that Python
   * should fall back to its own `config.drafts_dir`.
   */
  resolveOutputPath(settings: GuiSettings): string {
    if (settings.draftFolder && this.isValidDir(settings.draftFolder)) {
      return settings.draftFolder;
    }
    return '';
  }

  /**
   * Compute the effective assets base path.
   *
   * When transfer is enabled and `draftFolder` is valid, assets are stored in
   * a `CozeJianYingAssistantAssets` sibling directory next to `draftFolder`.
   * Otherwise returns `""` so Python uses `config.assets_dir`.
   */
  resolveAssetsBasePath(settings: GuiSettings): string {
    if (settings.draftFolder && this.isValidDir(settings.draftFolder)) {
      return join(dirname(settings.draftFolder), 'CozeJianYingAssistantAssets');
    }
    return '';
  }

  /** Compute both effective paths in one call (for IPC handler). */
  resolveEffectivePaths(settings: GuiSettings): EffectivePaths {
    return {
      assetsBasePath: this.resolveAssetsBasePath(settings),
      outputPath: this.resolveOutputPath(settings),
    };
  }

  /**
   * Auto-detect the JianyingPro draft folder using well-known Windows paths.
   * Mirrors the Python `detect_default_draft_folder()` logic but uses
   * `app.getPath('home')` which is more reliable than `os.getenv('USERNAME')`.
   */
  detectDefaultDraftFolder(): string | null {
    const homeDir = app.getPath('home');
    // Extract the username from the home directory path (last path segment).
    const username = homeDir.split(/[\\/]/).at(-1) ?? '';

    for (const template of JIANYING_DRAFT_TEMPLATES) {
      const candidate = template.replace('{username}', username);
      if (this.isValidDir(candidate)) {
        return candidate;
      }
    }
    return null;
  }
}

/** Singleton instance — safe to import anywhere in the main process. */
export const pathResolverService = new PathResolverService();
