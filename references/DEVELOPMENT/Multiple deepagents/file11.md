# src/app/types/types.ts

@@ -34,3 +34,18 @@ export interface Thread {
  createdAt: Date;
  updatedAt: Date;
}

export interface Agent {
  id: string;
  name: string;
  description?: string;
  color?: string;
}

export interface AgentContext {
  agent: Agent;
  threadId: string | null;
  todos: TodoItem[];
  files: Record<string, string>;
  selectedSubAgent: SubAgent | null;
}