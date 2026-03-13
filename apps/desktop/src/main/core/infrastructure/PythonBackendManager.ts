import { spawn } from 'node:child_process';
import type { ChildProcess } from 'node:child_process';
import { existsSync } from 'node:fs';
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
 * In development, spawns `python -m src.main --gui-only --port 20210` from the
 * monorepo root (two levels up from the Electron app directory).
 * In production the binary or venv should be co-located under resources/python/.
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

  /**
   * Spawn the Python backend and wait until it reports healthy.
   * Returns a Promise that resolves once the process is ready.
   */
  async start(): Promise<void> {
    if (this.process) {
      logger.warn('Python backend already running');
      return;
    }

    const { cmd, args, cwd } = this.resolveSpawnConfig();
    logger.info(`Starting Python backend: ${cmd} ${args.join(' ')} (cwd: ${cwd})`);

    this.process = spawn(cmd, args, {
      cwd,
      env: { ...process.env },
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
      if (process.platform === 'win32') {
        spawn('taskkill', ['/pid', String(this.process.pid), '/f', '/t']);
      } else {
        this.process.kill('SIGTERM');
      }
    } catch (err) {
      logger.warn('Error stopping Python process:', err);
    }
    this.process = null;
  }

  // ---------------------------------------------------------------------------

  private resolveSpawnConfig(): { args: string[]; cmd: string; cwd: string } {
    if (isDev) {
      // In development, run from the monorepo root using the system python
      const cwd = this.projectRoot;
      const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';
      return {
        args: ['-m', 'src.main', '--gui-only', '--port', String(GUI_PORT), '--host', GUI_HOST],
        cmd: pythonCmd,
        cwd,
      };
    }

    // In production, look for a bundled python executable under resources/
    const resourcesDir = process.resourcesPath;
    const bundledPython = join(
      resourcesDir,
      'python',
      process.platform === 'win32' ? 'python.exe' : 'python3',
    );

    if (existsSync(bundledPython)) {
      return {
        args: ['-m', 'src.main', '--gui-only', '--port', String(GUI_PORT), '--host', GUI_HOST],
        cmd: bundledPython,
        cwd: join(resourcesDir, 'python'),
      };
    }

    // Fallback: system python from project root
    logger.warn('Bundled Python not found, falling back to system python');
    const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';
    return {
      args: ['-m', 'src.main', '--gui-only', '--port', String(GUI_PORT), '--host', GUI_HOST],
      cmd: pythonCmd,
      cwd: this.projectRoot,
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
