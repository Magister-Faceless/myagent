# src/app/hooks/useChat.ts

@@ -1,36 +1,36 @@
import { useCallback, useMemo } from "react";
import { v4 as uuidv4 } from "uuid";
import { useStream } from "@langchain/langgraph-sdk/react";
import { type Message } from "@langchain/langgraph-sdk";
import { getDeployment } from "@/lib/environment/deployments";
import { v4 as uuidv4 } from "uuid";
import type { TodoItem } from "../types/types";
import { createClient } from "@/lib/client";
import { createClientForAgent } from "@/lib/client";
import { useAuthContext } from "@/providers/Auth";

import type { TodoItem, Agent } from "../types/types";

type StateType = {
  messages: Message[];
  todos: TodoItem[];
  files: Record<string, string>;
};

export function useChat(
  agent: Agent,
  threadId: string | null,
  setThreadId: (
    value: string | ((old: string | null) => string | null) | null,
    value: string | ((old: string | null) => string | null) | null
  ) => void,
  onTodosUpdate: (todos: TodoItem[]) => void,
  onFilesUpdate: (files: Record<string, string>) => void,
  onFilesUpdate: (files: Record<string, string>) => void
) {
  const deployment = useMemo(() => getDeployment(), []);
  const { session } = useAuthContext();
  const accessToken = session?.accessToken;

  const agentId = useMemo(() => {
    if (!deployment?.agentId) {
      throw new Error(`No agent ID configured in environment`);
    if (!agent?.id) {
      throw new Error(`No agent ID provided`);
    }
    return deployment.agentId;
  }, [deployment]);
    return agent.id;
  }, [agent]);

  const handleUpdateEvent = useCallback(
    (data: { [node: string]: Partial<StateType> }) => {
@@ -43,12 +43,12 @@ export function useChat(
        }
      });
    },
    [onTodosUpdate, onFilesUpdate],
    [onTodosUpdate, onFilesUpdate]
  );

  const stream = useStream<StateType>({
    assistantId: agentId,
    client: createClient(accessToken || ""),
    client: createClientForAgent(accessToken || "", agentId),
    reconnectOnMount: true,
    threadId: threadId ?? null,
    onUpdateEvent: handleUpdateEvent,
@@ -76,10 +76,10 @@ export function useChat(
          config: {
            recursion_limit: 100,
          },
        },
        }
      );
    },
    [stream],
    [stream]
  );

  const stopStream = useCallback(() => {
