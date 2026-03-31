import { RocketOutlined } from '@ant-design/icons'
import { Flexbox } from '@lobehub/ui'
import { Empty, Steps } from 'antd'

/**
 * 新手指引 — 步骤式引导容器（Shell）
 *
 * 后续将填充每一步的详细内容与交互逻辑。
 * 当前仅展示布局骨架。
 */
const GettingStartedPage = () => {
  return (
    <Flexbox align="center" style={{ height: '100%', overflowY: 'auto', scrollbarWidth: 'thin' }}>
      <Flexbox gap={32} style={{ maxWidth: 720, width: '100%', padding: 24 }}>
        <Empty
          image={<RocketOutlined style={{ fontSize: 48, color: 'var(--ant-color-primary)' }} />}
          description="快速上手 Coze2JianYing"
        />

        <Steps
          direction="vertical"
          current={-1}
          items={[
            {
              title: '环境准备',
              description: '安装 Python 运行环境与剪映桌面端',
            },
            {
              title: '配置路径',
              description: '在设置页配置剪映草稿文件夹路径',
            },
            {
              title: '连接 Coze',
              description: '通过云端直连或中转模式建立与 Coze 的通信',
            },
            {
              title: '生成草稿',
              description: '使用 Coze 插件调用 API 自动生成剪映草稿',
            },
            {
              title: '进阶用法',
              description: '探索脚本执行、枚举查询等高级功能',
            },
          ]}
        />
      </Flexbox>
    </Flexbox>
  )
}

export default GettingStartedPage
