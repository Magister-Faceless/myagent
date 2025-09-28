# MyAgents Desktop App - Enhanced Local Storage with AI Memory System

## Executive Summary

This enhanced plan integrates the **Memori AI memory system** with our local SQLite-based architecture to create a powerful desktop app that provides:

1. **Intelligent Memory Management**: AI-powered conversation processing and retrieval
2. **Thread-Centric Architecture**: Threads as unified project containers
3. **Cross-Agent Memory Sharing**: All agents access shared memory within threads
4. **Local-Only Storage**: Everything stays on user's machine
5. **File Management**: Upload, modify, and version control files
6. **Pure SQLite Solution**: No hybrid approach needed - SQLite handles everything efficiently

## Key Insights from Memori Integration

### Memory System Benefits
- **Intelligent Classification**: Automatically categorizes memories (facts, preferences, skills, context, rules)
- **Smart Retrieval**: AI-powered search that understands intent and context
- **Cross-Agent Sharing**: Multiple agents can access and build upon shared memories
- **Deduplication**: Prevents redundant memory storage
- **Importance Scoring**: Prioritizes critical information

### SQLite Optimization
- **Proven at Scale**: Memori successfully uses SQLite for memory storage
- **Full-Text Search**: SQLite's FTS5 provides excellent search capabilities
- **JSON Support**: Modern SQLite handles JSON data efficiently
- **ACID Compliance**: Ensures data integrity across agent operations

## Enhanced Database Architecture

### Core Tables (SQLite)

```sql
-- Threads table (enhanced from existing checkpointer)
CREATE TABLE IF NOT EXISTS threads (
    id TEXT PRIMARY KEY,                    -- Thread ID (existing LangGraph)
    name TEXT,                             -- User-friendly project name
    description TEXT,                      -- Project description
    created_by_agent TEXT,                 -- Original agent
    last_active_agent TEXT,                -- Most recent agent
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT,                         -- JSON metadata
    status TEXT DEFAULT 'active'           -- active, archived, deleted
);

-- Enhanced memory system (based on Memori)
CREATE TABLE IF NOT EXISTS memories (
    id TEXT PRIMARY KEY,                   -- Memory UUID
    thread_id TEXT NOT NULL,               -- Links to thread
    conversation_id TEXT,                  -- Specific conversation within thread
    content TEXT NOT NULL,                 -- Memory content
    summary TEXT,                          -- Searchable summary
    classification TEXT NOT NULL,          -- essential, contextual, conversational, reference, personal, conscious_info
    importance TEXT NOT NULL,              -- critical, high, medium, low
    topic TEXT,                           -- Main topic/subject
    entities TEXT,                        -- JSON array of entities
    keywords TEXT,                        -- JSON array of keywords
    is_user_context BOOLEAN DEFAULT FALSE, -- Contains user personal info
    is_preference BOOLEAN DEFAULT FALSE,   -- User preference/opinion
    is_skill_knowledge BOOLEAN DEFAULT FALSE, -- User's abilities/expertise
    is_current_project BOOLEAN DEFAULT FALSE, -- Current work context
    confidence_score REAL DEFAULT 0.7,    -- AI confidence (0.0-1.0)
    promotion_eligible BOOLEAN DEFAULT FALSE, -- Should be promoted to short-term
    created_by_agent TEXT,                -- Which agent created it
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (thread_id) REFERENCES threads(id) ON DELETE CASCADE
);

-- Full-text search index for memories
CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(
    content, summary, topic, entities, keywords,
    content='memories', content_rowid='rowid'
);

-- Files table (enhanced for better integration)
CREATE TABLE IF NOT EXISTS files (
    id TEXT PRIMARY KEY,                   -- File UUID
    thread_id TEXT NOT NULL,               -- Links to thread
    memory_id TEXT,                        -- Optional link to memory
    filename TEXT NOT NULL,                -- Original filename
    file_path TEXT,                        -- Relative path for filesystem storage
    storage_type TEXT NOT NULL,            -- 'blob' or 'filesystem'
    file_type TEXT NOT NULL,               -- 'upload', 'generated', 'export'
    mime_type TEXT,                        -- MIME type
    size_bytes INTEGER NOT NULL,           -- File size
    hash_sha256 TEXT,                      -- Content hash
    content BLOB,                          -- File content (if storage_type='blob')
    created_by_agent TEXT,                 -- Which agent created it
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT,                         -- JSON metadata
    FOREIGN KEY (thread_id) REFERENCES threads(id) ON DELETE CASCADE,
    FOREIGN KEY (memory_id) REFERENCES memories(id) ON DELETE SET NULL
);

-- File versions for change tracking
CREATE TABLE IF NOT EXISTS file_versions (
    id TEXT PRIMARY KEY,                   -- Version UUID
    file_id TEXT NOT NULL,                 -- References files.id
    version_number INTEGER NOT NULL,       -- Sequential version
    content BLOB,                          -- Version content
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,                       -- 'user' or agent name
    change_description TEXT,               -- What changed
    FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE,
    UNIQUE(file_id, version_number)
);

-- Agent interactions (track cross-agent collaboration)
CREATE TABLE IF NOT EXISTS agent_interactions (
    id TEXT PRIMARY KEY,
    thread_id TEXT NOT NULL,
    source_agent TEXT NOT NULL,            -- Agent making the request
    target_agent TEXT,                     -- Agent being invoked (NULL for tools)
    interaction_type TEXT NOT NULL,        -- 'memory_search', 'file_access', 'tool_call', 'subagent_spawn'
    context TEXT,                          -- JSON context data
    result TEXT,                           -- JSON result data
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (thread_id) REFERENCES threads(id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_memories_thread ON memories(thread_id);
CREATE INDEX IF NOT EXISTS idx_memories_classification ON memories(classification);
CREATE INDEX IF NOT EXISTS idx_memories_importance ON memories(importance);
CREATE INDEX IF NOT EXISTS idx_memories_created_at ON memories(created_at);
CREATE INDEX IF NOT EXISTS idx_files_thread ON files(thread_id);
CREATE INDEX IF NOT EXISTS idx_files_type ON files(file_type);
CREATE INDEX IF NOT EXISTS idx_agent_interactions_thread ON agent_interactions(thread_id);
```

