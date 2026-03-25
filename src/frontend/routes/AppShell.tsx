import { useEffect } from "react";
import { Outlet } from "react-router-dom";

import TourLayer from "@/features/Tour/TourLayer";
import { useTourStore } from "@/store/tour";
import { hasCompletedOnboarding } from "@/routes/Onboarding/storage";

/**
 * 根路由包装壳，挂载在所有路由之上。
 * - 渲染子路由（<Outlet />）
 * - 挂载全局 TourLayer（overlay Tour，不属于任何具体布局）
 * - 首次进入时自动启动 Tour（无需独立 onboarding 页面）
 */
const AppShell = () => {
  const startTour = useTourStore((s) => s.startTour);

  useEffect(() => {
    if (!hasCompletedOnboarding()) {
      startTour();
    }
    // 仅在组件挂载时执行一次
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <>
      <Outlet />
      <TourLayer />
    </>
  );
};

export default AppShell;
