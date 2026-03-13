import {
  ClearOutlined,
  DownOutlined,
  PauseOutlined,
  UpOutlined,
} from "@ant-design/icons";
import { Button, Tooltip } from "antd";
import { createStyles } from "antd-style";
import { useEffect, useRef } from "react";

import { useLogStore } from "@/store/log/store";
import { useSSELog } from "@/hooks/useSSELog";
import type { LogEntry } from "@/store/log/initialState";

const LEVEL_COLORS: Record<LogEntry["level"], string> = {
  DEBUG: "#8c8c8c",
  INFO: "#52c41a",
  WARNING: "#faad14",
  ERROR: "#f5222d",
  CRITICAL: "#ff4d4f",
};

const useStyles = createStyles(({ token, css }) => ({
  panel: css`
    display: flex;
    flex-direction: column;
    height: 180px;
    border-top: 1px solid ${token.colorBorderSecondary};
    background: ${token.colorBgLayout};
  `,
  toolbar: css`
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 4px 8px;
    border-bottom: 1px solid ${token.colorBorderSecondary};
    font-size: 12px;
    color: ${token.colorTextSecondary};
  `,
  dot: css`
    display: inline-block;
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #52c41a;
    box-shadow: 0 0 4px 2px rgba(82, 196, 26, 0.4);
    animation: pulse 1.5s ease-in-out infinite;
    @keyframes pulse {
      0%,
      100% {
        opacity: 1;
      }
      50% {
        opacity: 0.4;
      }
    }
  `,
  dotOff: css`
    display: inline-block;
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: ${token.colorTextQuaternary};
  `,
  log: css`
    flex: 1;
    overflow-y: auto;
    padding: 4px 12px;
    font-family: ${token.fontFamilyCode};
    font-size: 12px;
    line-height: 1.8;
    scrollbar-width: thin;
  `,
  entry: css`
    display: flex;
    gap: 8px;
    white-space: pre-wrap;
    word-break: break-all;
  `,
}));

const LogPanel = () => {
  const { styles } = useStyles();
  const entries = useLogStore((s) => s.entries);
  const isStreaming = useLogStore((s) => s.isStreaming);
  const autoScroll = useLogStore((s) => s.autoScroll);
  const clearLogs = useLogStore((s) => s.clearLogs);
  const setAutoScroll = useLogStore((s) => s.setAutoScroll);

  // 连接 SSE
  useSSELog();

  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (autoScroll) {
      bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [entries, autoScroll]);

  return (
    <div className={styles.panel}>
      <div className={styles.toolbar}>
        <span className={isStreaming ? styles.dot : styles.dotOff} />
        <span style={{ flex: 1 }}>
          运行日志 {isStreaming ? "（已连接）" : "（未连接）"}
        </span>
        <Tooltip title={autoScroll ? "关闭自动滚动" : "开启自动滚动"}>
          <Button
            size="small"
            type="text"
            icon={autoScroll ? <DownOutlined /> : <PauseOutlined />}
            onClick={() => setAutoScroll(!autoScroll)}
          />
        </Tooltip>
        <Tooltip title="清空日志">
          <Button
            size="small"
            type="text"
            icon={<ClearOutlined />}
            onClick={clearLogs}
          />
        </Tooltip>
      </div>
      <div className={styles.log}>
        {entries.map((e) => (
          <div key={e.id} className={styles.entry}>
            <span style={{ color: "#8c8c8c", flexShrink: 0 }}>
              {e.timestamp}
            </span>
            <span
              style={{
                color: LEVEL_COLORS[e.level],
                flexShrink: 0,
                minWidth: 52,
              }}
            >
              {e.level}
            </span>
            <span>{e.message}</span>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
    </div>
  );
};

export default LogPanel;
