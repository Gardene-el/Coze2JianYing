export interface ServiceState {
  /** Coze API 服务是否在运行 */
  isRunning: boolean;
  /** 服务监听端口 */
  port: number;
  /** 服务启/停操作是否进行中 */
  isLoading: boolean;
  /** ngrok 是否在运行 */
  ngrokRunning: boolean;
  /** ngrok 公网 URL */
  ngrokUrl: string;
  /** ngrok 操作是否进行中 */
  ngrokLoading: boolean;
}

export const initialServiceState: ServiceState = {
  isRunning: false,
  port: 20211,
  isLoading: false,
  ngrokRunning: false,
  ngrokUrl: "",
  ngrokLoading: false,
};
