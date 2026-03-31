import { CheckOutlined, CrownOutlined, DatabaseOutlined, SearchOutlined } from '@ant-design/icons'
import { Accordion, AccordionItem, copyToClipboard, Flexbox } from '@lobehub/ui'
import type { MenuProps } from 'antd'
import { Badge, Divider, Empty, Input, Menu, message, Tag, Tooltip } from 'antd'
import { useCallback, useMemo, useRef, useState } from 'react'

import { ENUM_CATEGORIES, type EnumTypeData, type SegmentCategoryData } from './enumData'
import { enumExplorerStyles as styles } from './style'

const DEFAULT_WIDTH = 280
const MIN_WIDTH = 180
const MAX_WIDTH = 480

/** Flatten all enum types across categories for quick lookup */
function findEnumByKey(
  categories: SegmentCategoryData[],
  enumKey: string,
): { enumType: EnumTypeData } | null {
  for (const cat of categories) {
    for (const fn of cat.functions) {
      for (const e of fn.enums) {
        if (e.key === enumKey) return { enumType: e }
      }
    }
  }
  return null
}

/** Build Menu items: categories as groups, enum types as clickable items inside accordion functions */
function buildMenuItems(
  categories: SegmentCategoryData[],
  expandedFns: string[],
  onFnExpandChange: (keys: string[]) => void,
  selectedEnumKey: string | null,
  onEnumSelect: (enumKey: string) => void,
): MenuProps['items'] {
  return categories.map((cat) => ({
    key: `cat:${cat.key}`,
    label: cat.label,
    type: 'group' as const,
    children: [
      {
        key: `accordion:${cat.key}`,
        label: (
          <Accordion
            expandedKeys={expandedFns}
            onExpandedChange={(keys) => onFnExpandChange(keys as string[])}
            gap={0}
            indicatorPlacement="end"
          >
            {cat.functions.map((fn) => (
              <AccordionItem
                key={fn.key}
                itemKey={fn.key}
                paddingBlock={2}
                paddingInline={0}
                title={<span className={styles.fnTitle}>{fn.label}</span>}
              >
                <Flexbox gap={0}>
                  {fn.enums.map((enumType) => (
                    <button
                      key={enumType.key}
                      type="button"
                      className={`${styles.enumItem} ${selectedEnumKey === enumType.key ? styles.enumItemActive : ''}`}
                      onClick={() => onEnumSelect(enumType.key)}
                    >
                      <span>{enumType.label}</span>
                      <span className={styles.enumCount}>{enumType.values.length}</span>
                    </button>
                  ))}
                </Flexbox>
              </AccordionItem>
            ))}
          </Accordion>
        ),
        type: 'group' as const,
      },
    ],
  }))
}

/** 单个可复制的枚举值标签：悬浮提示 + 点击复制 + 已复制反馈 */
const CopyableTag = ({ text }: { text: string }) => {
  const [copied, setCopied] = useState(false)
  const timerRef = useRef<ReturnType<typeof setTimeout>>(undefined)

  const handleCopy = useCallback(async () => {
    await copyToClipboard(text)
    message.success(`已复制: ${text}`)
    setCopied(true)
    clearTimeout(timerRef.current)
    timerRef.current = setTimeout(() => setCopied(false), 2000)
  }, [text])

  return (
    <Tooltip
      title={
        copied ? (
          <>
            <CheckOutlined /> 已复制
          </>
        ) : (
          '点击复制'
        )
      }
      mouseEnterDelay={0.3}
    >
      <Tag className={styles.valueTag} onClick={handleCopy}>
        {text}
      </Tag>
    </Tooltip>
  )
}

