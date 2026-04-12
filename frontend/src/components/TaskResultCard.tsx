/**
 * TaskResultCard — displays the result of a single processed task.
 *
 * Shows: input, output, tool used, status badge, timestamp,
 * and an expandable execution trace.
 */

import { useState } from "react";
import type { TaskResult } from "../types";
import ExecutionTrace from "./ExecutionTrace";

interface TaskResultCardProps {
  task: TaskResult;
  isLatest?: boolean;
}

function formatTime(isoString: string): string {
  return new Date(isoString).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

function getStatusBadge(status: string): { label: string; className: string } {
  switch (status) {
    case "completed":
      return { label: "✅ Completed", className: "badge-success" };
    case "failed":
      return { label: "❌ Failed", className: "badge-error" };
    default:
      return { label: "⏳ Pending", className: "badge-pending" };
  }
}

function getToolIcon(toolName: string | null): string {
  switch (toolName) {
    case "TextProcessorTool":
      return "📝";
    case "CalculatorTool":
      return "🔢";
    case "WeatherMockTool":
      return "🌤️";
    default:
      return "🛠️";
  }
}

export default function TaskResultCard({ task, isLatest = false }: TaskResultCardProps) {
  const [showTrace, setShowTrace] = useState(isLatest);
  const badge = getStatusBadge(task.status);

  return (
    <div className={`task-card ${isLatest ? "task-card-latest" : ""}`}>
      <div className="task-card-header">
        <div className="task-card-meta">
          <span className={`status-badge ${badge.className}`}>{badge.label}</span>
          {task.tool_used && (
            <span className="tool-badge">
              {getToolIcon(task.tool_used)} {task.tool_used}
            </span>
          )}
          <span className="task-time">{formatTime(task.created_at)}</span>
        </div>
      </div>

      <div className="task-card-body">
        <div className="task-field">
          <label>Input:</label>
          <p className="task-input-display">{task.input}</p>
        </div>

        {task.output && (
          <div className="task-field">
            <label>Output:</label>
            <pre className="task-output">{task.output}</pre>
          </div>
        )}

        {task.error && (
          <div className="task-field">
            <label>Error:</label>
            <p className="task-error">{task.error}</p>
          </div>
        )}
      </div>

      {task.execution_steps.length > 0 && (
        <div className="task-card-footer">
          <button
            className="trace-toggle"
            onClick={() => setShowTrace(!showTrace)}
          >
            {showTrace ? "▼ Hide" : "▶ Show"} Execution Trace ({task.execution_steps.length} steps)
          </button>
          {showTrace && <ExecutionTrace steps={task.execution_steps} />}
        </div>
      )}
    </div>
  );
}
