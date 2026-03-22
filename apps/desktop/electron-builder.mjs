import { execSync } from 'node:child_process';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import dotenv from 'dotenv';

import {
  copyNativeModules,
  copyNativeModulesToSource,
  getAsarUnpackPatterns,
  getNativeModulesFilesConfig,
} from './native-deps.config.mjs';

dotenv.config();

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const packageJSON = JSON.parse(await fs.readFile(path.join(__dirname, 'package.json'), 'utf8'));

const channel = process.env.UPDATE_CHANNEL;
const arch = os.arch();

// 自定义更新服务器 URL (用于 stable 频道)
const updateServerUrl = process.env.UPDATE_SERVER_URL;

console.info(`🚄 Build Version ${packageJSON.version}, Channel: ${channel}`);
console.info(`🏗️ Building for architecture: ${arch}`);

// Channel identity derived solely from UPDATE_CHANNEL env var.
// Supported channels: stable, nightly, canary
const isStable = !channel || channel === 'stable';
const isNightly = channel === 'nightly';
const isCanary = channel === 'canary';

// Strip trailing channel path from URL for re-appending the correct channel
// Handles both base URL (https://cdn.example.com) and legacy URL with channel (https://cdn.example.com/stable)
const stripChannelSuffix = (url) => url.replace(/\/(stable|nightly|canary|beta)\/?$/, '');

// 根据 channel 配置 publish provider
// - 所有渠道 + UPDATE_SERVER_URL: 使用 generic (S3)
// - 无 UPDATE_SERVER_URL: 回退到 GitHub (本地开发)
const getPublishConfig = () => {
  const channelPath = isStable ? 'stable' : isNightly ? 'nightly' : channel || 'stable';

  if (updateServerUrl) {
    const baseUrl = stripChannelSuffix(updateServerUrl);
    const fullUrl = `${baseUrl}/${channelPath}`;
    console.info(`📦 ${channelPath} channel: Using generic provider (${fullUrl})`);
    return [
      {
        provider: 'generic',
        url: fullUrl,
      },
    ];
  }

  // 本地开发无 S3 时回退到 GitHub
  console.info(`📦 ${channelPath} channel: No UPDATE_SERVER_URL, falling back to GitHub provider`);
  return [
    {
      owner: 'Gardene-el',
      provider: 'github',
      repo: 'Coze2JianYing',
    },
  ];
};

// 根据版本类型确定协议 scheme
const getProtocolScheme = () => {
  if (isCanary) return 'coze2jianying-canary';
  if (isNightly) return 'coze2jianying-nightly';
  return 'coze2jianying';
};

const protocolScheme = getProtocolScheme();

/**
 * @type {import('electron-builder').Configuration}
 * @see https://www.electron.build/configuration
 */
const config = {
  /**
   * BeforePack hook to resolve pnpm symlinks for native modules.
   * This ensures native modules are properly included in the asar archive.
   */
  beforePack: async () => {
    await copyNativeModulesToSource();

    console.info('📦 Downloading agent-browser binary...');
    execSync('node scripts/download-agent-browser.mjs', { stdio: 'inherit', cwd: __dirname });
  },
  /**
   * AfterPack hook: copy native modules to asar.unpacked (resolving pnpm symlinks)
   *
   * @see https://github.com/electron-userland/electron-builder/issues/9254
   */
  afterPack: async (context) => {
    // Windows: resources is directly in appOutDir
    const resourcesPath = path.join(context.appOutDir, 'resources');

    // Copy native modules to asar.unpacked, resolving pnpm symlinks
    const unpackedNodeModules = path.join(resourcesPath, 'app.asar.unpacked', 'node_modules');
    await copyNativeModules(unpackedNodeModules);
  },
  appId: 'com.coze2jianying.desktop',

  // Native modules must be unpacked from asar to work correctly
  asarUnpack: getAsarUnpackPatterns(),

  detectUpdateChannel: true,

  directories: {
    buildResources: '../../assets/electron/build',
    output: 'release',
  },

  electronDownload: {
    mirror: 'https://npmmirror.com/mirrors/electron/',
  },

  files: [
    'dist',
    // Map assets/electron/resources/ into the asar at resources/ (icon, tray, html pages)
    { from: '../../assets/electron/resources', to: 'resources' },
    'dist/renderer/**/*',
    // Exclude all node_modules first
    '!node_modules',
    // Then explicitly include native modules using object form (handles pnpm symlinks)
    ...getNativeModulesFilesConfig(),
  ],
  generateUpdatesFilesForAllChannels: true,
  npmRebuild: true,
  nsis: {
    allowToChangeInstallationDirectory: true,
    artifactName: '${productName}-${version}-setup.${ext}',
    createDesktopShortcut: 'always',
    installerHeader: '../../assets/electron/build/nsis-header.bmp',
    installerSidebar: '../../assets/electron/build/nsis-sidebar.bmp',
    oneClick: false,
    shortcutName: '${productName}',
    uninstallDisplayName: '${productName}',
    uninstallerSidebar: '../../assets/electron/build/nsis-sidebar.bmp',
  },
  protocols: [
    {
      name: 'Coze2JianYing Protocol',
      schemes: [protocolScheme],
    },
  ],
  publish: getPublishConfig(),

  // Release notes 配置
  // 可以通过环境变量 RELEASE_NOTES 传入，或从文件读取
  // 这会被写入 latest-mac.yml / latest.yml 中，供 generic provider 使用
  releaseInfo: {
    releaseNotes: process.env.RELEASE_NOTES || undefined,
  },

  extraResources: [
    { from: 'resources/bin', to: 'bin' },
    // CPython embed 产物目录：整体映射到安装包 resources/python/
    // python.exe 位于 resources/python/python.exe（替代旧 PyInstaller backend.exe）
    { from: 'resources/python', to: 'python' },
  ],

  win: {
    executableName: 'Coze2JianYing',
  },
};

export default config;