const EnumExplorerPage = () => {
  const [sidebarWidth, setSidebarWidth] = useState(DEFAULT_WIDTH)
  const [selectedEnumKey, setSelectedEnumKey] = useState<string | null>(null)
  const [expandedFns, setExpandedFns] = useState<string[]>(() =>
    ENUM_CATEGORIES.flatMap((cat) => cat.functions.map((fn) => fn.key)),
  )
  const [search, setSearch] = useState('')
  const draggingRef = useRef(false)
  const startXRef = useRef(0)
  const startWidthRef = useRef(0)
  const handleRef = useRef<HTMLDivElement>(null)
  const sidebarRef = useRef<HTMLDivElement>(null)

  const selectedEnum = useMemo(() => {
    if (!selectedEnumKey) return null
    return findEnumByKey(ENUM_CATEGORIES, selectedEnumKey)?.enumType ?? null
  }, [selectedEnumKey])

  const filteredValues = useMemo(() => {
    if (!selectedEnum) return { free: [], vip: [] }
    const q = search.trim().toLowerCase()
    const matched = q
      ? selectedEnum.values.filter((v) => v.name.toLowerCase().includes(q))
      : selectedEnum.values
    return {
      free: matched.filter((v) => !v.isVip),
      vip: matched.filter((v) => v.isVip),
    }
  }, [selectedEnum, search])

  const onEnumSelect = useCallback((enumKey: string) => {
    setSelectedEnumKey(enumKey)
    setSearch('')
  }, [])

  const menuItems = useMemo(
    () =>
      buildMenuItems(ENUM_CATEGORIES, expandedFns, setExpandedFns, selectedEnumKey, onEnumSelect),
    [expandedFns, selectedEnumKey, onEnumSelect],
  )

  const applySidebarWidth = useCallback((w: number) => {
    sidebarRef.current?.style.setProperty('--enum-sidebar-w', `${w}px`)
  }, [])

  const onPointerDown = useCallback(
    (e: React.PointerEvent) => {
      e.preventDefault()
      draggingRef.current = true
      startXRef.current = e.clientX
      startWidthRef.current = sidebarWidth
      handleRef.current?.setPointerCapture(e.pointerId)
      handleRef.current?.setAttribute('data-dragging', 'true')
    },
    [sidebarWidth],
  )

  const onPointerMove = useCallback(
    (e: React.PointerEvent) => {
      if (!draggingRef.current) return
      const delta = e.clientX - startXRef.current
      const next = Math.min(MAX_WIDTH, Math.max(MIN_WIDTH, startWidthRef.current + delta))
      applySidebarWidth(next)
      setSidebarWidth(next)
    },
    [applySidebarWidth],
  )

  const onPointerUp = useCallback((e: React.PointerEvent) => {
    draggingRef.current = false
    handleRef.current?.releasePointerCapture(e.pointerId)
    handleRef.current?.setAttribute('data-dragging', 'false')
  }, [])

  return (
    <div className={styles.root}>
      {/* -------- 左侧分类侧栏 -------- */}
      <div ref={sidebarRef} className={styles.sidebar}>
        <div className={styles.sidebarInner}>
          <Menu
            mode="inline"
            items={menuItems}
            selectable={false}
            style={{ border: 'none', background: 'transparent' }}
          />
        </div>
        {/* ---- 拖拽手柄 ---- */}
        <div
          ref={handleRef}
          className={styles.resizeHandle}
          onPointerDown={onPointerDown}
          onPointerMove={onPointerMove}
          onPointerUp={onPointerUp}
        />
      </div>

      {/* -------- 右侧内容区 -------- */}
      <div className={styles.content}>
        {selectedEnum ? (
          <div className={styles.contentInner}>
            {/* ---- 标题栏 ---- */}
            <Flexbox gap={8} align="baseline" className={styles.titleRow}>
              <h3 className={styles.title}>
                {selectedEnum.label}
                <span className={styles.titleSub}>{selectedEnum.key}</span>
              </h3>
            </Flexbox>
            <Flexbox horizontal gap={12} className={styles.statsRow}>
              <span>共 {selectedEnum.values.length} 项</span>
              <span>免费 {selectedEnum.values.filter((v) => !v.isVip).length}</span>
              <span>付费 {selectedEnum.values.filter((v) => v.isVip).length}</span>
              <span>
                （免费 /
                付费）是下述内容在剪映软件中的使用条件，与本软件无关。coze2jianying不是盈利软件。
              </span>
            </Flexbox>

            {/* ---- 搜索栏 ---- */}
            <Input
              prefix={<SearchOutlined />}
              placeholder={`搜索 ${selectedEnum.label} …`}
              allowClear
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{ marginBottom: 16 }}
            />

            {/* ---- 免费值列表 ---- */}
            {filteredValues.free.length > 0 && (
              <>
                <Divider plain className={styles.sectionDivider}>
                  <Badge status="success" />
                  &nbsp;免费 ({filteredValues.free.length})
                </Divider>
                <div className={styles.valueGrid}>
                  {filteredValues.free.map((v) => {
                    const text = `${selectedEnum.key}.${v.name}`
                    return <CopyableTag key={v.name} text={text} />
                  })}
                </div>
              </>
            )}

            {/* ---- 付费值列表 ---- */}
            {filteredValues.vip.length > 0 && (
              <>
                <Divider plain className={styles.sectionDividerVip}>
                  <CrownOutlined className={styles.crownIcon} />
                  &nbsp;付费 VIP ({filteredValues.vip.length})
                </Divider>
                <div className={styles.valueGrid}>
                  {filteredValues.vip.map((v) => {
                    const text = `${selectedEnum.key}.${v.name}`
                    return <CopyableTag key={v.name} text={text} />
                  })}
                </div>
              </>
            )}

            {filteredValues.free.length === 0 && filteredValues.vip.length === 0 && (
              <Empty description="没有匹配的枚举值" style={{ marginTop: 48 }} />
            )}
          </div>
        ) : (
          <Flexbox
            align="center"
            justify="center"
            className={styles.contentInner}
            style={{ minHeight: '100%' }}
          >
            <Empty
              image={
                <DatabaseOutlined style={{ fontSize: 48, color: 'var(--ant-color-primary)' }} />
              }
              description="从左侧选择枚举类型以查看详情"
            />
          </Flexbox>
        )}
      </div>
    </div>
  )
}

export default EnumExplorerPage
