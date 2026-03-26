/**
 * CloudflareCard — settings & controls for the Cloudflare Tunnel provider.
 *
 * Two modes:
 *  - Quick tunnel (token empty): no account needed, gets a *.trycloudflare.com URL
 *  - Named tunnel (token filled): persistent domain via cloudflared
 */
import {
  CheckCircleOutlined,
  CloseCircleOutlined,
  CopyOutlined,
} from "@ant-design/icons";
import { Button, Divider, Form, Input, Space, Tooltip, Typography } from "antd";
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

interface CloudflareCardProps {
  port: number;
  serviceRunning: boolean;
  otherTunnelRunning: boolean;
  onSuccess: (msg: string) => void;
  onError: (msg: string) => void;
}

const CloudflareCard = ({
  port,
  serviceRunning,
  otherTunnelRunning,
  onSuccess,
  onError,
}: CloudflareCardProps) => {
  const [form] = Form.useForm();

  const { cloudflareRunning, cloudflareLoading, cloudflareUrl } =
    useServiceStore();
  const { startCloudflare, stopCloudflare } = useServiceStore();
  const { cloudflareTunnelToken, cloudflareTunnelPublicUrl, saveSettings } =
    useSettingsStore();

  const cfToken = Form.useWatch("cfToken", form);

  useEffect(() => {
    form.setFieldsValue({
      cfToken: cloudflareTunnelToken,
      cfPublicUrl: cloudflareTunnelPublicUrl,
    });
  }, [cloudflareTunnelToken, cloudflareTunnelPublicUrl, form]);

  const handleStart = async () => {
    const values = await form.validateFields();
    const token = (values.cfToken as string | undefined) ?? "";
    const publicUrl = (values.cfPublicUrl as string | undefined) ?? "";
    try {
      await saveSettings({
        cloudflareTunnelToken: token,
        cloudflareTunnelPublicUrl: publicUrl,
      });
      const url = await startCloudflare(token, publicUrl, port);
      onSuccess(`Cloudflare 隧道已启动: ${url}`);
    } catch (e: unknown) {
      onError(`Cloudflare 启动失败: ${(e as Error).message}`);
    }
  };

  const handleStop = async () => {
    try {
      await stopCloudflare();
      onSuccess("Cloudflare 隧道已停止");
    } catch (e: unknown) {
      onError(`停止失败: ${(e as Error).message}`);
    }
  };

  return (
    <>
      <Form form={form} layout="vertical" style={{ marginBottom: 12 }}>
        <Form.Item
          name="cfToken"
          label="服务 Token（可选）"
          extra="留空将使用免登录快速隧道（trycloudflare.com），填入 Token 可获得固定域名"
        >
          <Input.Password
            style={{ maxWidth: 400 }}
            placeholder="留空 = 快速隧道，无需账号"
            allowClear
          />
        </Form.Item>
        {cfToken && (
          <Form.Item
            name="cfPublicUrl"
            label="公网域名"
            rules={[{ required: true, message: "命名隧道需要填写公网域名" }]}
            extra="从 Cloudflare Zero Trust 控制台获取，例如 https://my-app.example.com"
          >
            <Input
              style={{ maxWidth: 400 }}
              placeholder="https://my-app.example.com"
            />
          </Form.Item>
        )}
      </Form>

      <Space>
        <Button
          type="primary"
          icon={<CheckCircleOutlined />}
          loading={cloudflareLoading}
          disabled={cloudflareRunning || !serviceRunning || otherTunnelRunning}
          onClick={handleStart}
        >
          启动
        </Button>
        <Button
          danger
          icon={<CloseCircleOutlined />}
          loading={cloudflareLoading}
          disabled={!cloudflareRunning}
          onClick={handleStop}
        >
          停止
        </Button>
      </Space>

      {cloudflareUrl && (
        <>
          <Divider />
          <div className={styles.row}>
            <Text strong>公网地址：</Text>
            <Text code copyable>
              {cloudflareUrl}
            </Text>
            <Tooltip title="复制">
              <Button
                size="small"
                icon={<CopyOutlined />}
                onClick={() => {
                  void navigator.clipboard.writeText(cloudflareUrl);
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

export default CloudflareCard;
