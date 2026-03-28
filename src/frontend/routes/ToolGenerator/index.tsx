import { DownloadOutlined } from '@ant-design/icons'
import { Button, Form, Input, Typography } from 'antd'

import PageContainer from '@/components/PageContainer'
import PageHeader from '@/components/PageHeader'

// Vite 在编译期将 YAML 内容内联为字符串常量
// openapi.generated.yaml 由 scripts/openapi_generator/main.py 生成并提交至仓库
import rawSpec from '../../../../openapi.generated.yaml?raw'

const { Text } = Typography

const DEFAULT_URL = 'https://coze2jianying.pages.dev'

/** 将 YAML 中的 servers[0].url 替换为用户指定的地址 */
function applyServerUrl(yaml: string, url: string): string {
  const normalized = url.trim().replace(/\/$/, '')
  return yaml.replace(/^(servers:\n- url: ).+$/m, `$1${normalized}`)
}

const ToolGeneratorPage = () => {
  const [form] = Form.useForm<{ serverUrl: string }>()

  const handleGenerate = () => {
    const serverUrl = (form.getFieldValue('serverUrl') as string) || DEFAULT_URL

    if (!serverUrl.startsWith('http://') && !serverUrl.startsWith('https://')) {
      form.setFields([
        {
          name: 'serverUrl',
          errors: ['请输入以 http:// 或 https:// 开头的完整 URL'],
        },
      ])
      return
    }

    const output = applyServerUrl(rawSpec, serverUrl)
    const blob = new Blob([output], { type: 'text/yaml;charset=utf-8' })
    const objectUrl = URL.createObjectURL(blob)
    const anchor = document.createElement('a')
    anchor.href = objectUrl
    anchor.download = 'openapi.yaml'
    anchor.click()
    URL.revokeObjectURL(objectUrl)
  }

  return (
    <PageContainer>
      <PageHeader title="插件生成器" />

      <Form
        form={form}
        layout="vertical"
        initialValues={{ serverUrl: DEFAULT_URL }}
        style={{ marginTop: 24, maxWidth: 560 }}
      >
        <Form.Item
          label="你的服务地址"
          name="serverUrl"
          extra={
            <Text type="secondary" style={{ fontSize: 12 }}>
              填入你部署了 Coze2JianYing API 的公网地址，生成的 openapi.yaml 将以该地址作为
              servers[0].url，可直接在 Coze 平台上导入为私有插件。
            </Text>
          }
        >
          <Input placeholder={DEFAULT_URL} allowClear />
        </Form.Item>

        <Form.Item>
          <Button type="primary" icon={<DownloadOutlined />} onClick={handleGenerate}>
            生成并下载 openapi.yaml
          </Button>
        </Form.Item>
      </Form>
    </PageContainer>
  )
}

export default ToolGeneratorPage
