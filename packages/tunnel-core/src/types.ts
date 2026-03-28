/**
 * Shared types for tunnel providers.
 * Zero runtime — pure TypeScript interfaces and type aliases.
 *
 * Adding a new provider:
 *   1. Add provider id to `TunnelProvider` union.
 *   2. Add a `TunnelProviderMeta` entry to `TUNNEL_PROVIDER_LIST`.
 *   3. Implement `ITunnelProvider` in the desktop main-process.
 *   4. Register it in `TunnelRegistry`.
 *   5. Add a settings interface (e.g. `FrpSettings`) and union it into
 *      `TunnelProviderSettings`.
 *   Candidates: "frp" | "localtunnel" | "bore"
 */

export type TunnelProvider = 'ngrok' | 'cloudflare'

/** Static metadata for a tunnel provider — drives the provider list UI. */
export interface TunnelProviderMeta {
  /** Unique provider id, matches `TunnelProvider`. */
  id: TunnelProvider
  /** Display name shown in the provider list. */
  name: string
  /** One-line description shown below the name. */
  description: string
}

/** All supported tunnel providers in display order. */
export const TUNNEL_PROVIDER_LIST: TunnelProviderMeta[] = [
  {
    id: 'ngrok',
    name: 'ngrok',
    description: '稳定的商业内网穿透服务，免费层有流量限制',
  },
  {
    id: 'cloudflare',
    name: 'Cloudflare Tunnel',
    description: '基于 Cloudflare 全球网络，免登录快速隧道或命名隧道',
  },
]

export interface TunnelStatus {
  isRunning: boolean
  publicUrl?: string
}

/** Contract every provider implementation must satisfy (used in the main process). */
export interface ITunnelProvider {
  getStatus(): TunnelStatus
  startTunnel(port: number, settings: NgrokSettings | CloudflareTunnelSettings): Promise<string>
  stopTunnel(): Promise<void>
}

export interface NgrokSettings {
  authToken: string
  region: string
}

/** Cloudflare Tunnel settings.
 *  - `token` empty  → quick tunnel (trycloudflare.com), no account needed.
 *  - `token` filled → named tunnel via `cloudflared tunnel run --token`.
 *    In this case `publicUrl` MUST also be set to the hostname configured in
 *    the Cloudflare Zero Trust dashboard (cloudflared does not broadcast it).
 */
export interface CloudflareTunnelSettings {
  /** Service token from the Cloudflare dashboard, or empty for quick tunnel. */
  token?: string
  /** For named tunnels: the public hostname from the Cloudflare Zero Trust
   *  dashboard, e.g. https://my-app.example.com.  Unused for quick tunnels. */
  publicUrl?: string
  /**
   * Transport protocol passed to cloudflared via `--protocol`.
   * Defaults to `"http2"` for quick tunnels.
   *
   * cloudflared 2024+ defaults to QUIC (UDP 7844), which is silently dropped
   * on many networks/firewalls and does NOT automatically fall back to HTTP/2.
   * Use `"http2"` (TLS/TCP 443) for maximum compatibility, or `"quic"` on
   * networks where UDP is allowed.
   *
   * Valid values: `"http2"` | `"quic"` | `"auto"`
   */
  protocol?: 'http2' | 'quic' | 'auto'
}

export type TunnelProviderSettings = {
  ngrok?: NgrokSettings
  cloudflare?: CloudflareTunnelSettings
}

export interface StartTunnelPayload {
  provider: TunnelProvider
  port: number
  /** Override stored settings for this invocation. */
  settings?: Partial<NgrokSettings | CloudflareTunnelSettings>
}

export interface TunnelSettingsPayload {
  provider: TunnelProvider
  settings: NgrokSettings | CloudflareTunnelSettings
}

export interface TunnelProviderPayload {
  provider: TunnelProvider
}
