/**
 * ExecutionTrace — displays the agent's step-by-step reasoning.
 *
 * Each step is shown as a timeline entry with step number and description.
 * This is a key differentiator — it makes the agent's "thinking" transparent.
 */

import type { ExecutionStep } from "../types";

interface ExecutionTraceProps {
  steps: ExecutionStep[];
}

export default function ExecutionTrace({ steps }: ExecutionTraceProps) {
  if (steps.length === 0) return null;

  return (
    <div className="execution-trace">
      <h4 className="trace-title">🔍 Execution Trace</h4>
      <div className="trace-timeline">
        {steps.map((step) => (
          <div key={step.step_number} className="trace-step">
            <div className="step-marker">
              <span className="step-number">{step.step_number}</span>
              <div className="step-line" />
            </div>
            <div className="step-content">
              <p className="step-description">{step.description}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
