import { PlayCircleOutlined, ReloadOutlined, SearchOutlined } from '@ant-design/icons'
import { Button, Card, Input, message, Space, Spin, Tag } from 'antd'
import { createStaticStyles } from 'antd-style'
import { useEffect, useRef, useState } from 'react'

import PageContainer from '@/components/PageContainer'
import PageHeader from '@/components/PageHeader'
import { useEnsureBackend } from '@/hooks/useEnsureBackend'
import { guiReplayAPI } from '@/services/gui/replay'
import { workerReplayAPI } from '@/services/worker/replay'
import { initialSettingsState } from '@/store/settings/initialState'
import { useSettingsStore } from '@/store/settings/store'

const DEFAULT_WORKER_URL = initialSettingsState.relayWorkerUrl

const styles = createStaticStyles(({ css, cssVar }) => ({
  json: css`
    width: 100%;
    max-height: 500px;
    overflow: auto;
    padding: 12px;
    font-family: ${cssVar.fontFamilyCode};
    font-size: 12px;
    line-height: 1.6;
    background: ${cssVar.colorBgLayout};
    border: 1px solid ${cssVar.colorBorderSecondary};
    border-radius: ${cssVar.borderRadius};
    white-space: pre;
  `,
}))

type ExecuteStatus = 'idle' | 'loading' | 'success' | 'error'

const ReplayPage = () => {
  const [msgApi, ctx] = message.useMessage()
  const [draftId, setDraftId] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<object | null>(null)

  const [executing, setExecuting] = useState(false)
  const [execStatus, setExecStatus] = useState<ExecuteStatus>('idle')
  const [execMsg, setExecMsg] = useState('')

  const { ensureReady } = useEnsureBackend()

  const relayWorkerUrl = useSettingsStore((s) => s.relayWorkerUrl)
  const saveSettings = useSettingsStore((s) => s.saveSettings)
  const [urlInput, setUrlInput] = useState(relayWorkerUrl)

  // 当 store 中的值初次加载后同步到本地输入框
  useEffect(() => {
    setUrlInput(relayWorkerUrl)
  }, [relayWorkerUrl])

  const saveTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  const handleUrlChange = (value: string) => {
    setUrlInput(value)
    if (saveTimerRef.current) clearTimeout(saveTimerRef.current)
    saveTimerRef.current = setTimeout(async () => {
      try {
        await saveSettings({ relayWorkerUrl: value })
        msgApi.success('已保存', 1)
      } catch (e: unknown) {
        msgApi.error(`保存失败: ${(e as Error).message}`)
      }
    }, 500)
  }

  const handleReset = async () => {
    setUrlInput(DEFAULT_WORKER_URL)
    try {
      await saveSettings({ relayWorkerUrl: DEFAULT_WORKER_URL })
      msgApi.success('已重置为默认值', 1.5)
    } catch (e: unknown) {
      msgApi.error(`重置失败: ${(e as Error).message}`)
    }
  }

  const handleQuery = async () => {
    if (!draftId.trim()) return msgApi.warning('请输入 Draft ID')
    if (!urlInput.trim()) {
      msgApi.error('未配置 云服务器地址，请在下方填写')
      return
    }
    setLoading(true)
    setResult(null)
    setExecStatus('idle')
    setExecMsg('')
    try {
      const data = await workerReplayAPI.get(urlInput, draftId.trim())
      setResult(data)
    } catch (e: unknown) {
      msgApi.error(`拉取失败: ${(e as Error).message}`)
    } finally {
      setLoading(false)
    }
  }

  const handleExecute = async () => {
    if (!result) return msgApi.warning('请先拉取数据')
    if (!urlInput.trim()) {
      msgApi.error('未配置云服务器地址，请在下方填写')
      return
    }
    setExecuting(true)
    setExecStatus('loading')
    setExecMsg('准备后端中…')
    try {
      await ensureReady()
      setExecMsg('执行中…')
      const res = await guiReplayAPI.execute(urlInput, draftId.trim())
      setExecStatus('success')
      setExecMsg(`执行成功，共处理 ${res.calls_executed} 条调用`)
      msgApi.success(`草稿已生成（${res.calls_executed} 条调用）`)
    } catch (e: unknown) {
      setExecStatus('error')
      setExecMsg(`执行失败: ${(e as Error).message}`)
      msgApi.error(`执行失败: ${(e as Error).message}`)
    } finally {
      setExecuting(false)
    }
  }

  return (
    <PageContainer>
      {ctx}
      <PageHeader title="粘贴id" />
      <Card
        title="📷 粘贴草稿id相关内容进所选框进行拉取，Coze2JianYing可以智能识别草稿id"
        style={{ marginBottom: 16 }}
      >
        <Input.Search
          value={draftId}
          onChange={(e) => setDraftId(e.target.value)}
          placeholder="输入 Draft ID，例如 1710000000000-xxxxx"
          enterButton={
            <>
              <SearchOutlined /> 拉取
            </>
          }
          loading={loading}
          onSearch={handleQuery}
          style={{ maxWidth: 560, marginBottom: 16 }}
        />

        {loading && <Spin />}

        {result && !loading && (
          <>
            <div className={styles.json}>{JSON.stringify(result, null, 2)}</div>
            <Space style={{ marginTop: 12 }} wrap>
              <Button
                type="primary"
                icon={<PlayCircleOutlined />}
                loading={executing}
                disabled={executing}
                onClick={handleExecute}
              >
                执行到草稿
              </Button>
              {execStatus !== 'idle' && (
                <Tag
                  color={
                    execStatus === 'loading'
                      ? 'processing'
                      : execStatus === 'success'
                        ? 'success'
                        : 'error'
                  }
                >
                  {executing ? (
                    <>
                      <Spin size="small" /> {execMsg}
                    </>
                  ) : (
                    execMsg
                  )}
                </Tag>
              )}
            </Space>
          </>
        )}
      </Card>

      <Card title="☁️ 云服务器地址" style={{ marginBottom: 12 }}>
        <Space.Compact style={{ width: '100%', maxWidth: 560 }}>
          <Input
            value={urlInput}
            onChange={(e) => handleUrlChange(e.target.value)}
            placeholder={DEFAULT_WORKER_URL}
          />
          <Button icon={<ReloadOutlined />} onClick={handleReset}>
            重置
          </Button>
        </Space.Compact>
      </Card>
    </PageContainer>
  )
}

export default ReplayPage
