import { CLASSNAMES } from '@lobehub/ui'
import type { Theme } from 'antd-style'
import { css } from 'antd-style'

// fix ios input keyboard / overflow hidden
// ref: https://zhuanlan.zhihu.com/p/113855026
// eslint-disable-next-line unicorn/no-anonymous-default-export
export default ({ token }: { prefixCls: string; token: Theme }) => css`
  html,
  body,
  #root {
    position: relative;

    overscroll-behavior: none;

    height: 100%;
    min-height: 100dvh;
    max-height: 100dvh;

    @media (device-width >= 576px) {
      overflow: hidden;
    }
  }

  body {
    /* 提高合成层级，强制硬件加速，否则会有渲染黑边 */
    will-change: opacity;
    transform: translateZ(0);
  }

  * {
    /* scrollbar-color/scrollbar-width supported from Chrome 121 */
    scrollbar-color: ${token.colorFill} transparent;
    scrollbar-width: thin;

    /* 移动端滚动容器隐藏滚动条 */
    #lobe-mobile-scroll-container {
      scrollbar-width: none;

      ::-webkit-scrollbar {
        width: 0;
        height: 0;
      }
    }

    ::-webkit-scrollbar {
      width: 0.75em;
      height: 0.75em;
    }

    ::-webkit-scrollbar-thumb {
      border-radius: 10px;
    }

    :hover::-webkit-scrollbar-thumb {
      border: 3px solid transparent;
      background-color: ${token.colorText};
      background-clip: content-box;
    }

    ::-webkit-scrollbar-track {
      background-color: transparent;
    }
  }

  button {
    -webkit-app-region: no-drag;
  }

  /* @lobehub/ui ContextTrigger / DropdownMenuTrigger 打开时高亮背景 */
  .${CLASSNAMES.ContextTrigger}[data-popup-open]:not([data-no-highlight]),
  .${CLASSNAMES.DropdownMenuTrigger}[data-popup-open]:not([data-no-highlight]) {
    background: ${token.colorFillTertiary};
  }
  .accordion-action:has(
    .${CLASSNAMES.DropdownMenuTrigger}[data-popup-open]:not([data-no-highlight])
  ) {
    opacity: 1;
  }
`
