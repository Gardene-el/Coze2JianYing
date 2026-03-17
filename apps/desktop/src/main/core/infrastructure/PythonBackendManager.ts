import { spawn, spawnSync } from 'node:child_process';
import type { ChildProcess } from 'node:child_process';
import { createHash } from 'node:crypto';
import { existsSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

import { app } from 'electron';

import { isDev } from '@/const/env';
import { createLogger } from '@/utils/logger';

const logger = createLogger('core:PythonBackendManager');

const GUI_PORT = 20210;
const GUI_HOST = '127.0.0.1';
const HEALTH_ENDPOINT = `http://${GUI_HOST}:${GUI_PORT}/gui/health`;
const HEALTH_POLL_MS = 500;
const HEALTH_TIMEOUT_MS = 30_000;

/**
 * Manages the Python FastAPI backend process lifecycle.
 *
 * Both development and production use the CPython Embeddable Package located at
 * apps/desktop/resources/python/ (dev) or resources/python/ (prod).
 *
 * In development, PythonBackendManager automatically rebuilds the embed when the
 * pyproject.toml hash changes (stamp check).  The rebuild is synchronous so the
 * window only opens after the backend is ready.
 *
 * In production the embed is pre-built by `npm run build:backend` and bundled by
 * electron-builder; no automatic rebuild is attempted.
 */
export class PythonBackendManager {
  private process: ChildProcess | null = null;
  private stopped = false;

  /** Monorepo root directory (Coze2JianYing/) */
  private readonly projectRoot: string;

  /** Port the Python GUI backend listens on */
  readonly port = GUI_PORT;

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
   * Ensure the CPython embed is built and up to date.
   * Only runs in development; production embeds are pre-built.
   * Uses spawnSync so the caller blocks until the build finishes.
   */
  private ensureEmbedReady(): void {
    if (!isDev) return;

    const [needs, reason] = this.needsRebuild();
    if (!needs) {
      logger.info(`Embed is ${reason}, skipping build`);
      return;
    }

    logger.info(`Embed needs rebuild: ${reason}`);
    logger.info('Running build_python.py — this may take a few minutes on first run...');

    const buildScript = join(this.projectRoot, 'scripts', 'build_workflow', 'build_python.py');
    const result = spawnSync('python', [buildScript], {
      cwd: this.projectRoot,
      stdio: 'inherit',
      timeout: 600_000, // 10 min upper bound
    });

    if (result.error) {
      throw new Error(
        `Failed to start build_python.py: ${result.error.message}\n` +
          `Make sure 'python' (3.8+) is available on PATH.`,
      );
    }
    if (result.status !== 0) {
      throw new Error(
        `build_python.py exited with code ${result.status}. ` +
          `Check the output above for details.`,
      );
    }

    logger.info('Embed build completed successfully');
  }

  /**
   * Spawn the Python backend and wait until it reports healthy.
   * Returns a Promise that resolves once the process is ready.
   */
  async start(): Promise<void> {
    if (this.process) {
      logger.warn('Python backend already running');
      return;
    }

    // Ensure the CPython embed is present and up to date before spawning.
    this.ensureEmbedReady();

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
    logger.info(`Python backend ready on port ${GUI_PORT}`);
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
      args: ['-m', 'src.main', '--gui-only', '--port', String(GUI_PORT), '--host', GUI_HOST],
      cmd: pythonExe,
      cwd: this.embedDir,
    };
  }

  private async waitForReady(): Promise<void> {
    const deadline = Date.now() + HEALTH_TIMEOUT_MS;

    while (Date.now() < deadline) {
      try {
        const resp = await fetch(HEALTH_ENDPOINT, { signal: AbortSignal.timeout(2000) });
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
