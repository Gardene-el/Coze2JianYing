import { SearchOutlined } from "@ant-design/icons";
import { Button, Card, Input, message, Spin, Typography } from "antd";
import { createStyles } from "antd-style";
import { useState } from "react";

import { guiReplayAPI } from "@/services/gui/replay";

const { Title, Text } = Typography;

const useStyles = createStyles(({ token, css }) => ({
  json: css`
    width: 100%;
    max-height: 500px;
    overflow: auto;
    padding: 12px;
    font-family: ${token.fontFamilyCode};
    font-size: 12px;
    line-height: 1.6;
    background: ${token.colorBgLayout};
    border: 1px solid ${token.colorBorderSecondary};
    border-radius: ${token.borderRadius}px;
    white-space: pre;
  `,
}));

const ReplayPage = () => {
  const { styles } = useStyles();
  const [msgApi, ctx] = message.useMessage();
  const [draftId, setDraftId] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<object | null>(null);

  const handleQuery = async () => {
    if (!draftId.trim()) return msgApi.warning("请输入 Draft ID");
    setLoading(true);
    setResult(null);
    try {
      const data = await guiReplayAPI.get(draftId.trim());
      setResult(data);
    } catch (e: unknown) {
      msgApi.error(`查询失败: ${(e as Error).message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {ctx}
      <Title level={3}>回放查看</Title>
      <Text type="secondary">
        通过 Draft ID 查询 Cloudflare Worker 上记录的调用回放
      </Text>

      <Card style={{ marginTop: 16 }}>
        <Input.Search
          value={draftId}
          onChange={(e) => setDraftId(e.target.value)}
          placeholder="输入 Draft ID，例如 1710000000000-xxxxx"
          enterButton={
            <>
              <SearchOutlined /> 查询
            </>
          }
          loading={loading}
          onSearch={handleQuery}
          style={{ maxWidth: 560, marginBottom: 16 }}
        />

        {loading && <Spin />}

        {result && !loading && (
          <div className={styles.json}>{JSON.stringify(result, null, 2)}</div>
        )}
      </Card>
    </>
  );
};

export default ReplayPage;
