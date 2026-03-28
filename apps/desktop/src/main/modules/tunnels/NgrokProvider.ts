import ngrok from '@ngrok/ngrok'

import { createLogger } from '@/utils/logger'

import type { ITunnelProvider, NgrokSettings, TunnelStatus } from './base'

const logger = createLogger('modules:tunnels:NgrokProvider')

export class NgrokProvider implements ITunnelProvider {
  private listener: Awaited<ReturnType<typeof ngrok.connect>> | null = null

  getStatus(): TunnelStatus {
    if (this.listener) {
      const url = this.listener.url()
      return { isRunning: !!url, publicUrl: url ?? undefined }
    }
    return { isRunning: false }
  }

  async startTunnel(port: number, settings: NgrokSettings): Promise<string> {
    if (this.listener) {
      logger.warn('Tunnel already running, stopping existing tunnel first')
      await this.stopTunnel()
    }

    logger.info(`Starting ngrok tunnel on port ${port}`, { region: settings.region })

    this.listener = await ngrok.connect({
      addr: port,
      authtoken: settings.authToken,
      region: settings.region,
    })

    const url = this.listener.url()
    if (!url) throw new Error('ngrok connected but returned no URL')

    logger.info(`Tunnel started: ${url}`)
    return url
  }

  async stopTunnel(): Promise<void> {
    if (!this.listener) return
    logger.info('Stopping ngrok tunnel')
    try {
      await this.listener.close()
    } catch (error) {
      logger.warn('Error closing ngrok listener, attempting session disconnect', error)
      await ngrok.disconnect().catch(() => void 0)
    } finally {
      this.listener = null
    }
    logger.info('Tunnel stopped')
  }
}
