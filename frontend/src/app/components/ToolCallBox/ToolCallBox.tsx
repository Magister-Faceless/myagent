"use client";

import React, { useState, useMemo, useCallback } from "react";
import {
  ChevronDown,
  ChevronRight,
  Terminal,
  CheckCircle,
  AlertCircle,
  Loader,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { ReferencesDisplay } from "../ReferencesDisplay/ReferencesDisplay";
import styles from "./ToolCallBox.module.scss";
import { ToolCall } from "../../types/types";

interface ToolCallBoxProps {
  toolCall: ToolCall;
}

export const ToolCallBox = React.memo<ToolCallBoxProps>(({ toolCall }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const { name, args, result, status, references } = useMemo(() => {
    const toolName = toolCall.name || "Unknown Tool";
    const toolArgs = toolCall.args || "{}";
    let parsedArgs = {};
    try {
      parsedArgs =
        typeof toolArgs === "string" ? JSON.parse(toolArgs) : toolArgs;
    } catch {
      parsedArgs = { raw: toolArgs };
    }
    const toolResult = toolCall.result || null;
    const toolStatus = toolCall.status || "completed";
    
    // Extract references from the result if available
    let extractedReferences = [];
    if (toolResult) {
      try {
        const parsedResult = typeof toolResult === "string" ? JSON.parse(toolResult) : toolResult;
        if (parsedResult && parsedResult.references && Array.isArray(parsedResult.references)) {
          extractedReferences = parsedResult.references;
        }
      } catch {
        // If parsing fails, no references
      }
    }

    return {
      name: toolName,
      args: parsedArgs,
      result: toolResult,
      status: toolStatus,
      references: extractedReferences,
    };
  }, [toolCall]);

  const statusIcon = useMemo(() => {
    switch (status) {
      case "completed":
        return <CheckCircle className={styles.statusCompleted} />;
      case "error":
        return <AlertCircle className={styles.statusError} />;
      case "pending":
        return <Loader className={styles.statusRunning} />;
      default:
        return <Terminal className={styles.statusDefault} />;
    }
  }, [status]);

  const toggleExpanded = useCallback(() => {
    setIsExpanded((prev) => !prev);
  }, []);

  const hasContent = result || Object.keys(args).length > 0;

  return (
    <div className={styles.container}>
      <Button
        variant="ghost"
        size="sm"
        onClick={toggleExpanded}
        className={styles.header}
        disabled={!hasContent}
      >
        <div className={styles.headerLeft}>
          {hasContent && isExpanded ? (
            <ChevronDown size={14} />
          ) : (
            <ChevronRight size={14} />
          )}
          {statusIcon}
          <span className={styles.toolName}>{name}</span>
        </div>
      </Button>

      {isExpanded && hasContent && (
        <div className={styles.content}>
          {Object.keys(args).length > 0 && (
            <div className={styles.section}>
              <h4 className={styles.sectionTitle}>Arguments</h4>
              <pre className={styles.codeBlock}>
                {JSON.stringify(args, null, 2)}
              </pre>
            </div>
          )}
          {result && (
            <div className={styles.section}>
              <h4 className={styles.sectionTitle}>Result</h4>
              <pre className={styles.codeBlock}>
                {typeof result === "string"
                  ? result
                  : JSON.stringify(result, null, 2)}
              </pre>
            </div>
          )}
          {references && references.length > 0 && (
            <div className={styles.section}>
              <ReferencesDisplay references={references} title="Sources" />
            </div>
          )}
        </div>
      )}
    </div>
  );
});

ToolCallBox.displayName = "ToolCallBox";
