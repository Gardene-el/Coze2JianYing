const ONBOARDING_KEY = "c2j-onboarding";

// VITE_FORCE_ONBOARDING=1 时在模块加载时清除标记，模拟"首次启动"
// 这样引导流程走完后，markOnboardingComplete() 能正常写入，导航不会死循环
if (import.meta.env.VITE_FORCE_ONBOARDING === "1") {
  localStorage.removeItem(ONBOARDING_KEY);
}

export const hasCompletedOnboarding = (): boolean => {
  return !!localStorage.getItem(ONBOARDING_KEY);
};

/** 写入完成标记（值为时间戳，便于问题排查） */
export const markOnboardingComplete = (): void => {
  localStorage.setItem(ONBOARDING_KEY, Date.now().toString());
};
