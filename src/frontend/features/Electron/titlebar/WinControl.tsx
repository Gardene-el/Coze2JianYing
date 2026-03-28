import { createStaticStyles } from 'antd-style'

/**
 * Windows native window-control button placeholder.
 * Reserves 132 px so draggable content doesn't overlap the native
 * min/max/close overlay buttons rendered by Electron's titleBarOverlay.
 *
 * lobehub uses `style={{ width: 132 }}` inline, but a VS Code lint rule in
 * this workspace forbids inline styles — createStaticStyles is used instead
 * as a module-level static object (NOT a hook, must NOT be called as a function).
 */
const styles = createStaticStyles(({ css }) => ({
  root: css`
    width: 132px;
  `,
}))

const WinControl = () => <div className={styles.root} />

export default WinControl
