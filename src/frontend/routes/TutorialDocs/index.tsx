import { Segmented } from 'antd'
import { Outlet, useLocation, useNavigate } from 'react-router-dom'

import { tutorialDocsStyles as styles } from './style'

const TAB_ITEMS = [
  { label: '新手指引', value: 'getting-started' },
  { label: 'API 文档', value: 'api-docs' },
  { label: '枚举查询', value: 'enums' },
  { label: '贴纸查询', value: 'stickers' },
]

/**
 * TutorialDocs 布局组件
 *
 * 固定顶部（Segmented 二级导航居中）+ 弹性内容区（<Outlet />）。
 * 各子路由自行管控滚动和内部布局。
 */
const TutorialDocsLayout = () => {
  const navigate = useNavigate()
  const { pathname } = useLocation()

  const currentTab =
    TAB_ITEMS.find((item) => pathname.endsWith(item.value))?.value || TAB_ITEMS[0].value

  return (
    <div className={styles.root}>
      {/* -------- 顶部导航 -------- */}
      <div className={styles.header}>
        <Segmented
          value={currentTab}
          options={TAB_ITEMS}
          onChange={(value) => navigate(`/tutorial-docs/${value}`)}
        />
      </div>

      {/* -------- 子路由内容 -------- */}
      <div className={styles.content}>
        <Outlet />
      </div>
    </div>
  )
}

export default TutorialDocsLayout
