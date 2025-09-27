import type { Agent } from "@/app/types/types";

// Default agents configuration
// You can modify this list to add/remove agents as needed
export const AVAILABLE_AGENTS: Agent[] = [
  {
    id: "main-agent",
    name: "Main Agent",
    description: "General purpose AI agent for complex tasks",
    color: "#3B82F6",
    icon: "🧠",
  },
  {
    id: "research-agent",
    name: "Research Agent",
    description: "Specialized agent for research and data analysis",
    color: "#8B5CF6",
    icon: "🔬",
  },
  {
    id: "code-assistant",
    name: "Code Assistant",
    description: "Specialized agent for coding and development tasks",
    color: "#10B981",
    icon: "💻",
  },
  {
    id: "content-creator",
    name: "Content Creator",
    description: "Agent for writing and content creation tasks",
    color: "#F59E0B",
    icon: "✍️",
  },
  {
    id: "literature-review",
    name: "Literature Review Agent",
    description:
      "Systematic literature review assistant with planning, screening, and synthesis subagents",
    color: "#6366F1",
    icon: "📚",
  },
];

export function getAgentById(id: string): Agent | undefined {
  return AVAILABLE_AGENTS.find((agent) => agent.id === id);
}

export function getDefaultAgent(): Agent {
  return AVAILABLE_AGENTS[0];
}
