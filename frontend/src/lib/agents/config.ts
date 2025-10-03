import type { Agent } from "@/app/types/types";

// Default agents configuration
// Matches ALL agents defined in backend/langgraph.json
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
    id: "medical-literature-agent",
    name: "Medical Literature Agent",
    description: "Specialized agent for medical literature search, filtering, review, and analysis",
    color: "#DC2626",
    icon: "🏥",
  },
  {
    id: "python-coding-agent",
    name: "Python Coding Assistant",
    description: "Specialized Python development assistant for coding, debugging, and best practices",
    color: "#3776AB",
    icon: "🐍",
  },
  {
    id: "enhanced-main-agent",
    name: "Enhanced Main Agent",
    description: "Memory-enhanced general purpose AI agent with intelligent context management",
    color: "#7C3AED",
    icon: "🧠✨",
  },
  {
    id: "literature-review",
    name: "Literature Review Agent",
    description: "Systematic literature review coordinator with human-in-the-loop workflow and citation verification",
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
