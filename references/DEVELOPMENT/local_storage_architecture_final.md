# MyAgents Desktop App - Local Storage Architecture (Final Plan)

## Executive Summary

Based on comprehensive analysis of requirements and existing infrastructure, this plan leverages the current SQLite-based system while adding file management capabilities for a desktop app that works like Cursor IDE, Windsurf, and Claude Code.

## Key Findings About Current System

### Thread Access Across Agents ✅
**EXCELLENT NEWS**: The current system already supports cross-agent thread access!

- All agents use the **same shared checkpointer** (`backend/data/checkpoints/agent_state.db`)
- When you select a different agent for an existing thread, that agent can access all previous thread state
- This means outputs from one agent (e.g., literature review) can be accessed by another agent (e.g., main agent)
- This is a **major advantage** - keep and enhance this feature!

### Current Architecture Strengths
1. **Unified State Storage**: Single SQLite database for all threads
2. **Cross-Agent Compatibility**: Any agent can access any thread
3. **Persistent State**: Files, todos, and conversation history survive restarts
4. **Thread-as-Project Model**: Already implemented via thread IDs

## Recommended Architecture: **Enhanced SQLite + Selective File System**

### Core Principle: "Best of Both Worlds"
- **Keep SQLite** for metadata, state, and small files
- **Add file system** for user uploads and large files
- **Maintain cross-agent thread access**
- **Enable user file editing**

## Storage Structure

```
~/.myagents/
├── config/
│   ├── app_config.json       # App settings
│   └── user_auth.json        # Local user credentials/credits
├── data/
│   ├── checkpoints/
│   │   └── agent_state.db    # Current SQLite (enhanced)
│   └── files/                # File system storage
│       ├── uploads/          # User-uploaded files
│       │   └── {thread_id}/  # Thread-specific uploads
│       ├── exports/          # Files ready for download
│       │   └── {thread_id}/  # Thread-specific exports
│       └── cache/            # Temporary files
└── logs/                     # Application logs
```

## Enhanced Database Schema

### Current Tables (Keep)
- LangGraph's built-in checkpoint tables
- Thread state and conversation history

### New Tables (Add)
```sql
-- File metadata and management
CREATE TABLE IF NOT EXISTS files (
    id TEXT PRIMARY KEY,              -- UUID
    thread_id TEXT NOT NULL,          -- Links to LangGraph thread
    filename TEXT NOT NULL,           -- Original filename
    storage_type TEXT NOT NULL,       -- 'sqlite_blob' | 'filesystem'
    storage_path TEXT,                -- Path if filesystem, NULL if blob
    file_type TEXT NOT NULL,          -- 'upload' | 'generated' | 'export'
    mime_type TEXT,                   -- MIME type
    size_bytes INTEGER NOT NULL,      -- File size
    hash_sha256 TEXT,                 -- Content hash for deduplication
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by_agent TEXT,            -- Which agent created it
    metadata TEXT,                    -- JSON metadata
    INDEX idx_thread_files (thread_id),
    INDEX idx_file_type (file_type)
);

-- File versions for change tracking
CREATE TABLE IF NOT EXISTS file_versions (
    id TEXT PRIMARY KEY,              -- Version UUID
    file_id TEXT NOT NULL,            -- References files.id
    version_number INTEGER NOT NULL,  -- Sequential version
    storage_path TEXT,                -- Path to version content
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,                  -- 'user' | 'agent_name'
    change_description TEXT,          -- What changed
    FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE,
    UNIQUE(file_id, version_number)
);

-- Thread metadata (enhance existing)
CREATE TABLE IF NOT EXISTS thread_metadata (
    thread_id TEXT PRIMARY KEY,       -- LangGraph thread ID
    project_name TEXT,                -- User-friendly name
    created_by_agent TEXT,            -- Original agent
    last_active_agent TEXT,           -- Most recent agent
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tags TEXT,                        -- JSON array of tags
    description TEXT                  -- Project description
);
```

## File Management Strategy

### Small Files (< 1MB): SQLite BLOB
- Generated code files
- Configuration files
- Text documents
- Fast access, atomic transactions