## Memory-Enhanced File Management

### Intelligent File Storage Strategy

```python
class EnhancedThreadFileManager:
    def __init__(self, thread_id: str):
        self.thread_id = thread_id
        self.db_path = get_enhanced_db_path()
        self.memory_agent = MemoryAgent()
        self.search_engine = MemorySearchEngine()
        
    def store_file_with_memory(
        self, 
        content: Union[str, bytes], 
        filename: str,
        file_type: str = "upload",
        agent_name: str = "user"
    ) -> Dict[str, str]:
        """Store file and create associated memory"""
        
        # Determine storage strategy based on size and type
        size = len(content) if isinstance(content, (str, bytes)) else 0
        storage_type = "blob" if size < 10 * 1024 * 1024 else "filesystem"  # 10MB threshold
        
        # Store file
        file_id = self._store_file(content, filename, file_type, storage_type, agent_name)
        
        # Create memory entry for the file
        memory_content = f"File uploaded: {filename} ({file_type})"
        if isinstance(content, str) and len(content) < 1000:
            memory_content += f"\nContent preview: {content[:500]}..."
            
        memory_id = self._create_file_memory(
            file_id=file_id,
            filename=filename,
            content_preview=memory_content,
            agent_name=agent_name
        )
        
        # Link file to memory
        self._link_file_to_memory(file_id, memory_id)
        
        return {
            "file_id": file_id,
            "memory_id": memory_id,
            "storage_type": storage_type
        }
        
    def search_files_by_content(self, query: str) -> List[Dict]:
        """Search files using AI-powered memory search"""
        
        # Use memory search to find relevant files
        search_plan = self.search_engine.plan_search(
            query=f"files related to: {query}",
            context=f"thread_id: {self.thread_id}"
        )
        
        # Execute search across memories and files
        results = self._execute_file_search(search_plan)
        
        return results
```

## Cross-Agent Memory Integration

### Enhanced Agent Memory Access

