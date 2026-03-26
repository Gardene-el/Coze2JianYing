export interface SettingsState {
  draftFolder: string;
  apiPort: string;
  ngrokAuthToken: string;
  ngrokRegion: string;
  /** Cloudflare Tunnel 服务 token（可选，留空使用快速隧道） */
  cloudflareTunnelToken: string;
  relayWorkerUrl: string;
  /** 是否已从后端加载 */
  loaded: boolean;
}

export const initialSettingsState: SettingsState = {
  draftFolder: "",
  apiPort: "20211",
  ngrokAuthToken: "",
  ngrokRegion: "us",
  cloudflareTunnelToken: "",
  relayWorkerUrl: "https://coze2jianying.pages.dev",
  loaded: false,
};
