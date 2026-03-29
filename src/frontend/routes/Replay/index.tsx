import { PlayCircleOutlined, ReloadOutlined, SearchOutlined } from '@ant-design/icons'
import { Button, Card, Input, message, Space, Spin, Tag, Typography } from 'antd'
import { useEffect, useRef, useState } from 'react'

import PageContainer from '@/components/PageContainer'
import PageHeader from '@/components/PageHeader'
import { useEnsureBackend } from '@/hooks/useEnsureBackend'
import { guiReplayAPI } from '@/services/gui/replay'
import { type WorkerReplayResult, workerReplayAPI } from '@/services/worker/replay'
import { initialSettingsState } from '@/store/settings/initialState'
import { useSettingsStore } from '@/store/settings/store'
import { extractDraftIds } from '@/utils/extractDraftIds'

const DEFAULT_WORKER_URL = initialSettingsState.relayWorkerUrl

type QueryStatus = 'idle' | 'loading' | 'success' | 'error'
type ExecStatus = 'idle' | 'loading' | 'success' | 'error'

interface IdState {
  queryStatus: QueryStatus
  queryResult: WorkerReplayResult | null
  queryError: string
  execStatus: ExecStatus
  execMsg: string
}

const defaultIdState = (): IdState => ({
  queryStatus: 'idle',
  queryResult: null,
  queryError: '',
  execStatus: 'idle',
  execMsg: '',
})

