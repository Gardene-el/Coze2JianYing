/**
 * Cloudflare Tunnel provider — wraps the `cloudflared` npm package (v0.7+).
 *
 * Two modes depending on whether a `token` is supplied:
 *   - Quick tunnel (token empty): no Cloudflare account needed — gets a
 *     *.trycloudflare.com URL via `Tunnel.quick(url)`.
 *   - Named tunnel (token non-empty): persistent domain configured in the
 *     Cloudflare dashboard via `Tunnel.withToken(token)`.
 *
 * The `Tunnel` class is an EventEmitter. We listen for the `'url'` event to
 * resolve the public URL, and `'error'` / `'exit'` to reject on failure.
 */

import { Tunnel, bin, install } from 'cloudflared';

import { createLogger } from '@/utils/logger';

import type { CloudflareTunnelSettings, ITunnelProvider, TunnelStatus } from './base';

const logger = createLogger('modules:tunnels:CloudflareProvider');

/** Ensure the cloudflared binary is present before starting a tunnel. */
async function ensureBinary(): Promise<void> {
  const fs = await import('node:fs');
  if (!fs.existsSync(bin)) {
    logger.info(`Downloading cloudflared binary to ${bin}`);
    await install(bin);
    logger.info('cloudflared binary downloaded');
  }
}

export class CloudflareProvider implements ITunnelProvider {
  private activeTunnel: Tunnel | null = null;
  private publicUrl: string | null = null;

  getStatus(): TunnelStatus {
    return {
      isRunning: this.activeTunnel !== null,
      publicUrl: this.publicUrl ?? undefined,
    };
  }

  async startTunnel(
    port: number,
    settings: CloudflareTunnelSettings,
  ): Promise<string> {
    if (this.activeTunnel) {
      logger.warn('Tunnel already running, stopping existing tunnel first');
      await this.stopTunnel();
    }

    await ensureBinary();

    const token = settings.token?.trim();

    const t: Tunnel = token
      ? Tunnel.withToken(token)
      : Tunnel.quick(`http://localhost:${port}`);

    if (token) {
      logger.info('Starting Cloudflare named tunnel via token');
    } else {
      logger.info(`Starting Cloudflare quick tunnel for http://localhost:${port}`);
    }

    this.activeTunnel = t;

    const publicUrl = await new Promise<string>((resolve, reject) => {
      const timeout = setTimeout(() => {
        reject(new Error('Cloudflare tunnel URL timeout (30 s)'));
      }, 30_000);

      t.once('url', (url: string) => {
        clearTimeout(timeout);
        resolve(url);
      });

      t.once('error', (err: Error) => {
        clearTimeout(timeout);
        reject(err);
      });

      t.once('exit', (code: number | null) => {
        clearTimeout(timeout);
        reject(new Error(`cloudflared exited unexpectedly (code ${code ?? 'null'})`));
      });
    });

    this.publicUrl = publicUrl;
    logger.info(`Cloudflare tunnel ready: ${publicUrl}`);
    return publicUrl;
  }

  async stopTunnel(): Promise<void> {
    if (!this.activeTunnel) return;
    logger.info('Stopping Cloudflare tunnel');
    try {
      this.activeTunnel.stop();
    } catch (error) {
      logger.warn('Error stopping Cloudflare tunnel', error);
    } finally {
      this.activeTunnel = null;
      this.publicUrl = null;
    }
    logger.info('Cloudflare tunnel stopped');
  }
}
