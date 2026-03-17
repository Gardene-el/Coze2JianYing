import type { CreateServicesResult, IpcServiceConstructor, MergeIpcService } from '@/utils/ipc';

import BrowserWindowsCtr from './BrowserWindowsCtr';
import DevtoolsCtr from './DevtoolsCtr';
import MenuController from './MenuCtr';
import NetworkProxyCtr from './NetworkProxyCtr';
import NotificationCtr from './NotificationCtr';
import ShortcutController from './ShortcutCtr';
import SystemController from './SystemCtr';
import TrayMenuCtr from './TrayMenuCtr';
import TunnelCtr from './TunnelCtr';
import UpdaterCtr from './UpdaterCtr';
import UploadFileCtr from './UploadFileCtr';

export const controllerIpcConstructors = [
  BrowserWindowsCtr,
  DevtoolsCtr,
  MenuController,
  NetworkProxyCtr,
  NotificationCtr,
  ShortcutController,
  SystemController,
  TrayMenuCtr,
  TunnelCtr,
  UpdaterCtr,
  UploadFileCtr,
] as const satisfies readonly IpcServiceConstructor[];

type DesktopControllerIpcConstructors = typeof controllerIpcConstructors;
type DesktopControllerServices = CreateServicesResult<DesktopControllerIpcConstructors>;
export type DesktopIpcServices = MergeIpcService<DesktopControllerServices>;
