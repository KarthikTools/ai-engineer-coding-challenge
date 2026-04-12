/**
 * ToolList — displays available tools the agent can use.
 */

import { useEffect, useState } from "react";
import type { ToolInfo } from "../types";
import { fetchTools } from "../api";

function getToolIcon(name: string): string {
  switch (name) {
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

export default function ToolList() {
  const [tools, setTools] = useState<ToolInfo[]>([]);

  useEffect(() => {
    fetchTools().then(setTools).catch(console.error);
  }, []);

  if (tools.length === 0) return null;

  return (
    <div className="tool-list">
      <h4>Available Tools</h4>
      <div className="tool-chips">
        {tools.map((tool) => (
          <div key={tool.name} className="tool-chip">
            <span className="tool-icon">{getToolIcon(tool.name)}</span>
            <div>
              <strong>{tool.name}</strong>
              <small>{tool.description}</small>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
