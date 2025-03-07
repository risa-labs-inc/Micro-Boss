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
  CODE = "code",
  RESULT = "result"
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
}

// Available models
export interface AvailableModels {
  [provider: string]: string[];
} 