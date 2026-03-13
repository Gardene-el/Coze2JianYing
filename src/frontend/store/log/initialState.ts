export interface LogEntry {
  id: number;
  timestamp: string;
  level: "DEBUG" | "INFO" | "WARNING" | "ERROR" | "CRITICAL";
  message: string;
  raw: string;
}

export interface LogState {
  entries: LogEntry[];
  isStreaming: boolean;
  autoScroll: boolean;
}

export const initialLogState: LogState = {
  entries: [],
  isStreaming: false,
  autoScroll: true,
};
