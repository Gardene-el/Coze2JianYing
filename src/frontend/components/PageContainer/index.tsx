/**
 * PageContainer — 对齐 LobeHub SettingContainer
 *
 * 外层 Flexbox 水平居中（align='center'），内层受 maxWidth 约束。
 * 同时接管垂直滚动（overflowY: 'auto'），因此上层 Content 需设为 overflow: hidden。
 */
import { type FlexboxProps, Flexbox } from "@lobehub/ui";
import { type PropsWithChildren, memo } from "react";

interface PageContainerProps extends FlexboxProps {
  /** 内容最大宽度，默认 1024px，对齐 LobeHub MAX_WIDTH */
  maxWidth?: number | string;
}

const PageContainer = memo<PropsWithChildren<PageContainerProps>>(
  ({ maxWidth = 1024, children, style, ...rest }) => {
    return (
      <Flexbox
        align={"center"}
        height={"100%"}
        width={"100%"}
        style={{
          overflowX: "hidden",
          overflowY: "auto",
          ...style,
        }}
        {...rest}
      >
        <Flexbox
          flex={1}
          gap={36}
          width={"100%"}
          style={{
            maxWidth,
            padding: "24px",
          }}
        >
          {children}
        </Flexbox>
      </Flexbox>
    );
  },
);

PageContainer.displayName = "PageContainer";

export default PageContainer;
