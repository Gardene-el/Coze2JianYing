import {
  CloudServerOutlined,
  CodeOutlined,
  HistoryOutlined,
  SettingOutlined,
} from "@ant-design/icons";
import { Menu, type MenuProps } from "antd";
import { createStyles } from "antd-style";
import { useLocation, useNavigate } from "react-router-dom";

const useStyles = createStyles(({ css }) => ({
  menu: css`
    border-inline-end: none !important;
    background: transparent;

    .ant-menu-item {
      border-radius: 8px;
      margin-inline: 8px;
      width: calc(100% - 16px);
    }
  `,
}));

const items: MenuProps["items"] = [
  { key: "/cloud-service", icon: <CloudServerOutlined />, label: "云端服务" },
  { key: "/draft-generator", icon: <CodeOutlined />, label: "草稿生成" },
  { key: "/script-executor", icon: <CodeOutlined />, label: "脚本执行" },
  { key: "/replay", icon: <HistoryOutlined />, label: "回放查看" },
  { key: "/settings", icon: <SettingOutlined />, label: "系统设置" },
];

const SidebarBody = () => {
  const { styles } = useStyles();
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <Menu
      className={styles.menu}
      mode="inline"
      selectedKeys={[location.pathname]}
      items={items}
      onClick={({ key }) => navigate(key)}
      inlineIndent={16}
    />
  );
};

export default SidebarBody;