```python
class CrossAgentMemoryManager:
    def __init__(self, thread_id: str):
        self.thread_id = thread_id
        self.memory_agent = MemoryAgent()
        self.search_engine = MemorySearchEngine()
        
    def get_thread_context(self, requesting_agent: str) -> Dict[str, Any]:
        """Get comprehensive thread context for any agent"""
        
        # Search for relevant memories
        context_memories = self.search_engine.execute_search(
            query="important context and decisions",
            db_manager=self.db_manager,
            namespace=self.thread_id,
            limit=20
        )
        
        # Get recent files
        recent_files = self._get_recent_files(limit=10)
        
        # Get agent interaction history
        interactions = self._get_agent_interactions(limit=15)
        
        return {
            "thread_id": self.thread_id,
            "requesting_agent": requesting_agent,
            "context_memories": context_memories,
            "recent_files": recent_files,
            "agent_interactions": interactions,
            "last_updated": datetime.now().isoformat()
        }
        
    def record_agent_interaction(
        self,
        source_agent: str,
        interaction_type: str,
        context: Dict = None,
        result: Dict = None
    ):
        """Record agent interactions for collaboration tracking"""
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO agent_interactions 
                (id, thread_id, source_agent, interaction_type, context, result)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                str(uuid.uuid4()),
                self.thread_id,
                source_agent,
                interaction_type,
                json.dumps(context or {}),
                json.dumps(result or {})
            ))
```

## Enhanced Tool Integration

### Memory-Aware File Tools

```python
@tool
def enhanced_write_file(
    path: str, 
    content: str, 
    thread_id: str,
    agent_name: str = "unknown"
) -> str:
    """Write file with automatic memory creation"""
    
    file_manager = EnhancedThreadFileManager(thread_id)
    
    try:
        result = file_manager.store_file_with_memory(
            content=content,
            filename=path,
            file_type="generated",
            agent_name=agent_name
        )
        
        return f"File written successfully: {path} (Memory ID: {result['memory_id']})"
        
    except Exception as e:
        return f"Error writing file: {str(e)}"

@tool
def intelligent_file_search(
    query: str,
    thread_id: str,
    agent_name: str = "unknown"
) -> str:
    """Search files using AI-powered memory search"""
    
    file_manager = EnhancedThreadFileManager(thread_id)
    memory_manager = CrossAgentMemoryManager(thread_id)
    
    # Record the search interaction
    memory_manager.record_agent_interaction(
        source_agent=agent_name,
        interaction_type="file_search",
        context={"query": query}
    )
    
    try:
        results = file_manager.search_files_by_content(query)
        
        if not results:
            return f"No files found matching: {query}"
            
        summary = f"Found {len(results)} relevant files:\n"
        for result in results[:5]:  # Top 5 results
            summary += f"- {result['filename']}: {result.get('summary', 'No summary')}\n"
            
        return summary
        
    except Exception as e:
        return f"Error searching files: {str(e)}"

@tool
def get_thread_memory_context(
    query: str,
    thread_id: str,
    agent_name: str = "unknown"
) -> str:
    """Get relevant context from thread memory"""
    
    memory_manager = CrossAgentMemoryManager(thread_id)
    
    try:
        context = memory_manager.get_thread_context(agent_name)
        
        # Filter context based on query
        relevant_memories = []
        for memory in context['context_memories']:
            if any(keyword.lower() in memory.get('content', '').lower() 
                   for keyword in query.split()):
                relevant_memories.append(memory)
                
        if not relevant_memories:
            return f"No relevant context found for: {query}"
            
        summary = f"Relevant context from thread memory:\n"
        for memory in relevant_memories[:3]:  # Top 3 most relevant
            summary += f"- {memory.get('summary', memory.get('content', '')[:100])}...\n"
            
        return summary
        
    except Exception as e:
        return f"Error retrieving context: {str(e)}"
```

## Desktop App Integration

### Local Storage Structure

```
~/.myagents/
├── config/
│   ├── app_settings.json          # App configuration
│   └── user_profile.json          # Local user data
├── data/
│   ├── myagents.db               # Main SQLite database
│   └── files/                    # Large file storage
│       └── {thread_id}/          # Thread-specific files
│           ├── uploads/          # User uploads
│           ├── generated/        # AI-generated files
│           └── versions/         # File versions
└── logs/                         # Application logs
```

### Enhanced Agent Configuration

