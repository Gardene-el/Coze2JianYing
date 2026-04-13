/**
 * PageHeader — 与页面内分区标题风格统一，使用 antd Divider 内嵌标题。
 */
import { Divider, Space, Typography } from 'antd'
import type { FC, ReactNode } from 'react'

interface PageHeaderProps {
  /** 右侧可选操作区（按钮等） */
  extra?: ReactNode
  /** 页面大标题 */
  title: ReactNode
}

const PageHeader: FC<PageHeaderProps> = ({ title, extra }) => {
  return (
    <Divider orientation="left" orientationMargin={0} style={{ marginTop: 12 }}>
      <Space>
        <Typography.Text strong style={{ fontSize: 18 }}>
          {title}
        </Typography.Text>
        {extra}
      </Space>
    </Divider>
  )
}

export default PageHeader
