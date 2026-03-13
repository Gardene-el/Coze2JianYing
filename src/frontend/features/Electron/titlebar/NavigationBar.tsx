import { ActionIcon, Flexbox } from "@lobehub/ui";
import { ArrowLeft, ArrowRight } from "lucide-react";
import { memo } from "react";

import { electronStylish } from "@/styles/electron";

import { useNavigationHistory } from "../navigation/useNavigationHistory";

/** Back / forward navigation buttons, pinned to the far left of the title bar. */
const NavigationBar = memo(() => {
  const { canGoBack, canGoForward, goBack, goForward } = useNavigationHistory();

  return (
    <Flexbox
      horizontal
      align="center"
      className={electronStylish.nodrag}
      gap={2}
    >
      <ActionIcon
        disabled={!canGoBack}
        icon={ArrowLeft}
        size="small"
        onClick={goBack}
      />
      <ActionIcon
        disabled={!canGoForward}
        icon={ArrowRight}
        size="small"
        onClick={goForward}
      />
    </Flexbox>
  );
});

export default NavigationBar;