const ReplayPage = () => {
  const [msgApi, ctx] = message.useMessage()
  const [rawInput, setRawInput] = useState('')
  const [extractedIds, setExtractedIds] = useState<string[]>([])
  const [idStates, setIdStates] = useState<Map<string, IdState>>(new Map())
  const [querying, setQuerying] = useState(false)
  const [executingAll, setExecutingAll] = useState(false)

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

  const handleInputChange = (val: string) => {
    setRawInput(val)
    setExtractedIds(extractDraftIds(val))
    setIdStates(new Map())
  }

  /** 函数式更新，安全地修改单个 ID 的状态 */
  const updateIdState = (id: string, patch: Partial<IdState>) => {
    setIdStates((prev) => {
      const next = new Map(prev)
      next.set(id, { ...(next.get(id) ?? defaultIdState()), ...patch })
      return next
    })
  }

  const handleQuery = async () => {
    if (extractedIds.length === 0) return msgApi.warning('未识别到有效的草稿 ID')
    if (!urlInput.trim()) return msgApi.error('未配置云服务器地址，请在下方填写')

    setQuerying(true)
    // 初始化所有 ID 为 loading 状态
    const initial = new Map<string, IdState>()
    for (const id of extractedIds) initial.set(id, { ...defaultIdState(), queryStatus: 'loading' })
    setIdStates(initial)

    // 并行拉取所有 ID
    await Promise.allSettled(
      extractedIds.map(async (id) => {
        try {
          const data = await workerReplayAPI.get(urlInput, id)
          updateIdState(id, { queryStatus: 'success', queryResult: data })
        } catch (e: unknown) {
          updateIdState(id, { queryStatus: 'error', queryError: (e as Error).message })
        }
      }),
    )
    setQuerying(false)
  }

  const handleExecuteOne = async (id: string) => {
    if (!urlInput.trim()) return msgApi.error('未配置云服务器地址，请在下方填写')
    updateIdState(id, { execStatus: 'loading', execMsg: '执行中…' })
    try {
      await ensureReady()
      const res = await guiReplayAPI.execute(urlInput, id)
      updateIdState(id, { execStatus: 'success', execMsg: `成功 ${res.calls_executed} 条` })
      msgApi.success(`草稿 ${id.slice(0, 13)}… 已生成（${res.calls_executed} 条调用）`)
    } catch (e: unknown) {
      const msg = (e as Error).message
      updateIdState(id, { execStatus: 'error', execMsg: msg })
      msgApi.error(`执行失败: ${msg}`)
    }
  }

  const handleExecuteAll = async () => {
    const fetchedIds = extractedIds.filter(
      (id) => (idStates.get(id)?.queryStatus ?? 'idle') === 'success',
    )
    if (fetchedIds.length === 0) return msgApi.warning('暂无可执行的草稿')
    if (!urlInput.trim()) return msgApi.error('未配置云服务器地址，请在下方填写')

    setExecutingAll(true)
    try {
      await ensureReady()
      for (const id of fetchedIds) {
        updateIdState(id, { execStatus: 'loading', execMsg: '执行中…' })
        try {
          const res = await guiReplayAPI.execute(urlInput, id)
          updateIdState(id, { execStatus: 'success', execMsg: `成功 ${res.calls_executed} 条` })
        } catch (e: unknown) {
          updateIdState(id, { execStatus: 'error', execMsg: (e as Error).message })
        }
      }
      msgApi.success(`全部执行完毕，共 ${fetchedIds.length} 个草稿`)
    } catch (e: unknown) {
      msgApi.error(`后端启动失败: ${(e as Error).message}`)
    } finally {
      setExecutingAll(false)
    }
  }

  const hasFetched = extractedIds.some((id) => idStates.get(id)?.queryStatus === 'success')

  return (
    <PageContainer>
      {ctx}
      <PageHeader title="粘贴id" />
      <Card
        title="📷 粘贴草稿id相关内容进所选框进行拉取，Coze2JianYing可以智能识别草稿id"
        style={{ marginBottom: 16 }}
      >
        {/* 输入区 */}
        <Input.TextArea
          value={rawInput}
          onChange={(e) => handleInputChange(e.target.value)}
          placeholder={
            '粘贴草稿 ID，支持以下格式：\n• 纯 ID（多行或任意分隔符均可）\n• JSON: {"draft_id": "..."}\n• JSON: {"draft_ids": ["..."]}'
          }
          autoSize={{ minRows: 3, maxRows: 8 }}
          style={{ marginBottom: 8, fontFamily: 'monospace' }}
        />

        {/* 识别反馈 */}
        {rawInput && (
          <div style={{ marginBottom: 12 }}>
            {extractedIds.length > 0 ? (
              <Space wrap>
                <Typography.Text type="secondary">
                  识别到 {extractedIds.length} 个草稿ID：
                </Typography.Text>
                {extractedIds.map((id) => (
                  <Tag key={id} color="blue">
                    {id}
                  </Tag>
                ))}
              </Space>
            ) : (
              <Tag color="warning">未能识别到有效的草稿 ID</Tag>
            )}
          </div>
        )}

        {/* 操作按钮 */}
        <Space style={{ marginBottom: idStates.size > 0 ? 16 : 0 }}>
          <Button
            type="primary"
            icon={<SearchOutlined />}
            loading={querying}
            disabled={extractedIds.length === 0}
            onClick={handleQuery}
          >
            {`拉取${extractedIds.length > 1 ? `（${extractedIds.length} 个）` : ''}`}
          </Button>
          {hasFetched && (
            <Button
              icon={<PlayCircleOutlined />}
              loading={executingAll}
              disabled={executingAll}
              onClick={handleExecuteAll}
            >
              全部执行
            </Button>
          )}
        </Space>

        {/* 每个 ID 的结果行 */}
        {idStates.size > 0 && (
          <div>
            {extractedIds.map((id) => {
              const state = idStates.get(id) ?? defaultIdState()
              return (
                <div
                  key={id}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 8,
                    padding: '8px 0',
                    borderBottom: '1px solid var(--ant-color-border-secondary)',
                    flexWrap: 'wrap',
                  }}
                >
                  <Typography.Text code copyable style={{ flex: 1, minWidth: 200 }}>
                    {id}
                  </Typography.Text>

                  {state.queryStatus === 'loading' && <Spin size="small" />}
                  {state.queryStatus === 'success' && state.queryResult && (
                    <Tag color="success">{state.queryResult.total} 条调用</Tag>
                  )}
                  {state.queryStatus === 'error' && (
                    <Tag color="error" title={state.queryError}>
                      拉取失败
                    </Tag>
                  )}

                  {state.execStatus !== 'idle' && (
                    <Tag
                      color={
                        state.execStatus === 'loading'
                          ? 'processing'
                          : state.execStatus === 'success'
                            ? 'success'
                            : 'error'
                      }
                    >
                      {state.execMsg}
                    </Tag>
                  )}

                  <Button
                    size="small"
                    icon={<PlayCircleOutlined />}
                    disabled={state.queryStatus !== 'success' || state.execStatus === 'loading'}
                    loading={state.execStatus === 'loading'}
                    onClick={() => handleExecuteOne(id)}
                  >
                    执行
                  </Button>
                </div>
              )
            })}
          </div>
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
