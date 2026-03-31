import { FileTextOutlined, LinkOutlined } from '@ant-design/icons'
import { Flexbox } from '@lobehub/ui'
import { Card, Empty, Typography } from 'antd'

const { Text } = Typography

/**
 * API 文档 — 文档浏览容器（Shell）
 *
 * 后续将集成 OpenAPI / Swagger 渲染器或自定义 Markdown 文档预览。
 * 当前仅展示布局骨架。
 */
const ApiDocsPage = () => {
  return (
    <Flexbox align="center" style={{ height: '100%', overflowY: 'auto', scrollbarWidth: 'thin' }}>
      <Flexbox gap={24} style={{ maxWidth: 1024, width: '100%', padding: 24 }}>
        <Empty
          image={<FileTextOutlined style={{ fontSize: 48, color: 'var(--ant-color-primary)' }} />}
          description="API 接口文档"
        />

        <Flexbox gap={16}>
          <Card size="small" hoverable>
            <Flexbox horizontal align="center" gap={12}>
              <LinkOutlined style={{ fontSize: 18, color: 'var(--ant-color-primary)' }} />
              <Flexbox gap={2}>
                <Text strong>Coze2JianYing REST API</Text>
                <Text type="secondary" style={{ fontSize: 12 }}>
                  草稿生成、素材管理、脚本执行等核心接口文档
                </Text>
              </Flexbox>
            </Flexbox>
          </Card>

          <Card size="small" hoverable>
            <Flexbox horizontal align="center" gap={12}>
              <LinkOutlined style={{ fontSize: 18, color: 'var(--ant-color-primary)' }} />
              <Flexbox gap={2}>
                <Text strong>pyJianYingDraft SDK</Text>
                <Text type="secondary" style={{ fontSize: 12 }}>
                  Python SDK 的类与方法参考文档
                </Text>
              </Flexbox>
            </Flexbox>
          </Card>
        </Flexbox>
      </Flexbox>
    </Flexbox>
  )
}

export default ApiDocsPage
