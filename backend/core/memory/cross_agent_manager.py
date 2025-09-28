"""
Cross-Agent Memory Manager for MyAgents

This module manages memory sharing and collaboration between different agents
within the same thread, enabling seamless knowledge transfer and context sharing.
"""

import json
import sqlite3
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from core.database.enhanced_schema import get_enhanced_db_manager
from core.memory.search_engine import get_search_engine


class CrossAgentMemoryManager:
    """Manager for cross-agent memory sharing and collaboration tracking"""
    
    def __init__(self, thread_id: str):
        """Initialize cross-agent memory manager for a specific thread"""
        self.thread_id = thread_id
        self.db_manager = get_enhanced_db_manager()
        self.search_engine = get_search_engine()
        
        # Ensure thread exists
        self._ensure_thread_exists()
    
    def _ensure_thread_exists(self):
        """Ensure thread exists in database"""
        try:
            existing_thread = self.db_manager.get_thread(self.thread_id)
            if not existing_thread:
                self.db_manager.create_thread(self.thread_id)
        except Exception as e:
            print(f"⚠️ Failed to ensure thread exists: {e}")
    
    def get_thread_context(
        self,
        requesting_agent: str,
        context_type: str = "comprehensive",
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Get comprehensive thread context for any agent
        
        Args:
            requesting_agent: Agent requesting the context
            context_type: Type of context ('comprehensive', 'recent', 'important', 'files')
            limit: Maximum number of items to return
            
        Returns:
            Dictionary containing thread context information
        """
        try:
            # Record the context request
            self.record_agent_interaction(
                source_agent=requesting_agent,
                interaction_type="context_request",
                context={"context_type": context_type, "limit": limit}
            )
            
            context = {
                "thread_id": self.thread_id,
                "requesting_agent": requesting_agent,
                "context_type": context_type,
                "timestamp": datetime.now().isoformat()
            }
            
            if context_type in ["comprehensive", "recent"]:
                # Get recent memories
                context["recent_memories"] = self._get_recent_memories(limit)
                
            if context_type in ["comprehensive", "important"]:
                # Get important memories
                context["important_memories"] = self._get_important_memories(limit)
                
            if context_type in ["comprehensive", "files"]:
                # Get recent files
                context["recent_files"] = self._get_recent_files(limit)
                
            if context_type == "comprehensive":
                # Get agent interactions
                context["agent_interactions"] = self._get_agent_interactions(limit)
                
                # Get thread metadata
                context["thread_info"] = self.db_manager.get_thread(self.thread_id)
                
                # Get context summary
                context["context_summary"] = self._generate_context_summary(context)
            
            # Update thread access
            self.db_manager.update_thread_access(self.thread_id, requesting_agent)
            
            return context
            
        except Exception as e:
            print(f"❌ Failed to get thread context: {e}")
            return {
                "thread_id": self.thread_id,
                "requesting_agent": requesting_agent,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def search_thread_memory(
        self,
        query: str,
        requesting_agent: str,
        search_type: str = "general",
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search thread memory with agent context tracking
        
        Args:
            query: Search query
            requesting_agent: Agent making the search
            search_type: Type of search ('general', 'files', 'decisions', 'context')
            limit: Maximum results to return
            
        Returns:
            List of relevant memories with search metadata
        """
        try:
            # Record the search interaction
            self.record_agent_interaction(
                source_agent=requesting_agent,
                interaction_type="memory_search",
                context={
                    "query": query,
                    "search_type": search_type,
                    "limit": limit
                }
            )
            
            # Execute search based on type
            if search_type == "files":
                # Search for file-related memories
                enhanced_query = f"files documents uploads generated: {query}"
            elif search_type == "decisions":
                # Search for decision-related memories
                enhanced_query = f"decisions choices conclusions determined: {query}"
            elif search_type == "context":
                # Search for contextual information
                enhanced_query = f"context background information about: {query}"
            else:
                enhanced_query = query
            
            # Use search engine
            results = self.search_engine.search_memories(
                query=enhanced_query,
                thread_id=self.thread_id,
                limit=limit,
                agent_name=requesting_agent
            )
            
            # Add cross-agent context to results
            for result in results:
                result["searched_by_agent"] = requesting_agent
                result["search_type"] = search_type
                result["cross_agent_accessible"] = True
            
            return results
            
        except Exception as e:
            print(f"❌ Memory search failed: {e}")
            return []
    
    def record_agent_interaction(
        self,
        source_agent: str,
        interaction_type: str,
        target_agent: Optional[str] = None,
        context: Optional[Dict] = None,
        result: Optional[Dict] = None
    ):
        """
        Record agent interactions for collaboration tracking
        
        Args:
            source_agent: Agent initiating the interaction
            interaction_type: Type of interaction
            target_agent: Target agent (if applicable)
            context: Interaction context data
            result: Interaction result data
        """
        try:
            interaction_id = str(uuid.uuid4())
            
            with sqlite3.connect(self.db_manager.db_path) as conn:
                conn.execute("""
                    INSERT INTO agent_interactions (
                        id, thread_id, source_agent, target_agent,
                        interaction_type, context, result
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    interaction_id,
                    self.thread_id,
                    source_agent,
                    target_agent,
                    interaction_type,
                    json.dumps(context or {}),
                    json.dumps(result or {})
                ))
                conn.commit()
                
        except Exception as e:
            print(f"⚠️ Failed to record agent interaction: {e}")
    
    def get_shared_context_summary(self, requesting_agent: str) -> str:
        """
        Generate a text summary of shared context for an agent
        
        Args:
            requesting_agent: Agent requesting the summary
            
        Returns:
            Text summary of thread context
        """
        try:
            # Get comprehensive context
            context = self.get_thread_context(requesting_agent, "comprehensive", 10)
            
            summary_parts = []
            
            # Thread info
            thread_info = context.get("thread_info", {})
            if thread_info:
                summary_parts.append(f"Thread: {thread_info.get('name', 'Unnamed')} (ID: {self.thread_id})")
                if thread_info.get('description'):
                    summary_parts.append(f"Description: {thread_info['description']}")
                summary_parts.append(f"Last active agent: {thread_info.get('last_active_agent', 'Unknown')}")
            
            # Recent important memories
            important_memories = context.get("important_memories", [])
            if important_memories:
                summary_parts.append("\nKey Information:")
                for memory in important_memories[:5]:
                    summary_parts.append(f"- {memory.get('summary', memory.get('content', '')[:100])}...")
            
            # Recent files
            recent_files = context.get("recent_files", [])
            if recent_files:
                summary_parts.append(f"\nRecent Files ({len(recent_files)}):")
                for file_info in recent_files[:3]:
                    summary_parts.append(f"- {file_info.get('filename', 'Unknown')} ({file_info.get('file_type', 'unknown')})")
            
            return "\n".join(summary_parts) if summary_parts else "No shared context available."
            
        except Exception as e:
            print(f"❌ Failed to generate context summary: {e}")
            return f"Error generating context summary: {str(e)}"
    
    def _get_recent_memories(self, limit: int) -> List[Dict]:
        """Get recent memories from the thread"""
        try:
            with sqlite3.connect(self.db_manager.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT * FROM memories
                    WHERE thread_id = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (self.thread_id, limit))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            print(f"⚠️ Failed to get recent memories: {e}")
            return []
    
    def _get_important_memories(self, limit: int) -> List[Dict]:
        """Get important memories from the thread"""
        try:
            with sqlite3.connect(self.db_manager.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT * FROM memories
                    WHERE thread_id = ? AND importance IN ('critical', 'high')
                    ORDER BY 
                        CASE importance 
                            WHEN 'critical' THEN 1 
                            WHEN 'high' THEN 2 
                            ELSE 3 
                        END,
                        created_at DESC
                    LIMIT ?
                """, (self.thread_id, limit))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            print(f"⚠️ Failed to get important memories: {e}")
            return []
    
    def _get_recent_files(self, limit: int) -> List[Dict]:
        """Get recent files from the thread"""
        try:
            with sqlite3.connect(self.db_manager.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT id, filename, file_type, size_bytes, created_by_agent, created_at
                    FROM files
                    WHERE thread_id = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (self.thread_id, limit))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            print(f"⚠️ Failed to get recent files: {e}")
            return []
    
    def _get_agent_interactions(self, limit: int) -> List[Dict]:
        """Get recent agent interactions"""
        try:
            with sqlite3.connect(self.db_manager.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT source_agent, target_agent, interaction_type, created_at
                    FROM agent_interactions
                    WHERE thread_id = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (self.thread_id, limit))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            print(f"⚠️ Failed to get agent interactions: {e}")
            return []
    
    def _generate_context_summary(self, context: Dict) -> str:
        """Generate a brief context summary"""
        try:
            summary_parts = []
            
            # Memory count
            recent_count = len(context.get("recent_memories", []))
            important_count = len(context.get("important_memories", []))
            if recent_count or important_count:
                summary_parts.append(f"Memories: {recent_count} recent, {important_count} important")
            
            # File count
            file_count = len(context.get("recent_files", []))
            if file_count:
                summary_parts.append(f"Files: {file_count} recent")
            
            # Interaction count
            interaction_count = len(context.get("agent_interactions", []))
            if interaction_count:
                summary_parts.append(f"Interactions: {interaction_count} recent")
            
            return ", ".join(summary_parts) if summary_parts else "No activity"
            
        except Exception as e:
            print(f"⚠️ Failed to generate context summary: {e}")
            return "Summary generation failed"


def get_cross_agent_manager(thread_id: str) -> CrossAgentMemoryManager:
    """Get cross-agent memory manager for a thread"""
    return CrossAgentMemoryManager(thread_id)


# Export for easy import
__all__ = ["CrossAgentMemoryManager", "get_cross_agent_manager"]
