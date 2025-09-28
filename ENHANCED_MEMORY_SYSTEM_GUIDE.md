# MyAgents Enhanced Memory System - User Guide

## Overview

The Enhanced Memory System transforms MyAgents into an intelligent, context-aware AI assistant with persistent memory, cross-agent collaboration, and intelligent file management. This system enables:

- **Intelligent Memory Processing**: Conversations are automatically processed into structured, searchable memories
- **Cross-Agent Collaboration**: All agents share memory within threads for seamless collaboration
- **Enhanced File Management**: Files are intelligently stored with memory links for easy discovery
- **Contextual Awareness**: Agents understand and build upon previous work in each thread

## Key Features

### 🧠 Intelligent Memory System
- **Automatic Processing**: Every conversation is processed into structured memories
- **Smart Classification**: Memories are categorized (essential, contextual, conversational, etc.)
- **Importance Scoring**: Critical information is prioritized for easy retrieval
- **Deduplication**: Prevents redundant information storage

### 🤝 Cross-Agent Collaboration
- **Shared Thread Memory**: All agents can access and build upon each other's work
- **Context Handoffs**: When switching agents, context is preserved automatically
- **Collaborative Building**: Agents reference and extend previous work
- **Interaction Tracking**: System tracks how agents collaborate

### 📁 Enhanced File Management
- **Memory-Linked Files**: Files are automatically connected to conversation memories
- **Intelligent Search**: Find files by content, context, or related conversations
- **Version Control**: Automatic versioning with change descriptions
- **Smart Storage**: Hybrid approach using SQLite for small files, filesystem for large files

### 🔍 Contextual Search
- **AI-Powered Search**: Understands intent and finds relevant information
- **Multi-Modal Search**: Search across memories, files, and agent interactions
- **Context-Aware Results**: Results include relevance and relationship information

## Getting Started

### 1. Setup the Enhanced System

Run the setup script to initialize the enhanced memory system:

```bash
cd backend
python scripts/setup_enhanced_system.py --setup
```

This will:
- Initialize the enhanced database
- Test all memory system components
- Create sample data to verify functionality

### 2. Migrate Existing Data (Optional)

If you have existing MyAgents data, migrate it to the enhanced system:

```bash
python scripts/migrate_to_enhanced_system.py
```

This will:
- Backup your existing data
- Extract memories from conversation history
- Migrate files and thread information
- Preserve all existing functionality

### 3. Start Using Enhanced Features

The enhanced system is now active! All conversations will automatically:
- Create structured memories
- Enable cross-agent collaboration
- Provide intelligent file management

## Using Enhanced Features

### Memory-Aware Conversations

Every conversation now creates intelligent memories:

**User**: "I'm working on a Python web scraping project using BeautifulSoup"

**Enhanced Agent**: 
- Processes this into a structured memory
- Classifies it as "current project" information
- Makes it searchable for future conversations
- Links it to any related files created

### Cross-Agent Collaboration

Switch between agents seamlessly:

1. **Literature Review Agent** creates research files and memories
2. **Switch to Main Agent** - automatically accesses previous work
3. **Main Agent** builds upon literature review findings
4. **All work is preserved** and accessible to future agents

### Enhanced File Operations

#### Create Files with Memory
```python
# Files are automatically linked to memories
enhanced_write_file("project_plan.md", content, thread_id, agent_name)
```

#### Intelligent File Search
```python
# Search files by content and context
intelligent_file_search("python scraping project", thread_id, agent_name)
```

#### Get Thread Context
```python
# Get comprehensive thread context
get_shared_context_summary(thread_id, agent_name)
```

## Enhanced Tools Reference

### Memory & Context Tools

#### `get_shared_context_summary(thread_id, agent_name)`
Get a comprehensive summary of all work done in the thread.

**Example**: "What has been accomplished in this project so far?"

#### `get_thread_memory_context(query, thread_id, agent_name)`
Search for specific information in thread memory.

**Example**: "Find information about the database schema we discussed"

### Enhanced File Tools

#### `enhanced_write_file(path, content, thread_id, agent_name)`
Create files with automatic memory linking and intelligent storage.

#### `enhanced_read_file(file_path, thread_id, agent_name)`
Read files with access tracking and memory context.

#### `intelligent_file_search(query, thread_id, agent_name)`
Search files using AI-powered understanding of content and context.

#### `list_thread_files(thread_id, agent_name, file_type, limit)`
List all files in the thread with metadata and context.

#### `update_file_content(file_path, new_content, thread_id, agent_name)`
Update files with automatic versioning and change tracking.

## Best Practices

### For Users

1. **Use Descriptive Requests**: The more context you provide, the better the memory system works
2. **Reference Previous Work**: Ask agents to build upon previous conversations
3. **Switch Agents Freely**: Each agent can access the full thread context
4. **Upload Relevant Files**: Files become part of the searchable knowledge base

### For Developers

1. **Always Use Enhanced Tools**: Use the enhanced file tools instead of basic ones
2. **Check Context First**: Use `get_shared_context_summary` before starting new work
3. **Create Meaningful Files**: Files with good content become valuable memory resources
4. **Document Decisions**: Important decisions become searchable memories

## Architecture Overview

### Database Structure
```
~/.myagents/data/enhanced/myagents_enhanced.db
├── threads          # Thread metadata
├── memories         # Structured conversation memories
├── files           # File metadata and small file storage
├── file_versions   # File version history
└── agent_interactions  # Cross-agent collaboration tracking
```

### File Storage
```
~/.myagents/data/files/
└── {thread_id}/
    ├── uploads/     # User-uploaded files
    ├── generated/   # AI-generated files
    └── versions/    # File version storage
```

## Troubleshooting

### Common Issues

#### "Memory processing failed"
- Check that the model configuration is correct
- Ensure the database is properly initialized
- Run the test script: `python scripts/setup_enhanced_system.py --test`

#### "File not found"
- Files might be stored as BLOBs in the database for small files
- Use `list_thread_files` to see all available files
- Check the file ID vs filename - the system uses UUIDs internally

#### "Cross-agent context not working"
- Ensure all agents are using the enhanced system
- Check that the thread ID is consistent across agent calls
- Verify the database contains the expected thread data

### Testing the System

Run comprehensive tests:
```bash
python scripts/setup_enhanced_system.py --test
```

Clean up test data:
```bash
python scripts/setup_enhanced_system.py --clean
```

## Advanced Features

### Memory Classification Types

- **essential**: Core facts, important preferences, key skills
- **contextual**: Current work context, ongoing projects
- **conversational**: Regular discussions, explanations
- **reference**: Code examples, documentation, resources
- **personal**: Personal information, preferences
- **conscious_info**: User details that should be immediately accessible

### File Storage Strategy

- **Small files (< 10MB)**: Stored as BLOBs in SQLite for fast access
- **Large files (≥ 10MB)**: Stored on filesystem with metadata in database
- **All files**: Linked to memories for contextual discovery

### Search Capabilities

- **Full-text search**: Using SQLite FTS5 for fast text search
- **Semantic search**: AI-powered understanding of search intent
- **Context-aware**: Results include relationship and relevance information
- **Multi-modal**: Search across memories, files, and interactions

## Support

For issues or questions:
1. Check this guide for common solutions
2. Run the test script to verify system functionality
3. Check the backup files if migration issues occur
4. Review the implementation files in `backend/core/` for technical details

The Enhanced Memory System represents a significant upgrade to MyAgents, providing the foundation for truly intelligent, context-aware AI assistance.