### Large Files (> 1MB): File System
- User uploads (documents, images, videos)
- Large datasets
- Binary files
- Better performance, direct OS access

### Implementation
```python
class ThreadFileManager:
    def __init__(self, thread_id: str):
        self.thread_id = thread_id
        self.db_path = get_checkpointer_path()
        self.files_root = Path.home() / ".myagents" / "data" / "files"
        
    def store_file(self, content: Union[str, bytes], filename: str, 
                   file_type: str = "generated") -> str:
        """Store file using appropriate strategy based on size"""
        size = len(content) if isinstance(content, (str, bytes)) else content.seek(0, 2)
        
        if size < 1024 * 1024:  # < 1MB: use SQLite
            return self._store_in_sqlite(content, filename, file_type)
        else:  # >= 1MB: use filesystem
            return self._store_in_filesystem(content, filename, file_type)
    
    def get_file(self, file_id: str) -> Optional[Union[str, bytes, Path]]:
        """Retrieve file content or path"""
        # Query database for file metadata
        # Return content (SQLite) or Path (filesystem)
        
    def update_file(self, file_id: str, content: Union[str, bytes], 
                    modified_by: str = "user") -> bool:
        """Update file and create version"""
        # Create new version
        # Update file content
        # Maintain version history
```

## User File Interaction Features

### 1. File Upload API
```python
@router.post("/threads/{thread_id}/files/upload")
async def upload_file(thread_id: str, file: UploadFile):
    """Upload file to specific thread"""
    file_manager = ThreadFileManager(thread_id)
    file_id = file_manager.store_file(
        await file.read(), 
        file.filename, 
        file_type="upload"
    )
    return {"file_id": file_id, "filename": file.filename}
```

### 2. File Download/Export
```python
@router.get("/threads/{thread_id}/files/{file_id}/download")
async def download_file(thread_id: str, file_id: str):
    """Download file from thread"""
    file_manager = ThreadFileManager(thread_id)
    file_path = file_manager.get_file(file_id)
    return FileResponse(file_path)
```

### 3. File Editing Interface
```python
@router.put("/threads/{thread_id}/files/{file_id}")
async def update_file(thread_id: str, file_id: str, content: str):
    """Update file content (creates new version)"""
    file_manager = ThreadFileManager(thread_id)
    success = file_manager.update_file(file_id, content, "user")
    return {"success": success}
```

### 4. Version Management
```python
@router.get("/threads/{thread_id}/files/{file_id}/versions")
async def get_file_versions(thread_id: str, file_id: str):
    """Get version history for file"""
    # Return list of versions with metadata

@router.get("/threads/{thread_id}/files/{file_id}/versions/{version}")
async def get_file_version(thread_id: str, file_id: str, version: int):
    """Get specific version of file"""
    # Return specific version content
```

## Cross-Agent Thread Access (Enhanced)

### Current Behavior (Keep)
- All agents share the same checkpointer
- Any agent can access any thread
- Thread state is preserved across agent switches

### Enhancements
```python
class CrossAgentFileAccess:
    @staticmethod
    def get_thread_files(thread_id: str, agent_name: str) -> List[FileMetadata]:
        """Get all files accessible to agent in thread"""
        # Return files created by any agent in this thread
        
    @staticmethod
    def create_file_reference(thread_id: str, file_id: str, 
                            referencing_agent: str) -> str:
        """Create reference to file from another agent's work"""
        # Log cross-agent file usage
        # Maintain audit trail
```

## Desktop App Integration

### 1. File System Watching
```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ThreadFileWatcher(FileSystemEventHandler):
    def on_modified(self, event):
        if not event.is_directory:
            # File was modified externally
            # Update database
            # Create new version
            # Notify UI
```

### 2. Native File Dialogs
```python
# Using tkinter for cross-platform file dialogs
import tkinter as tk
from tkinter import filedialog

def open_file_dialog(thread_id: str):
    """Open native file picker for uploads"""
    root = tk.Tk()
    root.withdraw()  # Hide main window
    
    files = filedialog.askopenfilenames(
        title="Select files to upload",
        filetypes=[("All files", "*.*")]
    )
    
    for file_path in files:
        # Upload to thread
        pass
```

