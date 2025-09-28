"""
Memory Agent Integration for MyAgents

This module integrates the Memori memory agent with our enhanced database system
to provide intelligent conversation processing and memory management.
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum

from models import get_default_model
from core.database.enhanced_schema import get_enhanced_db_manager


class MemoryClassification(str, Enum):
    """Memory classification types based on Memori"""
    ESSENTIAL = "essential"
    CONTEXTUAL = "contextual" 
    CONVERSATIONAL = "conversational"
    REFERENCE = "reference"
    PERSONAL = "personal"
    CONSCIOUS_INFO = "conscious_info"


class MemoryImportanceLevel(str, Enum):
    """Memory importance levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ProcessedMemory:
    """Processed memory structure"""
    id: str
    thread_id: str
    conversation_id: str
    content: str
    summary: str
    classification: MemoryClassification
    importance: MemoryImportanceLevel
    topic: Optional[str] = None
    entities: List[str] = None
    keywords: List[str] = None
    is_user_context: bool = False
    is_preference: bool = False
    is_skill_knowledge: bool = False
    is_current_project: bool = False
    confidence_score: float = 0.7
    promotion_eligible: bool = False
    created_by_agent: str = "unknown"
    created_at: datetime = None
    
    def __post_init__(self):
        if self.entities is None:
            self.entities = []
        if self.keywords is None:
            self.keywords = []
        if self.created_at is None:
            self.created_at = datetime.now()


