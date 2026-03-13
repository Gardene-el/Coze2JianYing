import {
  CloudServerOutlined,
  CodeOutlined,
  HistoryOutlined,
  SettingOutlined,
} from "@ant-design/icons";
import { FluentEmoji } from "@lobehub/ui";
import { Menu, type MenuProps } from "antd";
import { createStyles } from "antd-style";
import { useLocation, useNavigate } from "react-router-dom";

const useStyles = createStyles(({ token, css }) => ({
  menu: css`
    flex: 1;
    border-inline-end: none !important;
    background: transparent;

    .ant-menu-item {
      border-radius: 8px;
      margin-inline: 8px;
      width: calc(100% - 16px);
    }
  `,
  logo: css`
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 20px 16px 12px;

    font-size: 15px;
    font-weight: 700;
    color: ${token.colorText};
  `,
}));

const items: MenuProps["items"] = [
  { key: "/cloud-service", icon: <CloudServerOutlined />, label: "云端服务" },
  { key: "/draft-generator", icon: <CodeOutlined />, label: "草稿生成" },
  { key: "/script-executor", icon: <CodeOutlined />, label: "脚本执行" },
  { key: "/replay", icon: <HistoryOutlined />, label: "回放查看" },
  { key: "/settings", icon: <SettingOutlined />, label: "系统设置" },
];

const Sidebar = () => {
  const { styles } = useStyles();
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <>
      <div className={styles.logo}>
        <FluentEmoji emoji="📸" size={36} type="anim" />
        <span>Coze2JianYing</span>
      </div>
      <Menu
        className={styles.menu}
        mode="inline"
        selectedKeys={[location.pathname]}
        items={items}
        onClick={({ key }) => navigate(key)}
        inlineIndent={16}
      />
    </>
  );
};

export default Sidebar;
