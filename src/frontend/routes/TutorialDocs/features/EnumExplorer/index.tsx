import { DatabaseOutlined } from '@ant-design/icons'
import { Flexbox } from '@lobehub/ui'
import { Empty, Menu, type MenuProps } from 'antd'

import { enumExplorerStyles as styles } from './style'

/**
 * 枚举分类 — 按 Segment 类型组织
 * 后续将从 pyJianYingDraft 的枚举定义中动态生成。
 */
const ENUM_CATEGORIES: MenuProps['items'] = [
  {
    key: 'video',
    label: '视频',
    type: 'group',
    children: [
      { key: 'intro_type', label: '入场动画' },
      { key: 'outro_type', label: '出场动画' },
      { key: 'group_animation', label: '组合动画' },
      { key: 'transition', label: '转场' },
      { key: 'video_scene_effect', label: '画面特效' },
      { key: 'video_character_effect', label: '人物特效' },
      { key: 'filter', label: '滤镜' },
      { key: 'mask', label: '蒙版' },
      { key: 'mix_mode', label: '混合模式' },
    ],
  },
  {
    key: 'audio',
    label: '音频',
    type: 'group',
    children: [
      { key: 'audio_scene_effect', label: '音频场景特效' },
      { key: 'tone_effect', label: '音色效果' },
      { key: 'speech_to_song', label: '声音成曲' },
    ],
  },
  {
    key: 'text',
    label: '文本',
    type: 'group',
    children: [
      { key: 'text_intro', label: '文字入场动画' },
      { key: 'text_outro', label: '文字出场动画' },
      { key: 'text_loop', label: '文字循环动画' },
      { key: 'font', label: '字体' },
    ],
  },
  {
    key: 'keyframe',
    label: '关键帧',
    type: 'group',
    children: [{ key: 'keyframe_property', label: '关键帧属性' }],
  },
  {
    key: 'export',
    label: '导出',
    type: 'group',
    children: [
      { key: 'export_resolution', label: '分辨率' },
      { key: 'export_framerate', label: '帧率' },
    ],
  },
]

/**
 * 枚举查询 — 侧栏 + 内容分栏布局（Shell）
 *
 * 左侧：枚举分类导航（Menu）
 * 右侧：选中枚举的详情展示区
 *
 * 后续将接入真实枚举数据、搜索过滤、详情卡片等功能。
 */
const EnumExplorerPage = () => {
  return (
    <div className={styles.root}>
      {/* -------- 左侧分类侧栏 -------- */}
      <div className={styles.sidebar}>
        <div className={styles.sidebarInner}>
          <Menu
            mode="inline"
            items={ENUM_CATEGORIES}
            defaultOpenKeys={['video', 'audio', 'text', 'keyframe', 'export']}
            style={{ border: 'none', background: 'transparent' }}
          />
        </div>
      </div>

      {/* -------- 右侧内容区 -------- */}
      <div className={styles.content}>
        <Flexbox
          align="center"
          justify="center"
          className={styles.contentInner}
          style={{ minHeight: '100%' }}
        >
          <Empty
            image={<DatabaseOutlined style={{ fontSize: 48, color: 'var(--ant-color-primary)' }} />}
            description="从左侧选择枚举分类以查看详情"
          />
        </Flexbox>
      </div>
    </div>
  )
}

export default EnumExplorerPage
