/**
 * TaskHistory — displays the list of all past tasks.
 *
 * Features:
 *  - Reverse chronological order (newest first)
 *  - Empty state messaging
 *  - Export button
 */

import type { TaskResult } from "../types";
import TaskResultCard from "./TaskResultCard";

interface TaskHistoryProps {
  tasks: TaskResult[];
  onExport: () => void;
}

export default function TaskHistory({ tasks, onExport }: TaskHistoryProps) {
  return (
    <div className="task-history">
      <div className="history-header">
        <h3>📋 Task History ({tasks.length})</h3>
        {tasks.length > 0 && (
          <button className="export-btn" onClick={onExport}>
            ⬇ Export JSON
          </button>
        )}
      </div>

      {tasks.length === 0 ? (
        <div className="empty-state">
          <p>No tasks yet. Submit one above to get started!</p>
        </div>
      ) : (
        <div className="task-list">
          {tasks.map((task, index) => (
            <TaskResultCard
              key={task.id}
              task={task}
              isLatest={index === 0}
            />
          ))}
        </div>
      )}
    </div>
  );
}
