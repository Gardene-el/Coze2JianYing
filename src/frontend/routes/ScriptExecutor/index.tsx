import {
  CheckOutlined,
  ClearOutlined,
  FormatPainterOutlined,
  PlayCircleOutlined,
} from '@ant-design/icons'
import { Alert, Button, message, Space, Spin, Tag } from 'antd'
import { createStaticStyles } from 'antd-style'
import { useRef, useState } from 'react'

import PageContainer from '@/components/PageContainer'
import PageHeader from '@/components/PageHeader'
import { useEnsureBackend } from '@/hooks/useEnsureBackend'
import { guiScriptAPI } from '@/services/gui/script'

const styles = createStaticStyles(({ css, cssVar }) => ({
  textarea: css`
    width: 100%;
    min-height: 340px;
    padding: 12px;
    font-family: ${cssVar.fontFamilyCode};
    font-size: 13px;
    line-height: 1.6;
    border: 1px solid ${cssVar.colorBorder};
    border-radius: ${cssVar.borderRadius};
    background: ${cssVar.colorBgContainer};
    color: ${cssVar.colorText};
    resize: vertical;
    outline: none;
    &:focus {
      border-color: ${cssVar.colorPrimary};
    }
  `,
}))

type StatusType = 'idle' | 'loading' | 'success' | 'error'

const ScriptExecutorPage = () => {
  const [msgApi, ctx] = message.useMessage()
  const [status, setStatus] = useState<StatusType>('idle')
  const [statusText, setStatusText] = useState('就绪')
  const [validationMsg, setValidationMsg] = useState<string | null>(null)
  const textRef = useRef<HTMLTextAreaElement>(null)
  const { ensureReady } = useEnsureBackend()

  const getContent = () => textRef.current?.value.trim() ?? ''

  const handleFormat = async () => {
    const content = getContent()
    if (!content) return msgApi.warning('请先粘贴内容')
    setStatus('loading')
    try {
      await ensureReady()
      const data = await guiScriptAPI.format(content)
      if (textRef.current) textRef.current.value = data.formatted
      setStatus('idle')
      setStatusText('格式化完成')
    } catch (e: unknown) {
      msgApi.error(`格式化失败: ${(e as Error).message}`)
      setStatus('idle')
    }
  }

  const handleValidate = async () => {
    const content = getContent()
    if (!content) return msgApi.warning('请先粘贴内容')
    setStatus('loading')
    try {
      await ensureReady()
      const data = await guiScriptAPI.validate(content)
      setValidationMsg(data.valid ? null : (data.error ?? '语法错误'))
      setStatus(data.valid ? 'success' : 'error')
      setStatusText(data.valid ? '验证通过' : '验证失败')
    } catch (e: unknown) {
      msgApi.error(`验证失败: ${(e as Error).message}`)
      setStatus('idle')
    }
  }

  const handleExecute = async () => {
    const content = getContent()
    if (!content) return msgApi.warning('请先粘贴内容')
    setStatus('loading')
    setStatusText('执行中…')
    setValidationMsg(null)
    try {
      await ensureReady()
      await guiScriptAPI.execute(content)
      setStatus('success')
      setStatusText('执行成功 ✓')
      msgApi.success('脚本执行成功')
    } catch (e: unknown) {
      setStatus('error')
      setStatusText('执行失败')
      msgApi.error(`执行失败: ${(e as Error).message}`)
    }
  }

  const handleClear = () => {
    if (textRef.current) textRef.current.value = ''
    setStatus('idle')
    setStatusText('就绪')
    setValidationMsg(null)
  }

  const statusColor: Record<StatusType, 'default' | 'processing' | 'success' | 'error'> = {
    idle: 'default',
    loading: 'processing',
    success: 'success',
    error: 'error',
  }

  return (
    <PageContainer>
      {ctx}
      <PageHeader title="粘贴脚本" />
      <textarea
        ref={textRef}
        className={styles.textarea}
        placeholder="粘贴 Python 脚本或 Coze 导出的 JSON…"
      />

      {validationMsg && (
        <Alert type="error" message={validationMsg} showIcon style={{ marginTop: 8 }} />
      )}

      <Space
        style={{
          marginTop: 12,
          width: '100%',
          justifyContent: 'space-between',
        }}
        wrap
      >
        <Space>
          <Tag bordered={false} color={statusColor[status]}>
            {status === 'loading' ? (
              <>
                <Spin size="small" /> {statusText}
              </>
            ) : (
              statusText
            )}
          </Tag>
        </Space>
        <Space wrap>
          <Button icon={<ClearOutlined />} onClick={handleClear}>
            清空
          </Button>
          <Button
            icon={<FormatPainterOutlined />}
            disabled={status === 'loading'}
            onClick={handleFormat}
          >
            格式化输入
          </Button>
          <Button icon={<CheckOutlined />} disabled={status === 'loading'} onClick={handleValidate}>
            验证脚本
          </Button>
          <Button
            type="primary"
            icon={<PlayCircleOutlined />}
            loading={status === 'loading'}
            onClick={handleExecute}
          >
            执行脚本
          </Button>
        </Space>
      </Space>
    </PageContainer>
  )
}

export default ScriptExecutorPage
