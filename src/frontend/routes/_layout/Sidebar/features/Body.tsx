import {
  ApiOutlined,
  CloudServerOutlined,
  CodeOutlined,
  EditOutlined,
  HistoryOutlined,
  SettingOutlined,
  ThunderboltOutlined,
  ToolOutlined,
} from '@ant-design/icons'
import { Accordion, Flexbox } from '@lobehub/ui'
import CollapsibleNavGroup from '@/components/CollapsibleNavGroup'
import NavItem from '@/components/NavItem'
import { systemStatusSelectors } from '@/store/global/selectors/systemStatus'
import { useGlobalStore } from '@/store/global/store'

const SidebarBody = () => {
  const expandedGroups = useGlobalStore(systemStatusSelectors.expandedSidebarGroups)
  const updateSystemStatus = useGlobalStore((s) => s.updateSystemStatus)

  return (
    <Flexbox gap={4} style={{ paddingBlock: 4 }}>
      <Accordion
        expandedKeys={expandedGroups}
        onExpandedChange={(keys) => updateSystemStatus({ expandedSidebarGroups: keys as string[] })}
        gap={4}
        indicatorPlacement="end"
      >
        <CollapsibleNavGroup groupKey="auto" title="云端" icon={<ApiOutlined />}>
          <NavItem to="/cloud-service" icon={<CloudServerOutlined />} label="直连模式" />
          <NavItem to="/replay" icon={<HistoryOutlined />} label="拉取模式" />
        </CollapsibleNavGroup>

        <CollapsibleNavGroup groupKey="manual" title="手动" icon={<ThunderboltOutlined />}>
          <NavItem to="/script-executor" icon={<CodeOutlined />} label="粘贴脚本" />
          <NavItem to="/draft-generator" icon={<EditOutlined />} label="粘贴草稿（弃置）" />
        </CollapsibleNavGroup>

        <CollapsibleNavGroup groupKey="tools" title="工具" icon={<ToolOutlined />}>
          <NavItem to="/tool-generator" icon={<ToolOutlined />} label="插件生成器" />
        </CollapsibleNavGroup>
      </Accordion>

      <div data-tour="settings-nav">
        <NavItem to="/settings" icon={<SettingOutlined />} label="设置" />
      </div>
    </Flexbox>
  )
}

export default SidebarBody
