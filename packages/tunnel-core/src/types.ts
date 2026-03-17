/**
 * Shared types for tunnel providers.
 * Zero runtime — pure TypeScript interfaces and type aliases.
 */

export type TunnelProvider = "ngrok" | "cloudflare";

export interface TunnelStatus {
  isRunning: boolean;
  publicUrl?: string;
}

/** Contract every provider implementation must satisfy (used in the main process). */
export interface ITunnelProvider {
  getStatus(): TunnelStatus;
  startTunnel(
    port: number,
    settings: NgrokSettings | CloudflareTunnelSettings,
  ): Promise<string>;
  stopTunnel(): Promise<void>;
}

export interface NgrokSettings {
  authToken: string;
  region: string;
}

/** Reserved for future Cloudflare Tunnel support — not yet implemented. */
export interface CloudflareTunnelSettings {
  token: string;
  tunnelId?: string;
}

export type TunnelProviderSettings = {
  ngrok?: NgrokSettings;
  cloudflare?: CloudflareTunnelSettings;
};

export interface StartTunnelPayload {
  provider: TunnelProvider;
  port: number;
  /** Override stored settings for this invocation. */
  settings?: Partial<NgrokSettings | CloudflareTunnelSettings>;
}

export interface TunnelSettingsPayload {
  provider: TunnelProvider;
  settings: NgrokSettings | CloudflareTunnelSettings;
}

export interface TunnelProviderPayload {
  provider: TunnelProvider;
}
