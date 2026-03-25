import { spawn } from 'node:child_process';
import type { ChildProcess } from 'node:child_process';
import { createHash } from 'node:crypto';
import { existsSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

import { app } from 'electron';

import { isDev } from '@/const/env';
import { createLogger } from '@/utils/logger';

const logger = createLogger('core:PythonBackendManager');

const DEFAULT_PORT = 20211;
const GUI_HOST = '127.0.0.1';
const HEALTH_POLL_MS = 500;
const HEALTH_TIMEOUT_MS = 30_000;

/**
 * Manages the Python FastAPI backend process lifecycle.
 *
 * Both development and production use the CPython Embeddable Package located at
 * apps/desktop/resources/python/ (dev) or resources/python/ (prod).
 *
 * In development, PythonBackendManager checks that the CPython embed exists and
 * logs a warning when the pyproject.toml stamp is stale, but does NOT trigger a
 * rebuild at runtime.  Rebuilding is the responsibility of the build scripts:
 *   npm run build:backend        — full rebuild
 *   npm run build:backend:quick  — skip if python.exe already exists (used by dev:quick)
 *
 * In production the embed is pre-built by `npm run build:backend` and bundled by
 * electron-builder; no rebuild is attempted.
 */
export class PythonBackendManager {
  private process: ChildProcess | null = null;
  private stopped = false;
  private _port: number = DEFAULT_PORT;
  /** True once the CPython embed has been verified / built for this app session. */
  private embedReady = false;

  /** Monorepo root directory (Coze2JianYing/) */
  private readonly projectRoot: string;

  /** Port the Python backend is currently running on (or will use on next start). */
  get port(): number {
    return this._port;
  }

  /** True while the Python process is alive. */
  get isRunning(): boolean {
    return this.process !== null;
  }

  constructor() {
    // apps/desktop -> apps -> monorepo root
    this.projectRoot = join(app.getAppPath(), '..', '..');
    logger.debug(`Python project root: ${this.projectRoot}`);
  }

  /** Directory that contains python.exe + Lib/site-packages */
  private get embedDir(): string {
    if (isDev) return join(app.getAppPath(), 'resources', 'python');
    return join(process.resourcesPath, 'python');
  }

  /** Full path to the embedded python.exe */
  private get embedPythonExe(): string {
    return join(this.embedDir, 'python.exe');
  }

  /** Compute the log directory passed to Python via COZE2JY_LOG_DIR env var */
  private get logDir(): string {
    if (isDev) return join(this.projectRoot, 'logs');
    return join(process.resourcesPath, 'python', 'logs');
  }

  /**
   * Compute the expected stamp string for the current pyproject.toml.
   * Must match the format written by scripts/build_workflow/build_python.py.
   */
  private computeStamp(): string {
    const pyprojectPath = join(this.projectRoot, 'pyproject.toml');
    const hash = createHash('sha256').update(readFileSync(pyprojectPath)).digest('hex');
    // PYTHON_VERSION mirrors the value in build_python.py; bump both together.
    return `python_version=3.12.9\nhash=${hash}\n`;
  }

  /**
   * Check whether the embed needs to be (re)built.
   * Returns [needsBuild, reason].
   */
  private needsRebuild(): [boolean, string] {
    if (!existsSync(this.embedPythonExe)) return [true, 'python.exe missing'];
    const stampPath = join(this.embedDir, '.stamp');
    if (!existsSync(stampPath)) return [true, '.stamp missing'];
    const existing = readFileSync(stampPath, 'utf8');
    if (existing !== this.computeStamp()) return [true, 'stamp mismatch (dependencies changed)'];
    return [false, 'up to date'];
  }

  /**
   * Verify the CPython embed exists before starting the backend process.
   * Only runs in development (production embeds are pre-bundled by electron-builder).
   *
   * Rebuild is intentionally NOT triggered here — that is the job of the build
   * scripts (build:backend / build:backend:quick / dev:quick).  Doing a rebuild
   * inside start() would silently block the app for up to 10 minutes whenever
   * the Electron main process hot-reloads and pyproject.toml has changed.
   */
  private ensureEmbedReady(): void {
    if (!isDev) return;

    if (!existsSync(this.embedPythonExe)) {
      throw new Error(
        `Embedded python.exe not found at: ${this.embedPythonExe}\n` +
          `Run 'npm run build:backend' (or use 'bun run dev:quick') to build the CPython embed first.`,
      );
    }

    // Stamp check: only warn when dependencies appear stale, never auto-rebuild.
    const [stale, reason] = this.needsRebuild();
    if (stale) {
      logger.warn(
        `Python embed may be outdated (${reason}). ` +
          `Run 'npm run build:backend' to rebuild. Continuing with the existing embed.`,
      );
    } else {
      logger.info(`Python embed stamp is up to date`);
    }
  }

  /**
   * Spawn the Python backend and wait until it reports healthy.
   * @param port  Port to listen on; defaults to the current stored port.
   * Returns a Promise that resolves once the process is ready.
   */
  async start(port?: number): Promise<void> {
    if (this.process) {
      logger.warn('Python backend already running');
      return;
    }
    if (port !== undefined) this._port = port;
    this.stopped = false;

    // Ensure the CPython embed is present and up to date.
    // Only runs once per app session — subsequent UI-driven restarts skip this
    // to avoid re-running the stamp check (and a potential rebuild).
    if (!this.embedReady) {
      this.ensureEmbedReady();
      this.embedReady = true;
    }

    const { cmd, args, cwd } = this.resolveSpawnConfig();
    logger.info(`Starting Python backend: ${cmd} ${args.join(' ')} (cwd: ${cwd})`);

    this.process = spawn(cmd, args, {
      cwd,
      env: { ...process.env, COZE2JY_LOG_DIR: this.logDir },
      stdio: ['ignore', 'pipe', 'pipe'],
    });

    this.process.stdout?.on('data', (data: Buffer) => {
      for (const line of data.toString().split('\n')) {
        if (line.trim()) logger.debug(`[python] ${line.trim()}`);
      }
    });

    this.process.stderr?.on('data', (data: Buffer) => {
      for (const line of data.toString().split('\n')) {
        if (line.trim()) logger.warn(`[python:err] ${line.trim()}`);
      }
    });

    this.process.on('error', (err) => {
      logger.error('Python process error:', err);
    });

    this.process.on('exit', (code, signal) => {
      if (!this.stopped) {
        logger.warn(`Python process exited unexpectedly (code=${code}, signal=${signal})`);
      }
      this.process = null;
    });

    // Wait for the health endpoint to become available
    await this.waitForReady();
    logger.info(`Python backend ready on port ${this._port}`);
  }

  /** Kill the Python process if running. */
  stop(): void {
    this.stopped = true;
    if (!this.process) return;

    logger.info('Stopping Python backend');
    try {
      spawn('taskkill', ['/pid', String(this.process.pid), '/f', '/t']);
    } catch (err) {
      logger.warn('Error stopping Python process:', err);
    }
    this.process = null;
  }

  // ---------------------------------------------------------------------------

  private resolveSpawnConfig(): { args: string[]; cmd: string; cwd: string } {
    const pythonExe = this.embedPythonExe;

    if (!existsSync(pythonExe)) {
      // Should never happen in production (embed is pre-bundled).
      // In dev this means ensureEmbedReady() failed silently — surface a clear error.
      throw new Error(
        `Embedded python.exe not found at: ${pythonExe}\n` +
          `Run 'npm run build:backend' from apps/desktop to build the CPython embed.`,
      );
    }

    return {
      args: ['-m', 'src.main', '--gui-only', '--port', String(this._port), '--host', GUI_HOST],
      cmd: pythonExe,
      cwd: this.embedDir,
    };
  }

  private async waitForReady(): Promise<void> {
    const healthEndpoint = `http://${GUI_HOST}:${this._port}/gui/health`;
    const deadline = Date.now() + HEALTH_TIMEOUT_MS;

    while (Date.now() < deadline) {
      try {
        const resp = await fetch(healthEndpoint, { signal: AbortSignal.timeout(2000) });
        if (resp.ok) return;
      } catch {
        // not yet ready
      }

      if (!this.process) {
        throw new Error('Python backend process exited before becoming healthy');
      }

      await new Promise((r) => setTimeout(r, HEALTH_POLL_MS));
    }

    throw new Error(
      `Python backend did not become healthy within ${HEALTH_TIMEOUT_MS / 1000}s`,
    );
  }
}
