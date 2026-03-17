import type { Key } from "react";
import {
  ApiOutlined,
  ClockCircleOutlined,
  CloudServerOutlined,
  CodeOutlined,
  EditOutlined,
  HistoryOutlined,
  SettingOutlined,
  ThunderboltOutlined,
} from "@ant-design/icons";
import { Accordion, Flexbox } from "@lobehub/ui";

import { useGlobalStore } from "@/store/global/store";
import { systemStatusSelectors } from "@/store/global/selectors/systemStatus";
import CollapsibleNavGroup from "@/components/CollapsibleNavGroup";
import NavItem from "@/components/NavItem";

const SidebarBody = () => {
  const expandedGroups = useGlobalStore(
    systemStatusSelectors.expandedSidebarGroups,
  );
  const updateSystemStatus = useGlobalStore((s) => s.updateSystemStatus);

  return (
    <Flexbox gap={4} style={{ paddingBlock: 4 }}>
      <Accordion
        expandedKeys={expandedGroups}
        onExpandedChange={(keys) =>
          updateSystemStatus({ expandedSidebarGroups: keys as string[] })
        }
        gap={4}
        indicatorPlacement="end"
      >
        <CollapsibleNavGroup
          groupKey="auto"
          title="自动方案"
          icon={<ApiOutlined />}
        >
          <NavItem
            to="/cloud-service"
            icon={<CloudServerOutlined />}
            label="云端服务"
          />
          <NavItem to="/replay" icon={<HistoryOutlined />} label="回放查看" />
        </CollapsibleNavGroup>

        <CollapsibleNavGroup
          groupKey="manual"
          title="手动方案"
          icon={<ThunderboltOutlined />}
        >
          <NavItem
            to="/script-executor"
            icon={<CodeOutlined />}
            label="脚本执行"
          />
        </CollapsibleNavGroup>

        <CollapsibleNavGroup
          groupKey="legacy"
          title="过时方案"
          icon={<ClockCircleOutlined />}
        >
          <NavItem
            to="/draft-generator"
            icon={<EditOutlined />}
            label="草稿生成"
          />
        </CollapsibleNavGroup>
      </Accordion>

      <NavItem to="/settings" icon={<SettingOutlined />} label="系统设置" />
    </Flexbox>
  );
};

export default SidebarBody;
