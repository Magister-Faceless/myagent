# src/app/components/ChatInterface/ChatInterface.tsx

import { Send, Bot, LoaderCircle, SquarePen, History, X } from "lucide-react";
import { ChatMessage } from "../ChatMessage/ChatMessage";
import { ThreadHistorySidebar } from "../ThreadHistorySidebar/ThreadHistorySidebar";
import type { SubAgent, TodoItem, ToolCall } from "../../types/types";
import type { SubAgent, TodoItem, ToolCall, Agent } from "../../types/types";
import { useChat } from "../../hooks/useChat";
import styles from "./ChatInterface.module.scss";
import { Message } from "@langchain/langgraph-sdk";
import { extractStringFromMessageContent } from "../../utils/utils";

interface ChatInterfaceProps {
  agent: Agent;
  threadId: string | null;
  selectedSubAgent: SubAgent | null;
  setThreadId: (
    value: string | ((old: string | null) => string | null) | null,
    value: string | ((old: string | null) => string | null) | null
  ) => void;
  onSelectSubAgent: (subAgent: SubAgent) => void;
  onTodosUpdate: (todos: TodoItem[]) => void;
@@ -34,6 +35,7 @@ interface ChatInterfaceProps {

export const ChatInterface = React.memo<ChatInterfaceProps>(
  ({
    agent,
    threadId,
    selectedSubAgent,
    setThreadId,
@@ -48,10 +50,11 @@ export const ChatInterface = React.memo<ChatInterfaceProps>(
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const { messages, isLoading, sendMessage, stopStream } = useChat(
      agent,
      threadId,
      setThreadId,
      onTodosUpdate,
      onFilesUpdate,
      onFilesUpdate
    );

    useEffect(() => {
@@ -66,7 +69,7 @@ export const ChatInterface = React.memo<ChatInterfaceProps>(
        sendMessage(messageText);
        setInput("");
      },
      [input, isLoading, sendMessage],
      [input, isLoading, sendMessage]
    );

    const handleNewThread = useCallback(() => {
@@ -83,7 +86,7 @@ export const ChatInterface = React.memo<ChatInterfaceProps>(
        setThreadId(id);
        setIsThreadHistoryOpen(false);
      },
      [setThreadId],
      [setThreadId]
    );

    const toggleThreadHistory = useCallback(() => {
@@ -110,12 +113,12 @@ export const ChatInterface = React.memo<ChatInterfaceProps>(
          } else if (message.tool_calls && Array.isArray(message.tool_calls)) {
            toolCallsInMessage.push(
              ...message.tool_calls.filter(
                (toolCall: any) => toolCall.name !== "",
              ),
                (toolCall: any) => toolCall.name !== ""
              )
            );
          } else if (Array.isArray(message.content)) {
            const toolUseBlocks = message.content.filter(
              (block: any) => block.type === "tool_use",
              (block: any) => block.type === "tool_use"
            );
            toolCallsInMessage.push(...toolUseBlocks);
          }
@@ -137,7 +140,7 @@ export const ChatInterface = React.memo<ChatInterfaceProps>(
                args,
                status: "pending" as const,
              } as ToolCall;
            },
            }
          );
          messageMap.set(message.id!, {
            message,
@@ -150,7 +153,7 @@ export const ChatInterface = React.memo<ChatInterfaceProps>(
          }
          for (const [, data] of messageMap.entries()) {
            const toolCallIndex = data.toolCalls.findIndex(
              (tc: any) => tc.id === toolCallId,
              (tc: any) => tc.id === toolCallId
            );
            if (toolCallIndex === -1) {
              continue;
@@ -186,7 +189,7 @@ export const ChatInterface = React.memo<ChatInterfaceProps>(
        <div className={styles.header}>
          <div className={styles.headerLeft}>
            <Bot className={styles.logo} />
            <h1 className={styles.title}>Deep Agents</h1>
            <h1 className={styles.title}>{agent.name}</h1>
          </div>
          <div className={styles.headerRight}>
            <Button
@@ -204,6 +207,7 @@ export const ChatInterface = React.memo<ChatInterfaceProps>(
        </div>
        <div className={styles.content}>
          <ThreadHistorySidebar
            agent={agent}
            open={isThreadHistoryOpen}
            setOpen={setIsThreadHistoryOpen}
            currentThreadId={threadId}
@@ -270,7 +274,7 @@ export const ChatInterface = React.memo<ChatInterfaceProps>(
        </form>
      </div>
    );
  },
  }
);

ChatInterface.displayName = "ChatInterface";