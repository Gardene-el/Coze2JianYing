export interface SettingsState {
  draftFolder: string;
  apiPort: string;
  ngrokAuthToken: string;
  ngrokRegion: string;
  relayWorkerUrl: string;
  /** 是否已从后端加载 */
  loaded: boolean;
}

export const initialSettingsState: SettingsState = {
  draftFolder: "",
  apiPort: "20211",
  ngrokAuthToken: "",
  ngrokRegion: "us",
  relayWorkerUrl: "https://coze2jianying.pages.dev",
  loaded: false,
};