### 3. System Tray Integration
```python
import pystray
from PIL import Image

def create_system_tray():
    """Create system tray for quick access"""
    menu = pystray.Menu(
        pystray.MenuItem("Open MyAgents", show_app),
        pystray.MenuItem("Recent Projects", show_recent),
        pystray.MenuItem("Exit", quit_app)
    )
    
    icon = pystray.Icon("MyAgents", Image.open("icon.png"), menu=menu)
    icon.run()
```

## Implementation Roadmap

### Phase 1: Enhanced File Management (1-2 weeks)
1. **Database Schema Updates**
   - Add new tables to existing SQLite database
   - Migrate existing file data
   
2. **File Manager Implementation**
   - Create `ThreadFileManager` class
   - Implement size-based storage strategy
   - Add version control

3. **API Endpoints**
   - File upload/download endpoints
   - File editing endpoints
   - Version management endpoints

### Phase 2: User Interface (1-2 weeks)
1. **File Management UI**
   - File browser for each thread
   - Upload/download interface
   - Version history viewer

2. **File Editor Integration**
   - In-app text editor for small files
   - External editor integration for large files
   - Real-time sync with file system

### Phase 3: Desktop App Features (2-3 weeks)
1. **Native Integration**
   - File system watching
   - Native file dialogs
   - System tray integration

2. **Packaging & Distribution**
   - PyInstaller/cx_Freeze packaging
   - Auto-updater implementation
   - Installation wizard

### Phase 4: Advanced Features (2-4 weeks)
1. **Enhanced Cross-Agent Features**
   - File sharing between threads
   - Agent collaboration workflows
   - File dependency tracking

2. **Performance Optimizations**
   - File caching strategies
   - Background sync processes
   - Memory management

## Migration Strategy

### From Current System
1. **Automatic Migration**
   ```python
   def migrate_existing_data():
       """Migrate existing SQLite blobs to new system"""
       # Extract files from current checkpointer
       # Apply size-based storage strategy
       # Update metadata tables
   ```

2. **Backward Compatibility**
   - Keep existing file access methods working
   - Gradual migration of files to new system
   - No disruption to existing threads

## Security Considerations

### Local Data Protection
1. **File Permissions**
   - Restrict access to MyAgents directory
   - Use OS-level file permissions

2. **Data Encryption** (Optional)
   - Encrypt sensitive files at rest
   - Use user's system keychain for keys

3. **Audit Trail**
   - Log all file operations
   - Track cross-agent access
   - Maintain change history

## Benefits of This Architecture

### 1. **Maintains Current Strengths**
- Cross-agent thread access ✅
- SQLite reliability ✅
- Thread-as-project model ✅

### 2. **Adds Desktop App Features**
- Real file system integration ✅
- User file uploads/editing ✅
- Native OS integration ✅

### 3. **Performance Optimized**
- Small files: Fast SQLite access
- Large files: Efficient file system storage
- Hybrid approach for best performance

### 4. **User Experience**
- Works like Cursor/Windsurf/Claude Code
- Familiar file management
- Seamless agent switching

### 5. **Future-Proof**
- Scalable storage strategy
- Version control built-in
- Easy to add cloud sync later

## Conclusion

This architecture provides the best solution for your requirements:

1. ✅ **Desktop app with local storage** - All data stays local
2. ✅ **Thread-based project management** - Uses existing infrastructure  
3. ✅ **Cross-agent thread access** - Already working, enhanced further
4. ✅ **User file interaction** - Upload, edit, download capabilities
5. ✅ **SQLite strengths maintained** - Fast queries, reliability, atomic operations
6. ✅ **File system benefits added** - Real files for user interaction

The hybrid SQLite + file system approach gives you the reliability and query capabilities of SQLite while providing the user experience of real file management that desktop coding apps require.

**Recommendation**: Proceed with Phase 1 implementation to validate the approach, then continue with the full roadmap.
