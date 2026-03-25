import { Tour, type TourProps } from "antd";
import { useCallback, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import { markOnboardingComplete } from "@/routes/Onboarding/storage";
import { useTourStore } from "@/store/tour";

/**
 * 全局 overlay Tour 组件，挂载在 AppShell 中（路由树根部），
 * 通过 data-tour 属性选择器定位真实页面元素，无需持有任何 ref。
 *
 * Step 0: 高亮侧边栏「设置」导航项 [data-tour="settings-nav"]
 * Step 1: 自动导航至 /settings，高亮草稿路径输入区 [data-tour="draft-path"]
 */
const TourLayer = () => {
  const navigate = useNavigate();
  const open = useTourStore((s) => s.open);
  const closeTour = useTourStore((s) => s.closeTour);
  const [step, setStep] = useState(0);

  const handleChange = useCallback(
    (current: number) => {
      // 进入 step 1（配置草稿路径）时自动跳转到设置页面；
      // antd Tour 在下一渲染周期才对 target() 求值，届时 Settings 页已挂载
      if (current === 1) {
        void navigate("/settings");
      }
      setStep(current);
    },
    [navigate],
  );

  const handleFinish = useCallback(() => {
    markOnboardingComplete();
    closeTour();
  }, [closeTour]);

  const steps: TourProps["steps"] = useMemo(
    () => [
      {
        title: "指引",
        description:
          "Coze2JianYing依赖于电脑本机的「剪映」软件，\n请确保您已经安装，并根据当前指引完成配置，\n点击「>」将自动跳转至设置页面，引导您完成剪映草稿路径的配置。",
        target: () =>
          document.querySelector(
            '[data-tour="settings-nav"]',
          ) as unknown as HTMLElement,
        nextButtonProps: { children: ">" },
      },
      {
        title: "配置剪映草稿路径",
        description:
          "在此处手动填写或点击「自动检测」按钮检测剪映草稿文件夹路径。配置完成后点击「完成」返回拉取模式页面。",
        target: () =>
          document.querySelector(
            '[data-tour="draft-path"]',
          ) as unknown as HTMLElement,
        prevButtonProps: { children: "<" },
      },
    ],
    [],
  );

  return (
    <Tour
      current={step}
      open={open}
      steps={steps}
      onChange={handleChange}
      onClose={handleFinish}
      onFinish={handleFinish}
    />
  );
};

export default TourLayer;
