import { execSync } from 'node:child_process';
import fs from 'node:fs/promises';
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
      owner: 'lobehub',
      provider: 'github',
      repo: 'lobehub',
    },
  ];
};

// 根据版本类型确定协议 scheme
const getProtocolScheme = () => {
  if (isCanary) return 'lobehub-canary';
  if (isNightly) return 'lobehub-nightly';
  return 'lobehub';
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
  appId: 'com.lobehub.lobehub-desktop',

  // Native modules must be unpacked from asar to work correctly
  asarUnpack: getAsarUnpackPatterns(),

  detectUpdateChannel: true,

  directories: {
    buildResources: 'build',
    output: 'release',
  },

  electronDownload: {
    mirror: 'https://npmmirror.com/mirrors/electron/',
  },

  files: [
    'dist',
    'resources',
    'dist/renderer/**/*',
    '!resources/locales',
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
    installerHeader: './build/nsis-header.bmp',
    installerSidebar: './build/nsis-sidebar.bmp',
    oneClick: false,
    shortcutName: '${productName}',
    uninstallDisplayName: '${productName}',
    uninstallerSidebar: './build/nsis-sidebar.bmp',
  },
  protocols: [
    {
      name: 'LobeHub Protocol',
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

  extraResources: [{ from: 'resources/bin', to: 'bin' }],

  win: {
    executableName: 'LobeHub',
  },
};

export default config;
