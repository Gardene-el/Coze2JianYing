/**
 * Cloudflare Tunnel provider — wraps the `cloudflared` npm package (v0.7+).
 *
 * Two modes depending on whether a `token` is supplied:
 *   - Quick tunnel (token empty): no Cloudflare account needed — gets a
 *     *.trycloudflare.com URL via `Tunnel.quick(url)`, which emits `'url'`.
 *   - Named tunnel (token non-empty): persistent domain configured in the
 *     Cloudflare dashboard via `Tunnel.withToken(token)`, which emits
 *     `'connected'` (NOT `'url'`). The public URL is provided by the user.
 *
 * The `Tunnel` class is an EventEmitter.
 */

import { bin, install, Tunnel } from 'cloudflared'

import { createLogger } from '@/utils/logger'

import type { CloudflareTunnelSettings, ITunnelProvider, TunnelStatus } from './base'

const logger = createLogger('modules:tunnels:CloudflareProvider')

/** Ensure the cloudflared binary is present before starting a tunnel. */
async function ensureBinary(): Promise<void> {
  const fs = await import('node:fs')
  if (!fs.existsSync(bin)) {
    logger.info(`Downloading cloudflared binary to ${bin}`)
    await install(bin)
    logger.info('cloudflared binary downloaded')
  }
}

export class CloudflareProvider implements ITunnelProvider {
  private activeTunnel: Tunnel | null = null
  private publicUrl: string | null = null

  getStatus(): TunnelStatus {
    return {
      isRunning: this.activeTunnel !== null,
      publicUrl: this.publicUrl ?? undefined,
    }
  }