class MyAgentsMemoryAgent:
    """
    Memory Agent for MyAgents - processes conversations and extracts structured memories
    Adapted from Memori's MemoryAgent for our enhanced database system
    """
    
    SYSTEM_PROMPT = """You are an advanced Memory Processing Agent for MyAgents, responsible for analyzing conversations and extracting structured information.

Your primary functions:
1. **Intelligent Classification**: Categorize memories with enhanced classification system
2. **Context Detection**: Identify user context information for immediate promotion
3. **Entity Extraction**: Extract comprehensive entities and keywords
4. **Deduplication**: Identify and handle duplicate information
5. **Context Filtering**: Determine what should be stored vs filtered out

**CLASSIFICATION SYSTEM:**

**CONSCIOUS_INFO** (Auto-promote to short-term context):
- User's name, location, job, personal details
- Current projects, technologies they work with
- Preferences, work style, communication style
- Skills, expertise, learning goals

**ESSENTIAL**:
- Core facts that define user's context
- Important preferences and opinions
- Key skills and knowledge areas
- Critical project information

**CONTEXTUAL**:
- Current work context
- Ongoing projects and goals
- Environmental setup and tools

**CONVERSATIONAL**:
- Regular discussions and questions
- Explanations and clarifications
- Problem-solving conversations

**REFERENCE**:
- Code examples and technical references
- Documentation and resources
- Learning materials

**PERSONAL**:
- Life events and personal information
- Relationships and social context
- Personal interests and hobbies

**IMPORTANCE LEVELS:**
- **CRITICAL**: Must never be lost
- **HIGH**: Very important for context
- **MEDIUM**: Useful to remember
- **LOW**: Nice to have context

**PROCESSING RULES:**
1. AVOID DUPLICATES: Check if similar information already exists
2. MERGE SIMILAR: Combine related information when appropriate
3. FILTER UNNECESSARY: Skip trivial greetings, acknowledgments
4. EXTRACT ENTITIES: Identify people, places, technologies, projects
5. ASSESS IMPORTANCE: Rate based on relevance to user context
6. FLAG USER CONTEXT: Mark information for conscious promotion

Focus on extracting information that would genuinely help provide better context and assistance in future conversations."""

    def __init__(self):
        """Initialize the memory agent"""
        self.model = get_default_model()
        self.db_manager = get_enhanced_db_manager()
        
    def process_conversation(
        self,
        thread_id: str,
        user_input: str,
        ai_output: str,
        agent_name: str = "unknown",
        conversation_id: str = None
    ) -> ProcessedMemory:
        """
        Process a conversation and extract structured memory
        
        Args:
            thread_id: Thread/project ID
            user_input: User's input message
            ai_output: AI's response
            agent_name: Name of the agent processing
            conversation_id: Optional conversation ID
            
        Returns:
            Processed memory object
        """
        try:
            if conversation_id is None:
                conversation_id = str(uuid.uuid4())
            
            # Prepare conversation content
            conversation_text = f"User: {user_input}\nAssistant: {ai_output}"
            
            # Get existing memories for deduplication
            existing_memories = self._get_recent_memories(thread_id, limit=10)
            
            # Process with AI model
            processed_memory = self._extract_memory_with_ai(
                conversation_text=conversation_text,
                thread_id=thread_id,
                conversation_id=conversation_id,
                agent_name=agent_name,
                existing_memories=existing_memories
            )
            
            # Store in database
            self._store_memory(processed_memory)
            
            print(f"✅ Memory processed for thread {thread_id}: {processed_memory.classification}")
            return processed_memory
            
        except Exception as e:
            print(f"❌ Memory processing failed: {e}")
            # Return a basic memory for error cases
            return self._create_fallback_memory(
                thread_id=thread_id,
                conversation_id=conversation_id or str(uuid.uuid4()),
                content=f"User: {user_input}\nAssistant: {ai_output}",
                agent_name=agent_name
            )
    
    def _extract_memory_with_ai(
        self,
        conversation_text: str,
        thread_id: str,
        conversation_id: str,
        agent_name: str,
        existing_memories: List[Dict]
    ) -> ProcessedMemory:
        """Extract memory using AI model"""
        
        # Build context for deduplication
        dedup_context = ""
        if existing_memories:
            dedup_context = "\n\nEXISTING MEMORIES (for deduplication):\n"
            dedup_context += "\n".join([
                f"- {mem.get('summary', mem.get('content', ''))[:100]}..."
                for mem in existing_memories[:5]
            ])
        
        # Create prompt
        prompt = f"""Process this conversation for memory storage:

{conversation_text}

Thread ID: {thread_id}
Agent: {agent_name}
{dedup_context}

Extract and return a JSON object with the following structure:
{{
    "content": "The actual memory content",
    "summary": "Concise summary for search",
    "classification": "One of: essential, contextual, conversational, reference, personal, conscious_info",
    "importance": "One of: critical, high, medium, low",
    "topic": "Main topic/subject or null",
    "entities": ["array of people, places, technologies mentioned"],
    "keywords": ["array of key terms for search"],
    "is_user_context": boolean,
    "is_preference": boolean,
    "is_skill_knowledge": boolean,
    "is_current_project": boolean,
    "confidence_score": number between 0.0 and 1.0,
    "promotion_eligible": boolean
}}

Respond with ONLY the JSON object."""
        
        try:
            # Use the model to process
            response = self.model.invoke([
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ])
            
            # Extract JSON from response
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            # Clean up response
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            # Parse JSON
            data = json.loads(response_text)
            
            # Create ProcessedMemory object
            return ProcessedMemory(
                id=str(uuid.uuid4()),
                thread_id=thread_id,
                conversation_id=conversation_id,
                content=data.get("content", "No content extracted"),
                summary=data.get("summary", "No summary available"),
                classification=MemoryClassification(data.get("classification", "conversational")),
                importance=MemoryImportanceLevel(data.get("importance", "medium")),
                topic=data.get("topic"),
                entities=data.get("entities", []),
                keywords=data.get("keywords", []),
                is_user_context=bool(data.get("is_user_context", False)),
                is_preference=bool(data.get("is_preference", False)),
                is_skill_knowledge=bool(data.get("is_skill_knowledge", False)),
                is_current_project=bool(data.get("is_current_project", False)),
                confidence_score=float(data.get("confidence_score", 0.7)),
                promotion_eligible=bool(data.get("promotion_eligible", False)),
                created_by_agent=agent_name
            )
            
        except Exception as e:
            print(f"⚠️ AI memory extraction failed: {e}")
            return self._create_fallback_memory(
                thread_id=thread_id,
                conversation_id=conversation_id,
                content=conversation_text,
                agent_name=agent_name
            )
    
    def _create_fallback_memory(
        self,
        thread_id: str,
        conversation_id: str,
        content: str,
        agent_name: str
    ) -> ProcessedMemory:
        """Create a fallback memory for error cases"""
        return ProcessedMemory(
            id=str(uuid.uuid4()),
            thread_id=thread_id,
            conversation_id=conversation_id,
            content=content,
            summary="Conversation recorded (fallback)",
            classification=MemoryClassification.CONVERSATIONAL,
            importance=MemoryImportanceLevel.MEDIUM,
            confidence_score=0.5,
            created_by_agent=agent_name
        )
    
    def _get_recent_memories(self, thread_id: str, limit: int = 10) -> List[Dict]:
        """Get recent memories for deduplication"""
        try:
            return self.db_manager.search_memories(
                query="",  # Empty query to get recent memories
                namespace=thread_id,
                limit=limit
            )
        except Exception as e:
            print(f"⚠️ Failed to get recent memories: {e}")
            return []
    
    def _store_memory(self, memory: ProcessedMemory):
        """Store processed memory in database"""
        import sqlite3
        
        with sqlite3.connect(self.db_manager.db_path) as conn:
            conn.execute("""
                INSERT INTO memories (
                    id, thread_id, conversation_id, content, summary,
                    classification, importance, topic, entities, keywords,
                    is_user_context, is_preference, is_skill_knowledge, is_current_project,
                    confidence_score, promotion_eligible, created_by_agent
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                memory.id,
                memory.thread_id,
                memory.conversation_id,
                memory.content,
                memory.summary,
                memory.classification.value,
                memory.importance.value,
                memory.topic,
                json.dumps(memory.entities),
                json.dumps(memory.keywords),
                memory.is_user_context,
                memory.is_preference,
                memory.is_skill_knowledge,
                memory.is_current_project,
                memory.confidence_score,
                memory.promotion_eligible,
                memory.created_by_agent
            ))
            conn.commit()


def get_memory_agent() -> MyAgentsMemoryAgent:
    """Get the memory agent instance"""
    return MyAgentsMemoryAgent()


# Export for easy import
__all__ = ["MyAgentsMemoryAgent", "ProcessedMemory", "MemoryClassification", "MemoryImportanceLevel", "get_memory_agent"]
