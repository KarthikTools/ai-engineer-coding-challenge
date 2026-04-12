/**
 * TypeScript type definitions matching the backend Pydantic models.
 */

export interface ExecutionStep {
  step_number: number;
  description: string;
  timestamp: string;
}

export type TaskStatus = "pending" | "completed" | "failed";

export interface TaskResult {
  id: string;
  input: string;
  status: TaskStatus;
  output: string | null;
  tool_used: string | null;
  execution_steps: ExecutionStep[];
  created_at: string;
  completed_at: string | null;
  error: string | null;
}

export interface TaskRequest {
  input: string;
}

export interface ToolInfo {
  name: string;
  description: string;
}
