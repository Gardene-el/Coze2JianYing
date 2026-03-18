/**
 * PageHeader — 对齐 LobeHub SettingHeader
 *
 * 渲染大标题（fontSize=24）+ 可选右侧操作区 + 分割线（margin:0）。
 * 消费方无需自己写 Title / Divider，保持各页样式统一。
 */
import { Flexbox, Text } from "@lobehub/ui";
import { Divider } from "antd";
import { type FC, type ReactNode } from "react";

interface PageHeaderProps {
  /** 右侧可选操作区（按钮等） */
  extra?: ReactNode;
  /** 页面大标题 */
  title: ReactNode;
}

const PageHeader: FC<PageHeaderProps> = ({ title, extra }) => {
  return (
    <Flexbox gap={24} style={{ paddingTop: 12 }}>
      <Flexbox horizontal align={"center"} justify={"space-between"}>
        <Text strong fontSize={24}>
          {title}
        </Text>
        {extra}
      </Flexbox>
      <Divider style={{ margin: 0 }} />
    </Flexbox>
  );
};

export default PageHeader;
