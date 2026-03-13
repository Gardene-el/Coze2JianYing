import {
  FolderOpenOutlined,
  ReloadOutlined,
  SaveOutlined,
} from "@ant-design/icons";
import {
  Button,
  Card,
  Divider,
  Form,
  Input,
  message,
  Select,
  Space,
  Switch,
  Typography,
} from "antd";
import { useEffect } from "react";

import { useSettingsStore } from "@/store/settings/store";

const { Title, Text } = Typography;

const SettingsPage = () => {
  const [form] = Form.useForm();
  const [msgApi, ctx] = message.useMessage();

  const {
    draftFolder,
    apiPort,
    ngrokAuthToken,
    ngrokRegion,
    relayWorkerUrl,
    themeMode,
    transferEnabled,
    isSaving,
    loadSettings,
    saveSettings,
    detectDraftPath,
  } = useSettingsStore();

  useEffect(() => {
    void loadSettings();
  }, [loadSettings]);

  useEffect(() => {
    form.setFieldsValue({
      draftFolder,
      apiPort,
      ngrokAuthToken,
      ngrokRegion,
      relayWorkerUrl,
      themeMode,
      transferEnabled,
    });
  }, [
    draftFolder,
    apiPort,
    ngrokAuthToken,
    ngrokRegion,
    relayWorkerUrl,
    themeMode,
    transferEnabled,
    form,
  ]);

  const handleSave = async () => {
    const values = await form.validateFields();
    try {
      await saveSettings({
        draftFolder: values.draftFolder,
        apiPort: values.apiPort,
        ngrokAuthToken: values.ngrokAuthToken,
        ngrokRegion: values.ngrokRegion,
        relayWorkerUrl: values.relayWorkerUrl,
        themeMode: values.themeMode,
        transferEnabled: values.transferEnabled,
      });
      msgApi.success("设置已保存");
    } catch (e: unknown) {
      msgApi.error(`保存失败: ${(e as Error).message}`);
    }
  };

  const handleDetect = async () => {
    try {
      const path = await detectDraftPath();
      if (path) {
        form.setFieldValue("draftFolder", path);
        msgApi.success(`已检测到路径: ${path}`);
      } else {
        msgApi.warning("未检测到剪映草稿路径");
      }
    } catch (e: unknown) {
      msgApi.error(`检测失败: ${(e as Error).message}`);
    }
  };

  return (
    <>
      {ctx}
      <Title level={3}>系统设置</Title>

      <Form
        form={form}
        layout="vertical"
        style={{ maxWidth: 1024, marginTop: 16 }}
      >
        {/* 路径设置 */}
        <Card title="📁 路径设置" style={{ marginBottom: 16 }}>
          <Form.Item name="draftFolder" label="剪映草稿文件夹">
            <Space.Compact style={{ width: "100%" }}>
              <Form.Item name="draftFolder" noStyle>
                <Input placeholder="留空则使用应用内部目录" />
              </Form.Item>
              <Button icon={<FolderOpenOutlined />} onClick={handleDetect}>
                自动检测
              </Button>
            </Space.Compact>
          </Form.Item>
          <Form.Item
            name="transferEnabled"
            label="启用传输到草稿目录"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>
        </Card>

        {/* API 设置 */}
        <Card title="🔗 API 设置" style={{ marginBottom: 16 }}>
          <Form.Item name="apiPort" label="Coze API 端口">
            <Input style={{ width: 120 }} placeholder="20211" />
          </Form.Item>
          <Divider />
          <Form.Item name="ngrokAuthToken" label="ngrok Authtoken">
            <Input.Password placeholder="从 ngrok 控制台获取" />
          </Form.Item>
          <Form.Item name="ngrokRegion" label="ngrok 区域">
            <Select
              style={{ width: 120 }}
              options={["us", "eu", "ap", "au", "sa", "jp", "in"].map((v) => ({
                value: v,
                label: v,
              }))}
            />
          </Form.Item>
        </Card>

        {/* 云服务设置 */}
        <Card title="☁️ 云服务" style={{ marginBottom: 16 }}>
          <Form.Item name="relayWorkerUrl" label="Relay Worker URL">
            <Input placeholder="https://api.example.com/coze2jianying" />
          </Form.Item>
        </Card>

        {/* 外观 */}
        <Card title="🎨 外观" style={{ marginBottom: 16 }}>
          <Form.Item name="themeMode" label="主题模式">
            <Select
              style={{ width: 140 }}
              options={[
                { value: "system", label: "跟随系统" },
                { value: "light", label: "浅色" },
                { value: "dark", label: "深色" },
              ]}
            />
          </Form.Item>
        </Card>

        <Space>
          <Button
            type="primary"
            icon={<SaveOutlined />}
            loading={isSaving}
            onClick={handleSave}
          >
            保存设置
          </Button>
          <Button icon={<ReloadOutlined />} onClick={() => void loadSettings()}>
            重置
          </Button>
        </Space>
      </Form>
    </>
  );
};

export default SettingsPage;
