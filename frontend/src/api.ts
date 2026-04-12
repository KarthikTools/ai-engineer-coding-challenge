/**
 * API service layer — all backend communication in one place.
 *
 * Single responsibility: HTTP calls to the FastAPI backend.
 * Components never call fetch() directly.
 */

import type { TaskResult, TaskRequest, ToolInfo } from "./types";

const API_BASE = "http://localhost:8000/api";

class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${url}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new ApiError(
      response.status,
      body.detail || `Request failed with status ${response.status}`
    );
  }

  return response.json();
}

/** Submit a new task for the agent to process. */
export async function createTask(input: string): Promise<TaskResult> {
  const body: TaskRequest = { input };
  return request<TaskResult>("/tasks", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

/** Fetch all past tasks (most recent first). */
export async function fetchTasks(): Promise<TaskResult[]> {
  return request<TaskResult[]>("/tasks");
}

/** Fetch a single task by ID. */
export async function fetchTask(id: string): Promise<TaskResult> {
  return request<TaskResult>(`/tasks/${id}`);
}

/** List all available tools. */
export async function fetchTools(): Promise<ToolInfo[]> {
  return request<ToolInfo[]>("/tools");
}

/** Export all tasks as JSON. */
export async function exportTasks(): Promise<{ data: string; count: number }> {
  return request<{ data: string; count: number }>("/tasks/export");
}
