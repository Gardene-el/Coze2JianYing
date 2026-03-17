import type { TunnelProvider } from "@c2jy/tunnel-core";

import { ngrokTunnelService } from "./ngrok";

/**
 * Factory that returns the appropriate tunnel service for the given provider.
 * Add future providers (e.g. 'cloudflare') here without changing any other file.
 */
export const tunnelService = (provider: TunnelProvider) => {
  switch (provider) {
    case "ngrok":
      return ngrokTunnelService;
    case "cloudflare":
      throw new Error("Cloudflare Tunnel provider is not yet implemented");
  }
};

export { ngrokTunnelService } from "./ngrok";
