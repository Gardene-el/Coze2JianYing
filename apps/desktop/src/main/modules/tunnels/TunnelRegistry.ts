import { createLogger } from '@/utils/logger'

import type { ITunnelProvider, TunnelProvider } from './base'
import { CloudflareProvider } from './CloudflareProvider'
import { NgrokProvider } from './NgrokProvider'

const logger = createLogger('modules:tunnels:TunnelRegistry')

export class TunnelRegistry {
  private readonly providers = new Map<TunnelProvider, ITunnelProvider>()

  constructor() {
    this.providers.set('ngrok', new NgrokProvider())
    this.providers.set('cloudflare', new CloudflareProvider())
    logger.debug('TunnelRegistry initialized with providers: ngrok, cloudflare')
  }

  get(provider: TunnelProvider): ITunnelProvider {
    const impl = this.providers.get(provider)
    if (!impl) throw new Error(`Unknown tunnel provider: "${provider}"`)
    return impl
  }

  register(provider: TunnelProvider, impl: ITunnelProvider): void {
    this.providers.set(provider, impl)
    logger.info(`Registered tunnel provider: ${provider}`)
  }

  async stopAll(): Promise<void> {
    logger.info('Stopping all tunnel providers')
    await Promise.allSettled([...this.providers.values()].map((p) => p.stopTunnel()))
    logger.info('All tunnel providers stopped')
  }
}

export const tunnelRegistry = new TunnelRegistry()
