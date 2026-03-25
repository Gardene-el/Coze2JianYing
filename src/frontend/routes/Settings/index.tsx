import { FolderOpenOutlined, ReloadOutlined } from "@ant-design/icons";
import {
  Button,
  Card,
  Form,
  Input,
  message,
  Select,
  Space,
  Switch,
} from "antd";
import { useEffect, useRef } from "react";

import PageContainer from "@/components/PageContainer";
import PageHeader from "@/components/PageHeader";
import { useSettingsStore } from "@/store/settings/store";

const SettingsPage = () => {
  const [form] = Form.useForm();
  const [msgApi, ctx] = message.useMessage();

  const {
    draftFolder,
    ngrokAuthToken,
    ngrokRegion,
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
      ngrokAuthToken,
      ngrokRegion,
      transferEnabled,
    });
  }, [draftFolder, ngrokAuthToken, ngrokRegion, transferEnabled, form]);

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
          ngrokAuthToken: allValues.ngrokAuthToken as string,
          ngrokRegion: allValues.ngrokRegion as string,
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
    <PageContainer>
      {ctx}
      <PageHeader title="设置" />
      <Form
        form={form}
        layout="vertical"
        style={{ maxWidth: 1024, marginTop: 16 }}
        onValuesChange={handleValuesChange}
      >
        {/* 剪映路径 */}
        <Card title="📁 剪映路径" style={{ marginBottom: 16 }}>
          <div data-tour="draft-path">
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
          </div>
          <Form.Item
            name="transferEnabled"
            label="启用传输到草稿目录"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>
        </Card>

        {/* 隧道设置 */}
        <Card title="🚇 隧道设置" style={{ marginBottom: 16 }}>
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

        <Space>
          <Button icon={<ReloadOutlined />} onClick={() => void loadSettings()}>
            重置
          </Button>
        </Space>
      </Form>
    </PageContainer>
  );
};

export default SettingsPage;
