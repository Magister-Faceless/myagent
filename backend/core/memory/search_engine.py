"""
Memory Search Engine for MyAgents

Intelligent memory retrieval system that understands user queries and 
provides contextual search across thread memories.
"""

import json
import sqlite3
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

from models import get_default_model
from core.database.enhanced_schema import get_enhanced_db_manager


@dataclass
class MemorySearchQuery:
    """Structured search query for memory retrieval"""
    query_text: str
    intent: str
    entity_filters: List[str]
    category_filters: List[str]
    time_range: Optional[str] = None
    min_importance: float = 0.0
    search_strategy: List[str] = None
    expected_result_types: List[str] = None
    
    def __post_init__(self):
        if self.search_strategy is None:
            self.search_strategy = ["keyword_search"]
        if self.expected_result_types is None:
            self.expected_result_types = ["any"]


class MyAgentsSearchEngine:
    """
    Memory search engine for intelligent retrieval of thread memories
    Adapted from Memori's search capabilities for our enhanced system
    """
    
    SYSTEM_PROMPT = """You are a Memory Search Agent for MyAgents, responsible for understanding user queries and planning effective memory retrieval strategies.

Your primary functions:
1. **Analyze Query Intent**: Understand what the user is actually looking for
2. **Extract Search Parameters**: Identify key entities, topics, and concepts
3. **Plan Search Strategy**: Recommend the best approach to find relevant memories
4. **Filter Recommendations**: Suggest appropriate filters for category, importance, etc.

**MEMORY CATEGORIES AVAILABLE:**
- **essential**: Core facts, important preferences, key skills, critical project info
- **contextual**: Current work context, ongoing projects, environmental setup
- **conversational**: Regular discussions, explanations, problem-solving conversations
- **reference**: Code examples, documentation, learning materials
- **personal**: Life events, relationships, personal interests
- **conscious_info**: User details, preferences, skills, current projects

**SEARCH STRATEGIES:**
- **keyword_search**: Direct keyword/phrase matching in content
- **entity_search**: Search by specific entities (people, technologies, topics)
- **category_filter**: Filter by memory categories
- **importance_filter**: Filter by importance levels
- **temporal_filter**: Search within specific time ranges
- **semantic_search**: Conceptual/meaning-based search

**QUERY INTERPRETATION GUIDELINES:**
- "What did I learn about X?" → Focus on essential and contextual related to X
- "My preferences for Y" → Focus on conscious_info and personal categories
- "Rules about Z" → Focus on essential category
- "Recent work on A" → Temporal filter + contextual/essential categories
- "Important information about B" → Importance filter + keyword search

Be strategic and comprehensive in your search planning."""

    def __init__(self):
        """Initialize the search engine"""
        self.model = get_default_model()
        self.db_manager = get_enhanced_db_manager()
        
    def search_memories(
        self,
        query: str,
        thread_id: str,
        limit: int = 10,
        agent_name: str = "unknown"
    ) -> List[Dict[str, Any]]:
        """
        Execute intelligent memory search
        
        Args:
            query: User's search query
            thread_id: Thread to search within
            limit: Maximum results to return
            agent_name: Agent making the search
            
        Returns:
            List of relevant memories with search metadata
        """
        try:
            # Plan the search strategy
            search_plan = self._plan_search(query, thread_id)
            
            print(f"🔍 Search plan for '{query}': {search_plan.intent}")
            
            # Execute multi-strategy search
            all_results = []
            seen_memory_ids = set()
            
            # 1. Primary full-text search
            primary_results = self._execute_fulltext_search(
                search_plan, thread_id, limit
            )
            
            for result in primary_results:
                if result.get("memory_id") not in seen_memory_ids:
                    seen_memory_ids.add(result["memory_id"])
                    result["search_strategy"] = "fulltext_search"
                    result["search_reasoning"] = "Full-text search match"
                    all_results.append(result)
            
            # 2. Entity-based search if we have room
            if len(all_results) < limit and search_plan.entity_filters:
                entity_results = self._execute_entity_search(
                    search_plan, thread_id, limit - len(all_results)
                )
                
                for result in entity_results:
                    if result.get("memory_id") not in seen_memory_ids:
                        seen_memory_ids.add(result["memory_id"])
                        result["search_strategy"] = "entity_search"
                        result["search_reasoning"] = f"Entity match: {', '.join(search_plan.entity_filters)}"
                        all_results.append(result)
            
            # 3. Category-based search if we have room
            if len(all_results) < limit and search_plan.category_filters:
                category_results = self._execute_category_search(
                    search_plan, thread_id, limit - len(all_results)
                )
                
                for result in category_results:
                    if result.get("memory_id") not in seen_memory_ids:
                        seen_memory_ids.add(result["memory_id"])
                        result["search_strategy"] = "category_search"
                        result["search_reasoning"] = f"Category match: {', '.join(search_plan.category_filters)}"
                        all_results.append(result)
            
            # Sort by relevance and importance
            all_results = self._rank_results(all_results, search_plan)
            
            # Add search metadata
            for result in all_results:
                result["search_metadata"] = {
                    "original_query": query,
                    "interpreted_intent": search_plan.intent,
                    "search_timestamp": datetime.now().isoformat(),
                    "searched_by_agent": agent_name
                }
            
            print(f"✅ Found {len(all_results)} memories for query: '{query}'")
            return all_results[:limit]
            
        except Exception as e:
            print(f"❌ Memory search failed: {e}")
            return []
    
    def _plan_search(self, query: str, thread_id: str) -> MemorySearchQuery:
        """Plan search strategy using AI"""
        
        prompt = f"""Analyze this search query and create a search plan:

Query: "{query}"
Thread ID: {thread_id}

Return a JSON object with this structure:
{{
    "query_text": "Original query text",
    "intent": "Interpreted intent of the query",
    "entity_filters": ["specific entities to search for"],
    "category_filters": ["memory categories: essential, contextual, conversational, reference, personal, conscious_info"],
    "time_range": "time range or null",
    "min_importance": 0.0,
    "search_strategy": ["recommended search strategies"],
    "expected_result_types": ["expected types of results"]
}}

Respond with ONLY the JSON object."""
        
        try:
            response = self.model.invoke([
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ])
            
            # Extract and parse JSON
            response_text = response.content if hasattr(response, 'content') else str(response)
            response_text = self._clean_json_response(response_text)
            
            data = json.loads(response_text)
            
            return MemorySearchQuery(
                query_text=data.get("query_text", query),
                intent=data.get("intent", "General search"),
                entity_filters=data.get("entity_filters", []),
                category_filters=data.get("category_filters", []),
                time_range=data.get("time_range"),
                min_importance=float(data.get("min_importance", 0.0)),
                search_strategy=data.get("search_strategy", ["keyword_search"]),
                expected_result_types=data.get("expected_result_types", ["any"])
            )
            
        except Exception as e:
            print(f"⚠️ Search planning failed, using fallback: {e}")
            return MemorySearchQuery(
                query_text=query,
                intent="General search (fallback)",
                entity_filters=[word for word in query.split() if len(word) > 2],
                category_filters=[],
                search_strategy=["keyword_search"]
            )
    
    def _execute_fulltext_search(
        self, search_plan: MemorySearchQuery, thread_id: str, limit: int
    ) -> List[Dict]:
        """Execute full-text search using SQLite FTS5"""
        
        # Use the database manager's search method
        results = self.db_manager.search_memories(
            query=search_plan.query_text,
            namespace=thread_id,
            limit=limit
        )
        
        return results
    
    def _execute_entity_search(
        self, search_plan: MemorySearchQuery, thread_id: str, limit: int
    ) -> List[Dict]:
        """Execute entity-based search"""
        
        if not search_plan.entity_filters:
            return []
        
        # Search for entities in the entities JSON field
        entity_query = " OR ".join(search_plan.entity_filters)
        
        with sqlite3.connect(self.db_manager.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Search in entities and keywords JSON fields
            cursor = conn.execute("""
                SELECT *, confidence_score as importance_score
                FROM memories 
                WHERE thread_id = ? 
                AND (
                    entities LIKE ? OR 
                    keywords LIKE ? OR
                    content LIKE ?
                )
                ORDER BY importance DESC, created_at DESC
                LIMIT ?
            """, (
                thread_id,
                f"%{entity_query}%",
                f"%{entity_query}%", 
                f"%{entity_query}%",
                limit
            ))
            
            results = []
            for row in cursor.fetchall():
                result = dict(row)
                result['memory_id'] = result['id']
                results.append(result)
            
            return results
    
    def _execute_category_search(
        self, search_plan: MemorySearchQuery, thread_id: str, limit: int
    ) -> List[Dict]:
        """Execute category-based search"""
        
        if not search_plan.category_filters:
            return []
        
        with sqlite3.connect(self.db_manager.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Create placeholders for categories
            placeholders = ",".join("?" * len(search_plan.category_filters))
            
            cursor = conn.execute(f"""
                SELECT *, confidence_score as importance_score
                FROM memories 
                WHERE thread_id = ? AND classification IN ({placeholders})
                ORDER BY importance DESC, created_at DESC
                LIMIT ?
            """, [thread_id] + search_plan.category_filters + [limit])
            
            results = []
            for row in cursor.fetchall():
                result = dict(row)
                result['memory_id'] = result['id']
                results.append(result)
            
            return results
    
    def _rank_results(
        self, results: List[Dict], search_plan: MemorySearchQuery
    ) -> List[Dict]:
        """Rank search results by relevance and importance"""
        
        def calculate_score(result):
            # Base importance score
            importance_map = {"critical": 1.0, "high": 0.8, "medium": 0.6, "low": 0.4}
            importance_score = importance_map.get(result.get("importance", "medium"), 0.6)
            
            # Confidence score
            confidence_score = result.get("confidence_score", 0.7)
            
            # Recency score (newer is better)
            created_at = result.get("created_at", "")
            try:
                created_date = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                days_old = (datetime.now() - created_date.replace(tzinfo=None)).days
                recency_score = max(0, 1.0 - (days_old / 365))  # Decay over a year
            except:
                recency_score = 0.5
            
            # Combined score
            return (importance_score * 0.4) + (confidence_score * 0.4) + (recency_score * 0.2)
        
        # Sort by calculated score
        results.sort(key=calculate_score, reverse=True)
        return results
    
    def _clean_json_response(self, response_text: str) -> str:
        """Clean JSON response from AI model"""
        response_text = response_text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        return response_text.strip()


def get_search_engine() -> MyAgentsSearchEngine:
    """Get the search engine instance"""
    return MyAgentsSearchEngine()


# Export for easy import
__all__ = ["MyAgentsSearchEngine", "MemorySearchQuery", "get_search_engine"]
