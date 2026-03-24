import {
  CheckCircleOutlined,
  CloseCircleOutlined,
  CopyOutlined,
  GlobalOutlined,
  PlayCircleOutlined,
  ReloadOutlined,
  StopOutlined,
} from "@ant-design/icons";
import {
  Badge,
  Button,
  Card,
  Divider,
  Form,
  Input,
  message,
  Select,
  Space,
  Tag,
  Tooltip,
  Typography,
} from "antd";
import { createStaticStyles } from "antd-style";
import { useEffect, useRef, useState } from "react";

import PageContainer from "@/components/PageContainer";
import PageHeader from "@/components/PageHeader";
import { useServiceStatus } from "@/hooks/useServiceStatus";
import { useServiceStore } from "@/store/service/store";
import { initialSettingsState } from "@/store/settings/initialState";
import { useSettingsStore } from "@/store/settings/store";

const DEFAULT_API_PORT = initialSettingsState.apiPort;

const { Text } = Typography;

const styles = createStaticStyles(({ css }) => ({
  row: css`
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
  `,
}));

const CloudServicePage = () => {
  const [form] = Form.useForm();
  const [msgApi, ctx] = message.useMessage();

  // 状态
  const { isRunning, isLoading, ngrokRunning, ngrokLoading, ngrokUrl } =
    useServiceStore();
  const { startService, stopService, startNgrok, stopNgrok } =
    useServiceStore();
  const { apiPort, ngrokAuthToken, ngrokRegion, loadSettings } =
    useSettingsStore();
  const { saveSettings } = useSettingsStore();

  const [portInput, setPortInput] = useState(apiPort);
  const portSaveTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    setPortInput(apiPort);
  }, [apiPort]);

  const handlePortChange = (value: string) => {
    setPortInput(value);
    if (portSaveTimerRef.current) clearTimeout(portSaveTimerRef.current);
    portSaveTimerRef.current = setTimeout(async () => {
      try {
        await saveSettings({ apiPort: value });
        msgApi.success("已保存", 1);
      } catch (e: unknown) {
        msgApi.error(`保存失败: ${(e as Error).message}`);
      }
    }, 500);
  };

  const handlePortReset = async () => {
    setPortInput(DEFAULT_API_PORT);
    try {
      await saveSettings({ apiPort: DEFAULT_API_PORT });
      msgApi.success("已重置为默认端口", 1.5);
    } catch (e: unknown) {
      msgApi.error(`重置失败: ${(e as Error).message}`);
    }
  };

  // 轮询服务状态
  useServiceStatus();

  useEffect(() => {
    void loadSettings();
  }, [loadSettings]);

  useEffect(() => {
    form.setFieldsValue({ ngrokToken: ngrokAuthToken, ngrokRegion });
  }, [ngrokAuthToken, ngrokRegion, form]);

  // ---- 服务启停 ----
  const handleStartService = async () => {
    try {
      await startService();
      msgApi.success("Coze API 服务已启动");
    } catch (e: unknown) {
      msgApi.error(`启动失败: ${(e as Error).message}`);
    }
  };

  const handleStopService = async () => {
    try {
      await stopService();
      msgApi.success("服务已停止");
    } catch (e: unknown) {
      msgApi.error(`停止失败: ${(e as Error).message}`);
    }
  };

  // ---- ngrok ----
  const handleStartNgrok = async () => {
    const values = await form.validateFields();
    try {
      await saveSettings({
        ngrokAuthToken: values.ngrokToken,
        ngrokRegion: values.ngrokRegion,
      });
      const url = await startNgrok(
        values.ngrokToken,
        values.ngrokRegion,
        Number(portInput),
      );
      msgApi.success(`ngrok 已启动: ${url}`);
    } catch (e: unknown) {
      msgApi.error(`ngrok 启动失败: ${(e as Error).message}`);
    }
  };

  const handleStopNgrok = async () => {
    try {
      await stopNgrok();
      msgApi.success("ngrok 已停止");
    } catch (e: unknown) {
      msgApi.error(`停止失败: ${(e as Error).message}`);
    }
  };

  return (
    <PageContainer>
      {ctx}
      <PageHeader title="直连模式" />
      {/* Coze API 服务 */}
      <Card
        title={
          <Space>
            <span>Coze API 服务</span>
            <Badge
              status={isRunning ? "success" : "default"}
              text={isRunning ? "运行中" : "已停止"}
            />
          </Space>
        }
        style={{ marginBottom: 16 }}
      >
        <Space wrap>
          <Space.Compact size="small">
            <Input
              value={portInput}
              onChange={(e) => handlePortChange(e.target.value)}
              style={{ width: 80 }}
              placeholder={DEFAULT_API_PORT}
            />
            <Tooltip title="重置端口">
              <Button icon={<ReloadOutlined />} onClick={handlePortReset} />
            </Tooltip>
          </Space.Compact>
          <Button
            type="primary"
            icon={<PlayCircleOutlined />}
            loading={isLoading}
            disabled={isRunning}
            onClick={handleStartService}
          >
            启动服务
          </Button>
          <Button
            danger
            icon={<StopOutlined />}
            loading={isLoading}
            disabled={!isRunning}
            onClick={handleStopService}
          >
            停止服务
          </Button>
        </Space>
      </Card>

      {/* ngrok 内网穿透 */}
      <Card
        title={
          <Space>
            <GlobalOutlined />
            <span>ngrok 内网穿透</span>
            <Tag color={ngrokRunning ? "success" : "default"}>
              {ngrokRunning ? "运行中" : "未启动"}
            </Tag>
          </Space>
        }
      >
        <Form form={form} layout="inline" style={{ marginBottom: 12 }}>
          <Form.Item
            name="ngrokToken"
            label="Authtoken"
            rules={[{ required: true, message: "请填写 ngrok Authtoken" }]}
          >
            <Input.Password
              style={{ width: 280 }}
              placeholder="ngrok Authtoken"
            />
          </Form.Item>
          <Form.Item name="ngrokRegion" label="区域" initialValue="us">
            <Select
              style={{ width: 90 }}
              options={["us", "eu", "ap", "au", "sa", "jp", "in"].map((v) => ({
                value: v,
                label: v,
              }))}
            />
          </Form.Item>
        </Form>

        <div className={styles.row}>
          <Button
            type="primary"
            icon={<CheckCircleOutlined />}
            loading={ngrokLoading}
            disabled={ngrokRunning || !isRunning}
            onClick={handleStartNgrok}
          >
            启动 ngrok
          </Button>
          <Button
            danger
            icon={<CloseCircleOutlined />}
            loading={ngrokLoading}
            disabled={!ngrokRunning}
            onClick={handleStopNgrok}
          >
            停止 ngrok
          </Button>
        </div>

        {ngrokUrl && (
          <>
            <Divider />
            <div className={styles.row}>
              <Text strong>公网地址：</Text>
              <Text code copyable>
                {ngrokUrl}
              </Text>
              <Tooltip title="复制">
                <Button
                  size="small"
                  icon={<CopyOutlined />}
                  onClick={() => {
                    void navigator.clipboard.writeText(ngrokUrl);
                    msgApi.success("已复制");
                  }}
                />
              </Tooltip>
            </div>
          </>
        )}
      </Card>
    </PageContainer>
  );
};

export default CloudServicePage;