```python
def create_memory_enhanced_agent(agent_type: str = "main"):
    """Create agent with enhanced memory capabilities"""
    
    # Get enhanced tools
    enhanced_tools = [
        enhanced_write_file,
        enhanced_read_file,
        intelligent_file_search,
        get_thread_memory_context,
        # ... other tools
    ]
    
    # Create agent with memory-aware checkpointer
    agent = create_deep_agent(
        tools=enhanced_tools,
        instructions=get_memory_aware_instructions(agent_type),
        model=get_default_model(),
        checkpointer=get_enhanced_checkpointer(),
        # Memory-specific configuration
        memory_config={
            "enable_memory": True,
            "memory_classification": True,
            "cross_agent_sharing": True,
            "importance_scoring": True
        }
    )
    
    return agent

def get_memory_aware_instructions(agent_type: str) -> str:
    """Get instructions that emphasize memory usage"""
    
    base_instructions = f"""
You are a {agent_type} agent with enhanced memory capabilities. 

MEMORY USAGE GUIDELINES:
1. **Always search memory first** using get_thread_memory_context before starting new work
2. **Build upon previous work** - check what other agents have done in this thread
3. **Create meaningful memories** - your work will be remembered for future reference
4. **Use intelligent file search** to find relevant files and context
5. **Collaborate effectively** - other agents can access your work through shared memory

THREAD CONTEXT:
- Each thread is a project workspace
- All agents share the same memory within a thread
- Files, decisions, and context persist across agent switches
- Your contributions become part of the collective knowledge

Remember: You're part of a collaborative AI team with shared memory!
"""
    
    return base_instructions
```

## Implementation Roadmap

### Phase 1: Core Memory Integration (1-2 weeks)
1. **Database Schema Enhancement**
   - Add memory tables to existing SQLite database
   - Implement full-text search indexes
   - Create migration scripts

2. **Memory System Implementation**
   - Integrate Memori memory agent
   - Implement memory search engine
   - Add cross-agent memory manager

3. **Enhanced File Management**
   - Update file tools with memory integration
   - Implement intelligent file search
   - Add automatic memory creation for files

### Phase 2: Agent Enhancement (1-2 weeks)
1. **Memory-Aware Agents**
   - Update all agents with memory capabilities
   - Implement context-aware instructions
   - Add cross-agent collaboration features

2. **Enhanced Tools**
   - Create memory-aware versions of existing tools
   - Add intelligent search capabilities
   - Implement interaction tracking

### Phase 3: User Interface (1-2 weeks)
1. **Memory Browser**
   - UI for browsing thread memories
   - Search interface for finding context
   - Memory importance visualization

2. **File Management UI**
   - Enhanced file browser with memory integration
   - Intelligent file search interface
   - Version history with memory context

### Phase 4: Desktop Integration (1-2 weeks)
1. **Native Features**
   - File system watching with memory updates
   - Native file dialogs
   - System tray integration

2. **Performance Optimization**
   - Memory search caching
   - Background memory processing
   - Database optimization

## Benefits of This Enhanced Architecture

### 1. **Intelligent Context Management**
- AI automatically extracts and categorizes important information
- Smart search finds relevant context across all conversations
- Importance scoring prioritizes critical information

### 2. **Seamless Cross-Agent Collaboration**
- All agents share the same memory within threads
- Work builds upon previous agent contributions
- Automatic tracking of agent interactions

### 3. **Enhanced File Intelligence**
- Files are automatically linked to memories
- Intelligent search finds files by content and context
- Version control with memory-based change tracking

### 4. **Pure SQLite Efficiency**
- Single database handles all data types efficiently
- Full-text search provides fast memory retrieval
- ACID compliance ensures data integrity

### 5. **Local-First Privacy**
- All data stays on user's machine
- No cloud dependencies for core functionality
- Complete user control over data

## Migration from Current System

### Automatic Migration Process
```python
def migrate_to_enhanced_system():
    """Migrate existing threads to enhanced memory system"""
    
    # 1. Backup existing database
    backup_existing_database()
    
    # 2. Create new schema
    create_enhanced_schema()
    
    # 3. Migrate existing thread data
    migrate_thread_data()
    
    # 4. Extract memories from existing conversations
    extract_memories_from_history()
    
    # 5. Update file references
    update_file_references()
    
    print("✅ Migration completed successfully!")
```

## Conclusion

This enhanced architecture provides the best of all worlds:

1. ✅ **AI-Powered Memory**: Intelligent context management and retrieval
2. ✅ **Thread-Centric Design**: Maintains existing project model
3. ✅ **Cross-Agent Sharing**: Seamless collaboration between agents
4. ✅ **Local-Only Storage**: Complete privacy and control
5. ✅ **Pure SQLite Solution**: Efficient, reliable, and simple
6. ✅ **File Intelligence**: Smart file management with memory integration
7. ✅ **Desktop App Ready**: Native integration capabilities

The integration of Memori's memory system with our SQLite-based architecture creates a powerful desktop AI assistant that rivals commercial solutions while keeping all data local and under user control.

**Recommendation**: Proceed with Phase 1 implementation to validate the memory integration approach, then continue with the full roadmap.
