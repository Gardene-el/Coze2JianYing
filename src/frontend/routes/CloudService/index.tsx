import { PlayCircleOutlined, ReloadOutlined, StopOutlined } from '@ant-design/icons'
import type { TunnelProvider } from '@c2jy/tunnel-core'
import {
  Badge,
  Button,
  Divider,
  Empty,
  Input,
  message,
  Space,
  Tag,
  Tooltip,
  Typography,
} from 'antd'
import { useEffect, useRef, useState } from 'react'
import PageContainer from '@/components/PageContainer'
import PageHeader from '@/components/PageHeader'
import { useServiceStatus } from '@/hooks/useServiceStatus'
import { useServiceStore } from '@/store/service/store'
import { initialSettingsState } from '@/store/settings/initialState'
import { useSettingsStore } from '@/store/settings/store'

import CloudflareCard from './CloudflareCard'
import NgrokCard from './NgrokCard'
import TunnelProviderList from './TunnelProviderList'

const DEFAULT_API_PORT = initialSettingsState.apiPort

const { Text } = Typography

const CloudServicePage = () => {
  const [msgApi, ctx] = message.useMessage()

  // ── Service state ────────────────────────────────────────────
  const { isRunning, isLoading, ngrokRunning, cloudflareRunning } = useServiceStore()
  const { startService, stopService } = useServiceStore()
  const selectedTunnelProvider = useServiceStore((s) => s.selectedTunnelProvider)

  const { apiPort, loadSettings } = useSettingsStore()
  const { saveSettings } = useSettingsStore()

  const [portInput, setPortInput] = useState(apiPort)
  const portSaveTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  useEffect(() => {
    setPortInput(apiPort)
  }, [apiPort])

  const handlePortChange = (value: string) => {
    setPortInput(value)
    if (portSaveTimerRef.current) clearTimeout(portSaveTimerRef.current)
    portSaveTimerRef.current = setTimeout(async () => {
      try {
        await saveSettings({ apiPort: value })
        msgApi.success('已保存', 1)
      } catch (e: unknown) {
        msgApi.error(`保存失败: ${(e as Error).message}`)
      }
    }, 500)
  }

  const handlePortReset = async () => {
    setPortInput(DEFAULT_API_PORT)
    try {
      await saveSettings({ apiPort: DEFAULT_API_PORT })
      msgApi.success('已重置为默认端口', 1.5)
    } catch (e: unknown) {
      msgApi.error(`重置失败: ${(e as Error).message}`)
    }
  }

  useServiceStatus()

  useEffect(() => {
    void loadSettings()
  }, [loadSettings])

  // ── Service start / stop ─────────────────────────────────────
  const handleStartService = async () => {
    try {
      await startService()
      msgApi.success('Coze API 服务已启动')
    } catch (e: unknown) {
      msgApi.error(`启动失败: ${(e as Error).message}`)
    }
  }

  const handleStopService = async () => {
    try {
      await stopService()
      msgApi.success('服务已停止')
    } catch (e: unknown) {
      msgApi.error(`停止失败: ${(e as Error).message}`)
    }
  }

  // ── Tunnel provider selection ─────────────────────────────────
  const handleProviderSelect = (provider: TunnelProvider) => {
    useServiceStore.setState({ selectedTunnelProvider: provider })
  }

  // Tunnel title tag
  const tunnelRunning = ngrokRunning || cloudflareRunning
  const tunnelTag = tunnelRunning ? (
    <Tag color="success">运行中</Tag>
  ) : (
    <Tag color="default">未启动</Tag>
  )

  const port = Number(portInput) || 20211

  return (
    <PageContainer>
      {ctx}
      <PageHeader title="直连模式" />

      {/* ── Coze API 服务 ───────────────────────────────────── */}
      <div style={{ marginBottom: 16 }}>
        <Divider orientation="left" orientationMargin={0}>
          <Space>
            <Text strong>Coze API 服务</Text>
            <Badge
              status={isRunning ? 'success' : 'default'}
              text={isRunning ? '运行中' : '已停止'}
            />
          </Space>
        </Divider>
        <Space wrap>
          <Space.Compact size="small">
            <Input
              value={portInput}
              onChange={(e) => handlePortChange(e.target.value)}
              style={{ width: 80 }}
              placeholder={DEFAULT_API_PORT}
            />
            <Tooltip title="重置端口">
              <Button icon={<ReloadOutlined />} onClick={handlePortReset} />
            </Tooltip>
          </Space.Compact>
          <Button
            type="primary"
            icon={<PlayCircleOutlined />}
            loading={isLoading}
            disabled={isRunning}
            onClick={handleStartService}
          >
            启动服务
          </Button>
          <Button
            danger
            icon={<StopOutlined />}
            loading={isLoading}
            disabled={!isRunning}
            onClick={handleStopService}
          >
            停止服务
          </Button>
        </Space>
      </div>

      {/* ── 内网穿透（可选） ────────────────────────────────── */}
      <div>
        <Divider orientation="left" orientationMargin={0}>
          <Space>
            <Text strong>内网穿透（可选）</Text>
            {tunnelTag}
          </Space>
        </Divider>
        <div style={{ display: 'flex', gap: 0, minHeight: 160 }}>
          {/* Left: provider list */}
          <div
            style={{
              borderRight: '1px solid var(--ant-color-border-secondary)',
              paddingRight: 0,
              marginRight: 24,
            }}
          >
            <TunnelProviderList onSelect={handleProviderSelect} />
          </div>

          {/* Right: provider card */}
          <div style={{ flex: 1 }}>
            {!selectedTunnelProvider ? (
              <Empty
                description={<Text type="secondary">从左侧选择一个内网穿透服务商以展开配置</Text>}
                image={Empty.PRESENTED_IMAGE_SIMPLE}
                style={{ margin: '32px 0' }}
              />
            ) : (
              <>
                <Text strong style={{ display: 'block', marginBottom: 16 }}>
                  {selectedTunnelProvider === 'ngrok' ? 'ngrok' : 'Cloudflare Tunnel'}
                </Text>
                <Divider style={{ marginTop: 0 }} />
                {selectedTunnelProvider === 'ngrok' ? (
                  <NgrokCard
                    port={port}
                    serviceRunning={isRunning}
                    otherTunnelRunning={cloudflareRunning}
                    onSuccess={(m) => msgApi.success(m)}
                    onError={(m) => msgApi.error(m)}
                  />
                ) : (
                  <CloudflareCard
                    port={port}
                    serviceRunning={isRunning}
                    otherTunnelRunning={ngrokRunning}
                    onSuccess={(m) => msgApi.success(m)}
                    onError={(m) => msgApi.error(m)}
                  />
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </PageContainer>
  )
}

export default CloudServicePage
