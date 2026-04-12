/**
 * TaskInput — form component for submitting a new task.
 *
 * Features:
 *  - Text input with placeholder examples
 *  - Submit button with loading state
 *  - Quick-action buttons for common tasks
 */

import { useState } from "react";

interface TaskInputProps {
  onSubmit: (input: string) => Promise<void>;
  isLoading: boolean;
}

const EXAMPLE_TASKS = [
  'Convert "hello world" to uppercase',
  "Calculate 42 * 17",
  "What's the weather in Tokyo?",
  "Word count of 'the quick brown fox jumps'",
  "Reverse 'engineering'",
  "15 + 27 - 8",
];

export default function TaskInput({ onSubmit, isLoading }: TaskInputProps) {
  const [input, setInput] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    await onSubmit(input.trim());
    setInput("");
  };

  const handleQuickAction = async (example: string) => {
    if (isLoading) return;
    setInput(example);
    await onSubmit(example);
  };

  return (
    <div className="task-input-container">
      <form onSubmit={handleSubmit} className="task-form">
        <div className="input-row">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder='Try: "Convert hello to uppercase" or "Calculate 3 + 5"'
            disabled={isLoading}
            className="task-input"
            autoFocus
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="submit-btn"
          >
            {isLoading ? (
              <span className="spinner" />
            ) : (
              "Submit Task"
            )}
          </button>
        </div>
      </form>

      <div className="quick-actions">
        <span className="quick-label">Try:</span>
        {EXAMPLE_TASKS.map((example) => (
          <button
            key={example}
            className="quick-btn"
            onClick={() => handleQuickAction(example)}
            disabled={isLoading}
            title={example}
          >
            {example.length > 30 ? example.slice(0, 28) + "…" : example}
          </button>
        ))}
      </div>
    </div>
  );
}
