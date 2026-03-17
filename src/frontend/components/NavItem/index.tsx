import type { ReactNode } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { cx } from "antd-style";

import { useNavItemStyles } from "./style";

interface NavItemProps {
  to: string;
  icon: ReactNode;
  label: string;
}

const NavItem = ({ to, icon, label }: NavItemProps) => {
  const { styles } = useNavItemStyles();
  const navigate = useNavigate();
  const { pathname } = useLocation();

  const isActive = pathname === to;

  return (
    <div
      className={cx(styles.item, { [styles.active]: isActive })}
      onClick={() => navigate(to)}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === "Enter" && navigate(to)}
    >
      <span className={styles.icon}>{icon}</span>
      <span>{label}</span>
    </div>
  );
};

export default NavItem;
