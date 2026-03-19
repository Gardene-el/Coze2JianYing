import { ClearOutlined, ThunderboltOutlined } from "@ant-design/icons";
import { Button, Card, message, Space, Spin, Typography } from "antd";
import { createStaticStyles } from "antd-style";
import { useRef, useState } from "react";

import PageContainer from "@/components/PageContainer";
import PageHeader from "@/components/PageHeader";
import { guiDraftAPI } from "@/services/gui/draft";

const { Text } = Typography;

const styles = createStaticStyles(({ css, cssVar }) => ({
  textarea: css`
    flex: 1;
    width: 100%;
    min-height: 320px;
    padding: 12px;
    font-family: ${cssVar.fontFamilyCode};
    font-size: 13px;
    line-height: 1.6;
    border: 1px solid ${cssVar.colorBorder};
    border-radius: ${cssVar.borderRadius};
    background: ${cssVar.colorBgContainer};
    color: ${cssVar.colorText};
    resize: vertical;
    outline: none;
    &:focus {
      border-color: ${cssVar.colorPrimary};
    }
  `,
}));

const DraftGeneratorPage = () => {
  const [msgApi, ctx] = message.useMessage();
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("就绪");
  const textRef = useRef<HTMLTextAreaElement>(null);

  const handleGenerate = async () => {
    const content = textRef.current?.value.trim();
    if (!content) {
      msgApi.warning("请先粘贴 Coze 插件 JSON 数据");
      return;
    }
    setLoading(true);
    setStatus("正在生成…");
    try {
      await guiDraftAPI.generate(content);
      setStatus("生成成功 ✓");
      msgApi.success("草稿已生成");
    } catch (e: unknown) {
      setStatus("生成失败");
      msgApi.error(`生成失败: ${(e as Error).message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    if (textRef.current) textRef.current.value = "";
    setStatus("就绪");
  };

  return (
    <PageContainer>
      {ctx}
      <PageHeader title="粘贴草稿（弃置）" />
      <Card>
        <textarea
          ref={textRef}
          className={styles.textarea}
          placeholder="粘贴 JSON 数据…"
        />
        <Space
          style={{
            marginTop: 12,
            width: "100%",
            justifyContent: "space-between",
          }}
          wrap
        >
          <Text type="secondary">
            状态：
            {loading ? (
              <>
                <Spin size="small" /> {status}
              </>
            ) : (
              status
            )}
          </Text>
          <Space>
            <Button icon={<ClearOutlined />} onClick={handleClear}>
              清空内容
            </Button>
            <Button
              type="primary"
              icon={<ThunderboltOutlined />}
              loading={loading}
              onClick={handleGenerate}
            >
              生成草稿
            </Button>
          </Space>
        </Space>
      </Card>
    </PageContainer>
  );
};

export default DraftGeneratorPage;
