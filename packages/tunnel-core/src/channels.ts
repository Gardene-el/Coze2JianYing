/**
 * IPC channel name constants shared between the Electron main process and
 * the renderer process.  Both sides import from here so the strings can
 * never drift out of sync.
 *
 * Channel format: `tunnel.<methodName>` — matches TunnelCtr.groupName = 'tunnel'.
 */
export const TUNNEL_CHANNELS = {
  getSettings: "tunnel.getSettings",
  getStatus: "tunnel.getStatus",
  saveSettings: "tunnel.saveSettings",
  startTunnel: "tunnel.startTunnel",
  stopTunnel: "tunnel.stopTunnel",
} as const;

export type TunnelChannel =
  (typeof TUNNEL_CHANNELS)[keyof typeof TUNNEL_CHANNELS];
