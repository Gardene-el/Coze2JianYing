import { FolderOpenOutlined, ReloadOutlined } from "@ant-design/icons";
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
import { useTheme as useNextThemesTheme } from "next-themes";
import { useEffect, useRef } from "react";

import { useSettingsStore } from "@/store/settings/store";

const { Title, Text } = Typography;

const SettingsPage = () => {
  const [form] = Form.useForm();
  const [msgApi, ctx] = message.useMessage();

  const { theme: currentTheme, setTheme } = useNextThemesTheme();

  const {
    draftFolder,
    apiPort,
    ngrokAuthToken,
    ngrokRegion,
    relayWorkerUrl,
    transferEnabled,
    loadSettings,
    saveSettings,
    detectDraftPath,
  } = useSettingsStore();

  // debounce 计时器，500ms 内无操作才真正保存
  const saveTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

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
      transferEnabled,
    });
  }, [
    draftFolder,
    apiPort,
    ngrokAuthToken,
    ngrokRegion,
    relayWorkerUrl,
    transferEnabled,
    form,
  ]);

  /** 表单任意字段变化时 debounce 500ms 自动保存到 Python 后端 */
  const handleValuesChange = (
    _: unknown,
    allValues: Record<string, unknown>,
  ) => {
    if (saveTimerRef.current) clearTimeout(saveTimerRef.current);
    saveTimerRef.current = setTimeout(async () => {
      try {
        await saveSettings({
          draftFolder: allValues.draftFolder as string,
          apiPort: allValues.apiPort as string,
          ngrokAuthToken: allValues.ngrokAuthToken as string,
          ngrokRegion: allValues.ngrokRegion as string,
          relayWorkerUrl: allValues.relayWorkerUrl as string,
          transferEnabled: allValues.transferEnabled as boolean,
        });
        msgApi.success("已自动保存", 1.5);
      } catch (e: unknown) {
        msgApi.error(`保存失败: ${(e as Error).message}`);
      }
    }, 500);
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
        onValuesChange={handleValuesChange}
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
          {/* 主题模式由 next-themes 管理，存储在 localStorage，不经过 Python 后端 */}
          <Form.Item label="主题模式">
            <Select
              style={{ width: 140 }}
              value={currentTheme ?? "system"}
              options={[
                { value: "system", label: "跟随系统" },
                { value: "light", label: "浅色" },
                { value: "dark", label: "深色" },
              ]}
              onChange={(v) => setTheme(v)}
            />
          </Form.Item>
        </Card>

        <Space>
          <Button icon={<ReloadOutlined />} onClick={() => void loadSettings()}>
            重置
          </Button>
        </Space>
      </Form>
    </>
  );
};

export default SettingsPage;
