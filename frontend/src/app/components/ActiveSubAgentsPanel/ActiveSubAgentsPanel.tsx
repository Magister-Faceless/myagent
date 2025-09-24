"use client";

import React, { useState, useEffect } from "react";
import { Bot, CheckCircle, AlertCircle, Loader, ChevronDown, ChevronRight, Activity } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";

interface ActiveSubAgent {
  id: string;
  name: string;
  description: string;
  status: "active" | "completed" | "error";
  created_at: string;
  progress?: number;
}

interface SubAgentEvent {
  type: "subagent_started" | "subagent_completed" | "subagent_error";
  timestamp: string;
  data: ActiveSubAgent;
}

export const ActiveSubAgentsPanel: React.FC = () => {
  const [subAgents, setSubAgents] = useState<ActiveSubAgent[]>([]);
  const [isExpanded, setIsExpanded] = useState(true);

  useEffect(() => {
    // Listen for subagent events from system messages
    const handleMessage = (event: MessageEvent) => {
      try {
        // Look for subagent events in system messages
        if (event.data && typeof event.data === 'string') {
          const content = event.data;
          
          // Parse subagent events from system messages
          if (content.includes('**Event Data**:')) {
            const eventDataMatch = content.match(/\*\*Event Data\*\*:\s*({[\s\S]*?})/);
            if (eventDataMatch) {
              const eventData: SubAgentEvent = JSON.parse(eventDataMatch[1]);
              handleSubAgentEvent(eventData);
            }
          }
        }
      } catch (error) {
        console.warn('Failed to parse subagent event:', error);
      }
    };

    // Also listen for custom events
    const handleCustomEvent = (event: CustomEvent<SubAgentEvent>) => {
      handleSubAgentEvent(event.detail);
    };

    const handleSubAgentEvent = (eventData: SubAgentEvent) => {
      const { type, data } = eventData;
      
      setSubAgents(prev => {
        const existing = prev.find(agent => agent.id === data.id);
        
        if (type === 'subagent_started') {
          if (existing) {
            // Update existing
            return prev.map(agent => 
              agent.id === data.id 
                ? { ...agent, ...data, status: 'active' as const }
                : agent
            );
          } else {
            // Add new
            return [...prev, { ...data, status: 'active' as const }];
          }
        }
        
        if (type === 'subagent_completed') {
          return prev.map(agent => 
            agent.id === data.id 
              ? { ...agent, status: 'completed' as const, progress: 100 }
              : agent
          );
        }
        
        if (type === 'subagent_error') {
          return prev.map(agent => 
            agent.id === data.id 
              ? { ...agent, status: 'error' as const }
              : agent
          );
        }
        
        return prev;
      });
    };

    // Listen for messages and custom events
    window.addEventListener('message', handleMessage);
    window.addEventListener('subagent_event', handleCustomEvent as EventListener);

    return () => {
      window.removeEventListener('message', handleMessage);
      window.removeEventListener('subagent_event', handleCustomEvent as EventListener);
    };
  }, []);

  // Auto-remove completed/error subagents after 30 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      setSubAgents(prev => 
        prev.filter(agent => {
          if (agent.status === 'active') return true;
          
          const completedTime = new Date(agent.created_at).getTime();
          const now = Date.now();
          const thirtySecondsAgo = now - 30000;
          
          return completedTime > thirtySecondsAgo;
        })
      );
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const activeSubAgents = subAgents.filter(agent => agent.status === 'active');
  const recentSubAgents = subAgents.filter(agent => agent.status !== 'active');

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="text-green-500" size={16} />;
      case 'error':
        return <AlertCircle className="text-red-500" size={16} />;
      case 'active':
        return <Loader className="text-blue-500 animate-spin" size={16} />;
      default:
        return <Activity className="text-yellow-500" size={16} />;
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed':
        return 'Completed';
      case 'error':
        return 'Error';
      case 'active':
        return 'Running';
      default:
        return 'Pending';
    }
  };

  const formatTime = (timestamp: string) => {
    try {
      return new Date(timestamp).toLocaleTimeString();
    } catch {
      return timestamp;
    }
  };

  if (subAgents.length === 0) {
    return null;
  }

  return (
    <div className="border border-border rounded-lg bg-card text-card-foreground shadow-sm mb-4">
      <Button
        variant="ghost"
        size="sm"
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full justify-start p-3 hover:bg-accent/50 transition-colors"
      >
        <div className="flex items-center gap-2">
          {isExpanded ? (
            <ChevronDown size={14} />
          ) : (
            <ChevronRight size={14} />
          )}
          <Activity size={14} className="text-muted-foreground" />
          <span className="text-sm font-medium">
            SubAgents ({activeSubAgents.length} active, {recentSubAgents.length} recent)
          </span>
        </div>
      </Button>

      {isExpanded && (
        <div className="px-3 pb-3">
          {/* Active SubAgents */}
          {activeSubAgents.length > 0 && (
            <div className="mb-4 last:mb-0">
              <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">Active</h4>
              <div className="space-y-2">
                {activeSubAgents.map((agent) => (
                  <div key={agent.id} className="p-3 rounded-md border transition-all duration-200 border-blue-200 bg-blue-50/50 dark:border-blue-800 dark:bg-blue-950/30">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <Bot size={14} className="text-muted-foreground" />
                        <span className="text-sm font-medium">{agent.name}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        {getStatusIcon(agent.status)}
                        <span className="text-xs text-muted-foreground">{getStatusText(agent.status)}</span>
                      </div>
                    </div>
                    <div className="text-xs text-muted-foreground mb-2 line-clamp-2">
                      {agent.description}
                    </div>
                    <div className="flex items-center justify-between text-xs text-muted-foreground">
                      <span className="text-xs text-muted-foreground">Started: {formatTime(agent.created_at)}</span>
                    </div>
                    {agent.progress !== undefined && (
                      <Progress value={agent.progress} className="mt-2 h-1" />
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recent SubAgents */}
          {recentSubAgents.length > 0 && (
            <div className="mb-4 last:mb-0">
              <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">Recent</h4>
              <div className="space-y-2">
                {recentSubAgents.slice(-5).map((agent) => (
                  <div key={agent.id} className={cn(
                    "p-3 rounded-md border transition-all duration-200",
                    {
                      "border-green-200 bg-green-50/50 dark:border-green-800 dark:bg-green-950/30": agent.status === 'completed',
                      "border-red-200 bg-red-50/50 dark:border-red-800 dark:bg-red-950/30": agent.status === 'error'
                    }
                  )}>
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <Bot size={14} className="text-muted-foreground" />
                        <span className="text-sm font-medium">{agent.name}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        {getStatusIcon(agent.status)}
                        <span className="text-xs text-muted-foreground">{getStatusText(agent.status)}</span>
                      </div>
                    </div>
                    <div className="text-xs text-muted-foreground mb-2 line-clamp-2">
                      {agent.description}
                    </div>
                    <div className="flex items-center justify-between text-xs text-muted-foreground">
                      <span className="text-xs text-muted-foreground">Started: {formatTime(agent.created_at)}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

ActiveSubAgentsPanel.displayName = "ActiveSubAgentsPanel";
