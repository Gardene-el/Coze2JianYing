/**
 * NgrokCard — settings & controls for the ngrok tunnel provider.
 */
import {
  CheckCircleOutlined,
  CloseCircleOutlined,
  CopyOutlined,
} from "@ant-design/icons";
import {
  Button,
  Divider,
  Form,
  Input,
  Select,
  Space,
  Tooltip,
  Typography,
} from "antd";
import { createStaticStyles } from "antd-style";
import { useEffect } from "react";

import { useServiceStore } from "@/store/service/store";
import { useSettingsStore } from "@/store/settings/store";

const { Text } = Typography;

const styles = createStaticStyles(({ css }) => ({
  row: css`
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
  `,
}));

interface NgrokCardProps {
  /** Port the local Coze API service is listening on. */
  port: number;
  /** Whether the Coze API service is running; controls button disabled state. */
  serviceRunning: boolean;
  /** Whether any other tunnel is already running (mutual exclusion). */
  otherTunnelRunning: boolean;
  onSuccess: (msg: string) => void;
  onError: (msg: string) => void;
}

const NgrokCard = ({
  port,
  serviceRunning,
  otherTunnelRunning,
  onSuccess,
  onError,
}: NgrokCardProps) => {
  const [form] = Form.useForm();

  const { ngrokRunning, ngrokLoading, ngrokUrl } = useServiceStore();
  const { startNgrok, stopNgrok } = useServiceStore();
  const { ngrokAuthToken, ngrokRegion, saveSettings } = useSettingsStore();

  useEffect(() => {
    form.setFieldsValue({ ngrokToken: ngrokAuthToken, ngrokRegion });
  }, [ngrokAuthToken, ngrokRegion, form]);

  const handleStart = async () => {
    const values = await form.validateFields();
    try {
      await saveSettings({
        ngrokAuthToken: values.ngrokToken as string,
        ngrokRegion: values.ngrokRegion as string,
      });
      const url = await startNgrok(
        values.ngrokToken as string,
        values.ngrokRegion as string,
        port,
      );
      onSuccess(`ngrok 已启动: ${url}`);
    } catch (e: unknown) {
      onError(`ngrok 启动失败: ${(e as Error).message}`);
    }
  };

  const handleStop = async () => {
    try {
      await stopNgrok();
      onSuccess("ngrok 已停止");
    } catch (e: unknown) {
      onError(`停止失败: ${(e as Error).message}`);
    }
  };

  return (
    <>
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

      <Space>
        <Button
          type="primary"
          icon={<CheckCircleOutlined />}
          loading={ngrokLoading}
          disabled={ngrokRunning || !serviceRunning || otherTunnelRunning}
          onClick={handleStart}
        >
          启动
        </Button>
        <Button
          danger
          icon={<CloseCircleOutlined />}
          loading={ngrokLoading}
          disabled={!ngrokRunning}
          onClick={handleStop}
        >
          停止
        </Button>
      </Space>

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
                  onSuccess("已复制");
                }}
              />
            </Tooltip>
          </div>
        </>
      )}
    </>
  );
};

export default NgrokCard;
