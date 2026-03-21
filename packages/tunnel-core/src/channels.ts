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
  getWorkerUrl: "tunnel.getWorkerUrl",
  setWorkerUrl: "tunnel.setWorkerUrl",
} as const;

export type TunnelChannel =
  (typeof TUNNEL_CHANNELS)[keyof typeof TUNNEL_CHANNELS];

/**
 * IPC channels for managing the Python backend process.
 * Channel format: `backend.<methodName>` — matches BackendCtr.groupName = 'backend'.
 */
export const BACKEND_CHANNELS = {
  getPort: "backend.getPort",
  setPort: "backend.setPort",
  getStatus: "backend.getStatus",
  start: "backend.start",
  stop: "backend.stop",
} as const;

export type BackendChannel =
  (typeof BACKEND_CHANNELS)[keyof typeof BACKEND_CHANNELS];