  async startTunnel(port: number, settings: CloudflareTunnelSettings): Promise<string> {
    if (this.activeTunnel) {
      logger.warn('Tunnel already running, stopping existing tunnel first')
      await this.stopTunnel()
    }

    await ensureBinary()

    const token = settings.token?.trim()

    if (token) {
      // ── Named tunnel ────────────────────────────────────────────────────
      // Tunnel.withToken() connects to the Cloudflare network and emits
      // 'connected' when ready. It NEVER emits 'url' — the public hostname
      // is managed in the Cloudflare Zero Trust dashboard.
      logger.info('Starting Cloudflare named tunnel via token')
      const t = Tunnel.withToken(token, { '--no-autoupdate': true })
      this.activeTunnel = t

      t.on('stderr', (data: string) => logger.debug('[cloudflared stderr]', data))

      // Persistent exit handler — reset state if tunnel crashes after startup
      t.on('exit', (code: number | null, signal: string | null) => {
        if (this.activeTunnel === t) {
          logger.warn(
            `cloudflared named tunnel exited (code ${code ?? 'null'}, signal ${signal ?? 'none'})`,
          )
          this.activeTunnel = null
          this.publicUrl = null
        }
      })

      await new Promise<void>((resolve, reject) => {
        const timeout = setTimeout(() => {
          reject(new Error('Cloudflare 命名隧道连接超时 (30 s)'))
        }, 30_000)

        t.once('connected', () => {
          clearTimeout(timeout)
          resolve()
        })

        t.once('error', (err: Error) => {
          clearTimeout(timeout)
          reject(err)
        })

        t.once('exit', (code: number | null) => {
          clearTimeout(timeout)
          reject(new Error(`cloudflared 意外退出 (code ${code ?? 'null'})`))
        })
      })

      const publicUrl = settings.publicUrl?.trim()
      if (!publicUrl) {
        throw new Error('命名隧道需要在控制台填写公网域名')
      }
      this.publicUrl = publicUrl
      logger.info(`Cloudflare named tunnel ready: ${publicUrl}`)
      return publicUrl
    } else {
      // ── Quick tunnel ─────────────────────────────────────────────────────
      // Tunnel.quick() spawns a temporary tunnel and emits 'url' with the
      // assigned *.trycloudflare.com address.
      //
      // Force HTTP/2 transport via the (undocumented-in-help but functional)
      // --protocol flag.  cloudflared 2026.x defaults to QUIC (UDP 7844),
      // which is silently blocked on many networks/firewalls; it does NOT
      // automatically fall back to HTTP/2 within any useful timeout.
      // HTTP/2 (TLS over TCP 443) works reliably everywhere and connects in
      // ~2 s rather than failing with repeated QUIC timeouts.
      const protocol = settings.protocol ?? 'http2'
      logger.info(
        `Starting Cloudflare quick tunnel for http://127.0.0.1:${port} (protocol=${protocol})`,
      )
      const t = Tunnel.quick(`http://127.0.0.1:${port}`, {
        '--no-autoupdate': true,
        '--protocol': protocol,
      })
      this.activeTunnel = t

      // Persistent exit handler — reset state if tunnel crashes after startup
      t.on('exit', (code: number | null, signal: string | null) => {
        if (this.activeTunnel === t) {
          logger.warn(
            `cloudflared quick tunnel exited (code ${code ?? 'null'}, signal ${signal ?? 'none'})`,
          )
          this.activeTunnel = null
          this.publicUrl = null
        }
      })

      const publicUrl = await new Promise<string>((resolve, reject) => {
        const timeout = setTimeout(() => {
          reject(new Error('快速隧道连接超时 (60 s)'))
        }, 60_000)

        let resolvedUrl: string | null = null
        let readyTimer: ReturnType<typeof setTimeout> | null = null

        // 'url' event: cloudflared printed the trycloudflare.com hostname.
        // The URL is assigned by Cloudflare BEFORE the edge connection is
        // established — do NOT resolve immediately here.
        t.once('url', (url: string) => {
          logger.debug(`cloudflared quick tunnel URL received: ${url}`)
          resolvedUrl = url
          // Fallback: if "Registered tunnel connection" never appears
          // (newer cloudflared log formats), resolve after 10 s.
          readyTimer = setTimeout(() => {
            clearTimeout(timeout)
            t.off('stdout', onOutput)
            t.off('stderr', onOutput)
            resolve(resolvedUrl as string)
          }, 10_000)
        })

        // Watch for cloudflared's edge-connection confirmation line.
        // DO NOT match bare "connIndex" — it appears in pre-connection and
        // error lines and would cause a false-positive resolve.
        const registeredPattern = /registered tunnel connection|connection registered/i
        const onOutput = (data: string) => {
          logger.debug('[cloudflared]', data.trimEnd())
          if (resolvedUrl && registeredPattern.test(data)) {
            if (readyTimer) {
              clearTimeout(readyTimer)
              readyTimer = null
            }
            clearTimeout(timeout)
            t.off('stdout', onOutput)
            t.off('stderr', onOutput)
            resolve(resolvedUrl)
          }
        }
        t.on('stdout', onOutput)
        t.on('stderr', onOutput)

        t.once('error', (err: Error) => {
          clearTimeout(timeout)
          if (readyTimer) clearTimeout(readyTimer)
          reject(err)
        })

        t.once('exit', (code: number | null, signal: string | null) => {
          clearTimeout(timeout)
          if (readyTimer) clearTimeout(readyTimer)
          reject(
            new Error(`cloudflared 意外退出 (code ${code ?? 'null'}, signal ${signal ?? 'none'})`),
          )
        })
      })

      this.publicUrl = publicUrl
      logger.info(`Cloudflare quick tunnel ready: ${publicUrl}`)
      return publicUrl
    }
  }

  async stopTunnel(): Promise<void> {
    if (!this.activeTunnel) return
    logger.info('Stopping Cloudflare tunnel')
    try {
      this.activeTunnel.stop()
    } catch (error) {
      logger.warn('Error stopping Cloudflare tunnel', error)
    } finally {
      this.activeTunnel = null
      this.publicUrl = null
    }
    logger.info('Cloudflare tunnel stopped')
  }
}
