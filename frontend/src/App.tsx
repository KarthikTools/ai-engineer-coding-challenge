/**
 * App — root component for the Task Agent frontend.
 *
 * Layout:
 *  - Header with app title
 *  - Tool list showing available tools
 *  - Task input form
 *  - Task history with execution traces
 */

import { useState, useEffect, useCallback } from "react";
import type { TaskResult } from "./types";
import { createTask, fetchTasks, exportTasks } from "./api";
import TaskInput from "./components/TaskInput";
import TaskHistory from "./components/TaskHistory";
import ToolList from "./components/ToolList";
import "./App.css";

export default function App() {
  const [tasks, setTasks] = useState<TaskResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load existing tasks on mount
  useEffect(() => {
    fetchTasks()
      .then(setTasks)
      .catch(() => setError("Could not connect to backend. Is it running on port 8000?"));
  }, []);

  const handleSubmit = useCallback(async (input: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await createTask(input);
      setTasks((prev) => [result, ...prev]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An unexpected error occurred");
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleExport = useCallback(async () => {
    try {
      const result = await exportTasks();
      const blob = new Blob([result.data], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `task-export-${new Date().toISOString().slice(0, 10)}.json`;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      setError("Failed to export tasks");
    }
  }, []);

  return (
    <div className="app">
      <header className="app-header">
        <h1>🤖 Task Agent</h1>
        <p className="subtitle">
          Submit a task and watch the AI agent select the right tool and execute it
        </p>
      </header>

      <main className="app-main">
        <ToolList />
        <TaskInput onSubmit={handleSubmit} isLoading={isLoading} />

        {error && (
          <div className="error-banner">
            <span>⚠️ {error}</span>
            <button onClick={() => setError(null)}>✕</button>
          </div>
        )}

        <TaskHistory tasks={tasks} onExport={handleExport} />
      </main>

      <footer className="app-footer">
        <p>Built for the AI Engineer Coding Challenge • FastAPI + React + TypeScript</p>
      </footer>
    </div>
  );
}
