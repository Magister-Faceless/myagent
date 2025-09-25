"use client";

import React, { useState, useCallback, useEffect, useMemo } from "react";
import { useQueryState } from "nuqs";
import { ChatInterface } from "./components/ChatInterface/ChatInterface";
import { TasksFilesSidebar } from "./components/TasksFilesSidebar/TasksFilesSidebar";
import { SubAgentPanel } from "./components/SubAgentPanel/SubAgentPanel";
import { FileViewDialog } from "./components/FileViewDialog/FileViewDialog";
import { AgentSelector } from "./components/AgentSelector/AgentSelector";
import { createClientForAgent } from "@/lib/client";
import { useAuthContext } from "@/providers/Auth";
import { AVAILABLE_AGENTS, getDefaultAgent } from "@/lib/agents/config";
import type {
  SubAgent,
  FileItem,
  TodoItem,
  Agent,
  AgentContext,
} from "./types/types";
import styles from "./page.module.scss";

export default function HomePage() {
  const { session } = useAuthContext();
  const [threadId, setThreadId] = useQueryState("threadId");
  const [currentAgent, setCurrentAgent] = useState<Agent>(getDefaultAgent());
  const [selectedFile, setSelectedFile] = useState<FileItem | null>(null);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [isLoadingThreadState, setIsLoadingThreadState] = useState(false);

  const [agentContexts, setAgentContexts] = useState<
    Record<string, AgentContext>
  >({});

  const currentContext = useMemo(() => {
    return (
      agentContexts[currentAgent.id] || {
        agent: currentAgent,
        threadId: null,
        todos: [],
        files: {},
        selectedSubAgent: null,
      }
    );
  }, [agentContexts, currentAgent.id, currentAgent]);

  const toggleSidebar = useCallback(() => {
    setSidebarCollapsed((prev) => !prev);
  }, []);

  // When the threadId changes, grab the thread state from the graph server
  useEffect(() => {
    const fetchThreadState = async () => {
      if (!threadId || !session?.accessToken) {
        setTodos([]);
        setFiles({});
        setIsLoadingThreadState(false);
        return;
      }
      setIsLoadingThreadState(true);
      try {
        const client = createClientForAgent(session.accessToken, currentAgent.id);
        const state = await client.threads.getState(threadId);

        if (state.values) {
          const currentState = state.values as {
            todos?: TodoItem[];
            files?: Record<string, string>;
          };
          setTodos(currentState.todos || []);
          setFiles(currentState.files || {});
        }
      } catch (error) {
        console.error("Failed to fetch thread state:", error);
        setTodos([]);
        setFiles({});
      } finally {
        setIsLoadingThreadState(false);
      }
    };
    fetchThreadState();
  }, [threadId, session?.accessToken]);

  const handleNewThread = useCallback(() => {
    setThreadId(null);
    setSelectedSubAgent(null);
    setTodos([]);
    setFiles({});
  }, [setThreadId]);

  return (
    <div className={styles.container}>
      <TasksFilesSidebar
        todos={todos}
        files={files}
        onFileClick={setSelectedFile}
        collapsed={sidebarCollapsed}
        onToggleCollapse={toggleSidebar}
      />
      <div className={styles.mainContent}>
        <ChatInterface
          threadId={threadId}
          selectedSubAgent={selectedSubAgent}
          setThreadId={setThreadId}
          onSelectSubAgent={setSelectedSubAgent}
          onTodosUpdate={setTodos}
          onFilesUpdate={setFiles}
          onNewThread={handleNewThread}
          isLoadingThreadState={isLoadingThreadState}
        />
        {selectedSubAgent && (
          <SubAgentPanel
            subAgent={selectedSubAgent}
            onClose={() => setSelectedSubAgent(null)}
          />
        )}
      </div>
      {selectedFile && (
        <FileViewDialog
          file={selectedFile}
          onClose={() => setSelectedFile(null)}
        />
      )}
    </div>
  );
}
