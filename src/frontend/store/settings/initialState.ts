export interface SettingsState {
  draftFolder: string
  apiPort: string
  ngrokAuthToken: string
  ngrokRegion: string
  /** Cloudflare Tunnel 服务 token（可选，留空使用快速隧道） */
  cloudflareTunnelToken: string /** 命名遂道的公网域名，从 Cloudflare Zero Trust 控制台获取（仅使用 Token 时需要） */
  cloudflareTunnelPublicUrl: string
  relayWorkerUrl: string
  /** 是否已从后端加载 */
  loaded: boolean
}

export const initialSettingsState: SettingsState = {
  draftFolder: '',
  apiPort: '20211',
  ngrokAuthToken: '',
  ngrokRegion: 'us',
  cloudflareTunnelToken: '',
  cloudflareTunnelPublicUrl: '',
  relayWorkerUrl: 'https://coze2jianying.pages.dev',
  loaded: false,
}
