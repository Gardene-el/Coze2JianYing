/**
 * 全局 Window 类型扩展
 *
 * Electron preload 通过 contextBridge 暴露的 API 声明。
 * 对应 apps/desktop/src/preload/electronApi.ts。
 */

interface LobeEnv {
  darwinMajorVersion: number;
  isMacTahoe: boolean;
  platform: string;
}

interface ElectronStreamAPI {
  invoke: (channel: string, ...args: unknown[]) => Promise<unknown>;
  onStreamInvoke: (
    channel: string,
    handler: (...args: unknown[]) => void,
  ) => () => void;
}

declare interface Window {
  /**
   * `@electron-toolkit/preload` 的 electronAPI 对象。
   * 存在时说明当前运行于 Electron 环境。
   */
  electron?: Record<string, unknown>;

  /** 自定义 IPC invoke / stream API */
  electronAPI?: ElectronStreamAPI;

  /** 运行平台信息 */
  lobeEnv?: LobeEnv;
}
