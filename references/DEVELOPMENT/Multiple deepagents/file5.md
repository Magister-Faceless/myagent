# src/app/components/ThreadHistorySidebar/ThreadHistorySidebar.tsx

"use client";

import React, { useEffect, useState, useCallback, useMemo } from "react";
import { MessageSquare, X } from "lucide-react";

import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import { MessageSquare, X } from "lucide-react";
import { createClient } from "@/lib/client";
import { createClientForAgent } from "@/lib/client";
import { useAuthContext } from "@/providers/Auth";
import { getDeployment } from "@/lib/environment/deployments";
import type { Thread } from "../../types/types";
import type { Thread, Agent } from "../../types/types";
import styles from "./ThreadHistorySidebar.module.scss";
import { extractStringFromMessageContent } from "../../utils/utils";

interface ThreadHistorySidebarProps {
  agent: Agent;
  open: boolean;
  setOpen: (open: boolean) => void;
  currentThreadId: string | null;
  onThreadSelect: (threadId: string) => void;
}

export const ThreadHistorySidebar = React.memo<ThreadHistorySidebarProps>(
  ({ open, setOpen, currentThreadId, onThreadSelect }) => {
  ({ agent, open, setOpen, currentThreadId, onThreadSelect }) => {
    const [threads, setThreads] = useState<Thread[]>([]);
    const [isLoadingThreadHistory, setIsLoadingThreadHistory] = useState(true);
    const { session } = useAuthContext();
    const deployment = useMemo(() => getDeployment(), []);

    const fetchThreads = useCallback(async () => {
      if (!deployment?.deploymentUrl || !session?.accessToken) return;
      if (!agent?.id || !session?.accessToken) return;
      setIsLoadingThreadHistory(true);
      try {
        const client = createClient(session.accessToken);
        const client = createClientForAgent(session.accessToken, agent.id);
        const response = await client.threads.search({
          limit: 30,
          sortBy: "created_at",
@@ -51,7 +51,7 @@ export const ThreadHistorySidebar = React.memo<ThreadHistorySidebarProps>(
          } catch (error) {
            console.warn(
              `Failed to get first message for thread ${thread.thread_id}:`,
              error,
              error
            );
          }
          return {
@@ -63,19 +63,24 @@ export const ThreadHistorySidebar = React.memo<ThreadHistorySidebarProps>(
        });
        setThreads(
          threadList.sort(
            (a, b) => b.updatedAt.getTime() - a.updatedAt.getTime(),
          ),
            (a, b) => b.updatedAt.getTime() - a.updatedAt.getTime()
          )
        );
      } catch (error) {
        console.error("Failed to fetch threads:", error);
      } finally {
        setIsLoadingThreadHistory(false);
      }
    }, [deployment?.deploymentUrl, session?.accessToken]);
    }, [agent?.id, session?.accessToken]);

    useEffect(() => {
      fetchThreads();
    }, [fetchThreads, currentThreadId]);
    }, [fetchThreads, currentThreadId, agent.id]);

    // Clear threads when agent changes for immediate feedback
    useEffect(() => {
      setThreads([]);
    }, [agent.id]);

    const groupedThreads = useMemo(() => {
      const groups: Record<string, Thread[]> = {
@@ -182,7 +187,7 @@ export const ThreadHistorySidebar = React.memo<ThreadHistorySidebarProps>(
        </div>
      </div>
    );
  },
  }
);

const ThreadItem = React.memo<{S