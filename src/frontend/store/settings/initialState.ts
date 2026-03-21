import type { NeutralColors, PrimaryColors } from "@lobehub/ui";

/** 动效模式：敏捷 / 普通 / 禁用 */
export type AnimationMode = "agile" | "normal" | "disabled";

export interface SettingsState {
  draftFolder: string;
  apiPort: string;
  ngrokAuthToken: string;
  ngrokRegion: string;
  relayWorkerUrl: string;
  transferEnabled: boolean;
  /** 是否已从后端加载 */
  loaded: boolean;

  // ——— 主题定制（对齐 LobeChat）———
  /** 主色调，undefined 表示使用 @lobehub/ui 默认 */
  primaryColor: PrimaryColors | undefined;
  /** 中性色，undefined 表示使用 @lobehub/ui 默认 */
  neutralColor: NeutralColors | undefined;
  /** 动效模式 */
  animationMode: AnimationMode;
  /** 自定义字体族名（可选） */
  customFontFamily: string;
  /** 自定义字体远程 URL（可选，FontLoader 使用） */
  customFontURL: string;
}

export const initialSettingsState: SettingsState = {
  draftFolder: "",
  apiPort: "20211",
  ngrokAuthToken: "",
  ngrokRegion: "us",
  relayWorkerUrl: "https://coze2jianying.pages.dev",
  transferEnabled: false,
  loaded: false,

  primaryColor: undefined,
  neutralColor: undefined,
  animationMode: "agile",
  customFontFamily: "",
  customFontURL: "",
};
