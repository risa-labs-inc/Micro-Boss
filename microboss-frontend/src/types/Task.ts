// Task status enum
export enum TaskStatus {
  PENDING = "pending",
  RUNNING = "running",
  COMPLETED = "completed",
  FAILED = "failed"
}

// Event level enum
export enum EventLevel {
  INFO = "info",
  SUCCESS = "success",
  WARNING = "warning",
  ERROR = "error",
  DEBUG = "debug",
  TASK = "task",
  CODE = "code",
  RESULT = "result",
  EXECUTION = "execution"
}

// Event type
export interface Event {
  id: string;
  timestamp: number;
  formatted_time: string;
  level: string;
  message: string;
  task_id: string;
  type: string;
  data?: any;
  depth?: number;
  subtask_id?: string;
  parent_id?: string;
}

// Available models
export interface AvailableModels {
  [provider: string]: string[];
} 