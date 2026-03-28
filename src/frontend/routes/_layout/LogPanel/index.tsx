import { ClearOutlined, DownOutlined, PauseOutlined } from '@ant-design/icons'
import { Button, Tooltip } from 'antd'
import { createStaticStyles } from 'antd-style'
import { useCallback, useEffect, useRef, useState } from 'react'
import { useSSELog } from '@/hooks/useSSELog'
import type { LogEntry } from '@/store/log/initialState'
import { useLogStore } from '@/store/log/store'

const LOG_HEIGHT_KEY = 'c2j-log-height'
const LOG_COLLAPSED_KEY = 'c2j-log-collapsed'
const DEFAULT_HEIGHT = 180
const MIN_HEIGHT = 80
const MAX_HEIGHT = 800
/** 拖拽释放时低于此高度则吸附折叠 */
const COLLAPSE_THRESHOLD = 60

const LEVEL_COLORS: Record<LogEntry['level'], string> = {
  DEBUG: '#8c8c8c',
  INFO: '#52c41a',
  WARNING: '#faad14',
  ERROR: '#f5222d',
  CRITICAL: '#ff4d4f',
}

const styles = createStaticStyles(({ css, cssVar }) => ({
  panel: css`
    display: flex;
    flex-direction: column;
    border-top: 1px solid ${cssVar.colorBorderSecondary};
    background: ${cssVar.colorBgContainer};
    position: relative;
    overflow: hidden;
  `,
  resizeHandle: css`
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 5px;
    cursor: row-resize;
    z-index: 10;
    border: none;
    background: transparent;
    padding: 0;
    outline: none;
  `,
  /** 折叠后底部吸附标签 */
  collapsedTab: css`
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 0 12px;
    height: 28px;
    cursor: row-resize;
    user-select: none;
    border: none;
    border-top: 2px solid ${cssVar.colorBorderSecondary};
    background: ${cssVar.colorBgLayout};
    outline: none;
    font-size: 12px;
    color: ${cssVar.colorTextSecondary};
    transition: background 0.15s;
    &:hover {
      background: ${cssVar.colorFillSecondary};
    }
  `,
  gripper: css`
    display: inline-flex;
    flex-direction: column;
    gap: 2.5px;
    opacity: 0.45;
    flex-shrink: 0;
    pointer-events: none;
  `,
  gripperLine: css`
    display: block;
    width: 18px;
    height: 1.5px;
    border-radius: 1px;
    background: currentColor;
  `,
  toolbar: css`
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 4px 8px;
    flex-shrink: 0;
    border-bottom: 1px solid ${cssVar.colorBorderSecondary};
    font-size: 12px;
    color: ${cssVar.colorTextSecondary};
    user-select: none;
  `,
  dot: css`
    display: inline-block;
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #52c41a;
    box-shadow: 0 0 4px 2px rgba(82, 196, 26, 0.4);
    animation: pulse 1.5s ease-in-out infinite;
    @keyframes pulse {
      0%,
      100% {
        opacity: 1;
      }
      50% {
        opacity: 0.4;
      }
    }
  `,
  dotOff: css`
    display: inline-block;
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: ${cssVar.colorTextQuaternary};
  `,
  log: css`
    flex: 1;
    overflow-y: auto;
    padding: 4px 12px;
    font-family: ${cssVar.fontFamilyCode};
    font-size: 12px;
    line-height: 1.8;
    scrollbar-width: thin;
  `,
  entry: css`
    display: flex;
    gap: 8px;
    white-space: pre-wrap;
    word-break: break-all;
  `,
}))

