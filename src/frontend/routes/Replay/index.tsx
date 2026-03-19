import { SearchOutlined } from "@ant-design/icons";
import { Button, Card, Input, message, Spin } from "antd";
import { createStaticStyles } from "antd-style";
import { useState } from "react";

import PageContainer from "@/components/PageContainer";
import PageHeader from "@/components/PageHeader";
import { guiReplayAPI } from "@/services/gui/replay";

const styles = createStaticStyles(({ css, cssVar }) => ({
  json: css`
    width: 100%;
    max-height: 500px;
    overflow: auto;
    padding: 12px;
    font-family: ${cssVar.fontFamilyCode};
    font-size: 12px;
    line-height: 1.6;
    background: ${cssVar.colorBgLayout};
    border: 1px solid ${cssVar.colorBorderSecondary};
    border-radius: ${cssVar.borderRadius};
    white-space: pre;
  `,
}));

const ReplayPage = () => {
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
    <PageContainer>
      {ctx}
      <PageHeader title="拉取模式" />
      <Card>
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
    </PageContainer>
  );
};

export default ReplayPage;
