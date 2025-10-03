# Data Persistence System Analysis

## 🔍 **Current Setup - TWO Database Systems**

Your application has **TWO separate database systems** running in parallel:

### **1. LangGraph Checkpointer (Missing/Not Working)**
**Location:** `backend/data/checkpoints/agent_state.db`
**Status:** ❌ **DATABASE FILE DOESN'T EXIST**
**Purpose:** LangGraph's built-in state persistence
**What it stores:**
- Agent conversation state
- Message history
- Internal LangGraph state
- Files created via built-in tools

**Problem:** The checkpointer is configured but the database file is never created, which means:
- ❌ No conversation state is saved
- ❌ Files created by agents are lost on restart
- ❌ Thread state is not persisted

### **2. Enhanced Database (Working)**
**Location:** `backend/data/enhanced/myagents_enhanced.db`
**Status:** ✅ **EXISTS AND WORKING**
**Purpose:** Custom memory and file management system
**What it stores:**
- Threads (with metadata)
- Memories (AI memory system)
- Files (with versions)
- Agent interactions

## 📊 **Enhanced Database Schema**

### **Tables Structure:**

#### **1. threads**
```sql
CREATE TABLE threads (
    id TEXT PRIMARY KEY,
    name TEXT,
    description TEXT,
    created_by_agent TEXT,
    last_active_agent TEXT,
    created_at TIMESTAMP,
    last_accessed TIMESTAMP,
    metadata TEXT,
    status TEXT DEFAULT 'active'
)
```

#### **2. memories**
```sql
CREATE TABLE memories (
    id TEXT PRIMARY KEY,
    thread_id TEXT NOT NULL,
    conversation_id TEXT,
    content TEXT NOT NULL,
    summary TEXT,
    classification TEXT NOT NULL,
    importance TEXT NOT NULL,
    topic TEXT,
    entities TEXT,
    keywords TEXT,
    is_user_context BOOLEAN,
    is_preference BOOLEAN,
    is_skill_knowledge BOOLEAN,
    is_current_project BOOLEAN,
    confidence_score REAL,
    promotion_eligible BOOLEAN,
    created_by_agent TEXT,
    created_at TIMESTAMP,
    modified_at TIMESTAMP,
    FOREIGN KEY (thread_id) REFERENCES threads(id) ON DELETE CASCADE
)
```

#### **3. files**
```sql
CREATE TABLE files (
    id TEXT PRIMARY KEY,
    thread_id TEXT NOT NULL,
    memory_id TEXT,
    filename TEXT NOT NULL,
    filepath TEXT NOT NULL,
    content_type TEXT,
    size_bytes INTEGER,
    created_by_agent TEXT,
    created_at TIMESTAMP,
    modified_at TIMESTAMP,
    metadata TEXT,
    FOREIGN KEY (thread_id) REFERENCES threads(id) ON DELETE CASCADE,
    FOREIGN KEY (memory_id) REFERENCES memories(id) ON DELETE SET NULL
)
```

#### **4. file_versions**
```sql
CREATE TABLE file_versions (
    id TEXT PRIMARY KEY,
    file_id TEXT NOT NULL,
    version_number INTEGER NOT NULL,
    content TEXT,
    content_hash TEXT,
    created_by_agent TEXT,
    created_at TIMESTAMP,
    change_description TEXT,
    FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE
)
```

#### **5. agent_interactions**
```sql
CREATE TABLE agent_interactions (
    id TEXT PRIMARY KEY,
    thread_id TEXT NOT NULL,
    agent_id TEXT NOT NULL,
    interaction_type TEXT NOT NULL,
    input_data TEXT,
    output_data TEXT,
    tools_used TEXT,
    subagents_spawned TEXT,
    created_at TIMESTAMP,
    duration_ms INTEGER,
    FOREIGN KEY (thread_id) REFERENCES threads(id) ON DELETE CASCADE
)
```

## 🔗 **Data Relationships**

```
threads (1) ──────┬─────── (N) memories
                  │
                  ├─────── (N) files ────── (N) file_versions
                  │
                  └─────── (N) agent_interactions
```

**CASCADE DELETE:** When a thread is deleted, ALL related data is automatically deleted:
- ✅ All memories for that thread
- ✅ All files for that thread
- ✅ All file versions
- ✅ All agent interactions

## ❌ **Why Data Was Lost**

When you used the **dynamic literature-review agent**, here's what happened:

1. **Agent Factory created the agent** with checkpointer
2. **Checkpointer tried to save to:** `agent_state.db`
3. **Database file was never created** (SqliteSaver import issue or initialization failure)
4. **State saved to memory only** (in-memory fallback)
5. **Server restart** → All in-memory data lost
6. **Enhanced DB** was not being used by the dynamic agent

## ✅ **Why Older Data Still Exists**

Older threads/files exist because:
- They were saved in the **Enhanced Database** (`myagents_enhanced.db`)
- This database persists across restarts
- It's independent of the LangGraph checkpointer

## 🎯 **The Solution: Unified Persistence**

We need to ensure BOTH systems work together:

### **Option 1: Fix LangGraph Checkpointer (Recommended)**
- Ensure SqliteSaver is properly installed
- Create the database file on initialization
- All agents use the same checkpointer

### **Option 2: Use Enhanced DB Only**
- Disable LangGraph checkpointer
- Route all persistence through Enhanced DB
- Implement custom state management

### **Option 3: Hybrid Approach (Best)**
- LangGraph Checkpointer for agent state
- Enhanced DB for structured data (threads, memories, files)
- Sync between both systems

## 📋 **Current Issues**

1. ❌ **Checkpointer DB doesn't exist**
   - File: `agent_state.db` is missing
   - SqliteSaver may not be installed or failing

2. ❌ **Dynamic agents may not use Enhanced DB**
   - Agent factory creates agents with checkpointer
   - May not integrate with Enhanced DB

3. ❌ **No sync between systems**
   - LangGraph state separate from Enhanced DB
   - Data fragmentation possible

## 🔧 **Next Steps**

1. **Verify SqliteSaver installation**
2. **Test checkpointer creation**
3. **Ensure all agents use both systems**
4. **Implement proper data sync**
5. **Add cascade delete for checkpointer data**