const LogPanel = () => {
  const entries = useLogStore((s) => s.entries)
  const isStreaming = useLogStore((s) => s.isStreaming)
  const autoScroll = useLogStore((s) => s.autoScroll)
  const clearLogs = useLogStore((s) => s.clearLogs)
  const setAutoScroll = useLogStore((s) => s.setAutoScroll)

  const [panelHeight, setPanelHeight] = useState(() => {
    try {
      const stored = localStorage.getItem(LOG_HEIGHT_KEY)
      return stored ? parseInt(stored, 10) : DEFAULT_HEIGHT
    } catch {
      return DEFAULT_HEIGHT
    }
  })

  const [collapsed, setCollapsed] = useState(() => {
    try {
      return localStorage.getItem(LOG_COLLAPSED_KEY) === 'true'
    } catch {
      return false
    }
  })

  // 用 ref 保存最新高度，避免 mousedown 闭包捕获旧值
  const panelHeightRef = useRef(panelHeight)
  panelHeightRef.current = panelHeight

  const [isDragging, setIsDragging] = useState(false)

  /**
   * 展开状态下顶部拖拽条 — 向下拖到阈值以下时吸附折叠。
   */
  const handleResizeMouseDown = useCallback((e: React.MouseEvent) => {
    e.preventDefault()
    const startY = e.clientY
    const startH = panelHeightRef.current
    setIsDragging(true)

    const onMove = (ev: MouseEvent) => {
      setPanelHeight(Math.max(1, startH + startY - ev.clientY))
    }

    const onUp = (ev: MouseEvent) => {
      setIsDragging(false)
      document.removeEventListener('mousemove', onMove)
      document.removeEventListener('mouseup', onUp)
      const newH = startH + startY - ev.clientY
      if (newH < COLLAPSE_THRESHOLD) {
        // 吸附折叠，并还原高度供下次展开使用
        setCollapsed(true)
        setPanelHeight(startH)
        try {
          localStorage.setItem(LOG_COLLAPSED_KEY, 'true')
        } catch {}
      } else {
        const h = Math.max(MIN_HEIGHT, Math.min(MAX_HEIGHT, newH))
        setPanelHeight(h)
        try {
          localStorage.setItem(LOG_HEIGHT_KEY, String(h))
        } catch {}
      }
    }

    document.addEventListener('mousemove', onMove)
    document.addEventListener('mouseup', onUp)
  }, [])

  /**
   * 折叠标签的拖拽/点击 — 向上拖超过阈值展开；点击直接展开。
   */
  const handleTabMouseDown = useCallback((e: React.MouseEvent) => {
    e.preventDefault()
    const startY = e.clientY
    const savedH = panelHeightRef.current
    let didDrag = false
    setIsDragging(true)

    const onMove = (ev: MouseEvent) => {
      const dy = startY - ev.clientY
      if (dy > 5) {
        didDrag = true
        setCollapsed(false)
        setPanelHeight(Math.max(MIN_HEIGHT, Math.min(MAX_HEIGHT, dy)))
      }
    }

    const onUp = (ev: MouseEvent) => {
      setIsDragging(false)
      document.removeEventListener('mousemove', onMove)
      document.removeEventListener('mouseup', onUp)
      const dy = startY - ev.clientY
      if (!didDrag) {
        // 纯点击：展开到上次保存的高度
        setPanelHeight(savedH)
        setCollapsed(false)
        try {
          localStorage.setItem(LOG_COLLAPSED_KEY, 'false')
        } catch {}
        return
      }
      if (dy < COLLAPSE_THRESHOLD) {
        // 拖得不够远：吸附回折叠
        setCollapsed(true)
        setPanelHeight(savedH)
      } else {
        const h = Math.max(MIN_HEIGHT, Math.min(MAX_HEIGHT, dy))
        setPanelHeight(h)
        try {
          localStorage.setItem(LOG_HEIGHT_KEY, String(h))
          localStorage.setItem(LOG_COLLAPSED_KEY, 'false')
        } catch {}
      }
    }

    document.addEventListener('mousemove', onMove)
    document.addEventListener('mouseup', onUp)
  }, [])

  // 连接 SSE
  useSSELog()

  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (autoScroll && !collapsed) {
      bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
    }
  }, [autoScroll, collapsed])

  // 折叠态：仅渲染底部吸附标签
  if (collapsed) {
    return (
      <button type="button" className={styles.collapsedTab} onMouseDown={handleTabMouseDown}>
        <span className={styles.gripper}>
          <span className={styles.gripperLine} />
          <span className={styles.gripperLine} />
          <span className={styles.gripperLine} />
        </span>
        <span className={isStreaming ? styles.dot : styles.dotOff} />
        <span>运行日志</span>
        <span style={{ opacity: 0.55, fontSize: 11 }}>
          {isStreaming ? '（已连接）' : '（未连接）'}
        </span>
      </button>
    )
  }

  // 展开态：完整面板
  return (
    <div
      className={styles.panel}
      style={{
        height: panelHeight,
        transition: isDragging ? 'none' : 'height 0.12s ease',
      }}
    >
      <button type="button" className={styles.resizeHandle} onMouseDown={handleResizeMouseDown} />
      <div className={styles.toolbar}>
        <span className={isStreaming ? styles.dot : styles.dotOff} />
        <span style={{ flex: 1 }}>运行日志 {isStreaming ? '（已连接）' : '（未连接）'}</span>
        <Tooltip title={autoScroll ? '关闭自动滚动' : '开启自动滚动'}>
          <Button
            size="small"
            type="text"
            icon={autoScroll ? <DownOutlined /> : <PauseOutlined />}
            onClick={() => setAutoScroll(!autoScroll)}
          />
        </Tooltip>
        <Tooltip title="清空日志">
          <Button size="small" type="text" icon={<ClearOutlined />} onClick={clearLogs} />
        </Tooltip>
      </div>
      <div className={styles.log}>
        {entries.map((e) => (
          <div key={e.id} className={styles.entry}>
            <span style={{ color: '#8c8c8c', flexShrink: 0 }}>{e.timestamp}</span>
            <span
              style={{
                color: LEVEL_COLORS[e.level],
                flexShrink: 0,
                minWidth: 52,
              }}
            >
              {e.level}
            </span>
            <span>{e.message}</span>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
    </div>
  )
}

export default LogPanel
