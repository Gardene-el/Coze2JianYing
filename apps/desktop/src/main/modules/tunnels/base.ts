/**
 * Re-exports shared tunnel contracts from @c2jy/tunnel-core so that
 * main-process code import from a single, nearby path.
 *
 * Also the right place to add Node.js–specific helpers (e.g. a logger
 * factory that wraps provider errors) without polluting the pure-types
 * package.
 */
export type {
  CloudflareTunnelSettings,
  ITunnelProvider,
  NgrokSettings,
  TunnelProvider,
  TunnelProviderSettings,
  TunnelStatus,
} from '@c2jy/tunnel-core'
