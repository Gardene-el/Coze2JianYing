import { CheckOutlined, SearchOutlined, SmileOutlined } from '@ant-design/icons'
import { copyToClipboard } from '@lobehub/ui'
import { Empty, Input, message, Pagination, Spin, Tag, Tooltip } from 'antd'
import { useCallback, useEffect, useMemo, useRef, useState } from 'react'

import { stickerBrowserStyles as styles } from './style'

interface StickerItem {
  id: string
  name: string
}

const PAGE_SIZE = 100

/** 从 Vite public/ 静态资产懒加载全量贴纸数据 */
let _cachedStickers: StickerItem[] | null = null
let _loadingPromise: Promise<StickerItem[]> | null = null

function loadStickers(): Promise<StickerItem[]> {
  if (_cachedStickers) return Promise.resolve(_cachedStickers)
  if (_loadingPromise) return _loadingPromise
  _loadingPromise = fetch('/sticker.json')
    .then((r) => r.json() as Promise<StickerItem[]>)
    .then((data) => {
      _cachedStickers = data
      return data
    })
  return _loadingPromise
}

/** 单个可复制的贴纸标签：显示名称，点击复制 ID */
const StickerTag = ({ item }: { item: StickerItem }) => {
  const [copied, setCopied] = useState(false)
  const timerRef = useRef<ReturnType<typeof setTimeout>>(undefined)

  const handleCopy = useCallback(async () => {
    await copyToClipboard(item.id)
    message.success(`已复制贴纸 ID: ${item.id}`)
    setCopied(true)
    clearTimeout(timerRef.current)
    timerRef.current = setTimeout(() => setCopied(false), 2000)
  }, [item.id])

  return (
    <Tooltip
      title={
        copied ? (
          <>
            <CheckOutlined /> 已复制 {item.id}
          </>
        ) : (
          `点击复制 ID: ${item.id}`
        )
      }
      mouseEnterDelay={0.3}
    >
      <Tag className={styles.tag} onClick={handleCopy}>
        {item.name}
      </Tag>
    </Tooltip>
  )
}

const StickerBrowserPage = () => {
  const [allStickers, setAllStickers] = useState<StickerItem[]>([])
  const [page, setPage] = useState(1)
  const [inputValue, setInputValue] = useState('')
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadStickers()
      .then(setAllStickers)
      .catch(() => message.error('加载贴纸数据失败'))
      .finally(() => setLoading(false))
  }, [])

  const filtered = useMemo(() => {
    if (!search) return allStickers
    const kw = search.toLowerCase()
    return allStickers.filter((s) => s.name.toLowerCase().includes(kw))
  }, [allStickers, search])

  const pageItems = useMemo(
    () => filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE),
    [filtered, page],
  )

  const handleSearch = useCallback((value: string) => {
    setSearch(value.trim())
    setPage(1)
  }, [])

  return (
    <div className={styles.root}>
      {/* ---- 搜索栏 ---- */}
      <div className={styles.toolbar}>
        <Input
          prefix={<SearchOutlined />}
          placeholder="搜索贴纸名称…"
          allowClear
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onPressEnter={() => handleSearch(inputValue)}
          onClear={() => handleSearch('')}
          style={{ maxWidth: 360 }}
        />
        <span className={styles.stats}>
          {loading
            ? '加载中…'
            : search
              ? `找到 ${filtered.length.toLocaleString()} / ${allStickers.length.toLocaleString()} 个`
              : `共 ${allStickers.length.toLocaleString()} 个贴纸`}
        </span>
      </div>

      {/* ---- 贴纸网格 ---- */}
      <div className={styles.content}>
        {loading ? (
          <Spin style={{ display: 'block', margin: '60px auto' }} />
        ) : pageItems.length === 0 ? (
          <Empty
            image={
              <SmileOutlined style={{ fontSize: 48, color: 'var(--ant-color-text-quaternary)' }} />
            }
            description="没有匹配的贴纸"
            style={{ marginTop: 60 }}
          />
        ) : (
          <div className={styles.grid}>
            {pageItems.map((item) => (
              <StickerTag key={item.id} item={item} />
            ))}
          </div>
        )}
      </div>

      {/* ---- 分页 ---- */}
      {!loading && filtered.length > PAGE_SIZE && (
        <div className={styles.pagination}>
          <Pagination
            current={page}
            total={filtered.length}
            pageSize={PAGE_SIZE}
            onChange={(p) => setPage(p)}
            showSizeChanger={false}
            showQuickJumper
            showTotal={(t) => `共 ${t.toLocaleString()} 条`}
          />
        </div>
      )}
    </div>
  )
}

export default StickerBrowserPage
