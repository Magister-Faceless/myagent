"""
Enhanced File Management System with Memory Integration

This module provides intelligent file management that integrates with the memory system
to create contextual file storage and retrieval capabilities.
"""

import os
import hashlib
import sqlite3
import json
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Union, BinaryIO
from datetime import datetime

from core.database.enhanced_schema import get_enhanced_db_manager
from core.memory.memory_agent import get_memory_agent
from core.memory.search_engine import get_search_engine


class EnhancedThreadFileManager:
    """Enhanced file manager with memory integration for thread-based file management"""
    
    def __init__(self, thread_id: str):
        """Initialize enhanced file manager for a specific thread"""
        self.thread_id = thread_id
        self.db_manager = get_enhanced_db_manager()
        self.memory_agent = get_memory_agent()
        self.search_engine = get_search_engine()
        
        # Create thread-specific file storage directory
        self.files_root = Path.home() / ".myagents" / "data" / "files" / thread_id
        self.files_root.mkdir(parents=True, exist_ok=True)
        
        # Ensure thread exists in database
        self._ensure_thread_exists()
    
    def _ensure_thread_exists(self):
        """Ensure thread exists in database"""
        try:
            existing_thread = self.db_manager.get_thread(self.thread_id)
            if not existing_thread:
                self.db_manager.create_thread(self.thread_id)
        except Exception as e:
            print(f"⚠️ Failed to ensure thread exists: {e}")
    
    def store_file_with_memory(
        self,
        content: Union[str, bytes, BinaryIO],
        filename: str,
        file_type: str = "upload",
        agent_name: str = "user",
        metadata: Optional[Dict] = None
    ) -> Dict[str, str]:
        """
        Store file with automatic memory creation and linking
        
        Args:
            content: File content (string, bytes, or file-like object)
            filename: Original filename
            file_type: Type of file ('upload', 'generated', 'export')
            agent_name: Agent or user storing the file
            metadata: Additional metadata
            
        Returns:
            Dictionary with file_id, memory_id, and storage info
        """
        try:
            # Process content
            if hasattr(content, 'read'):
                # File-like object
                content_bytes = content.read()
                if isinstance(content_bytes, str):
                    content_bytes = content_bytes.encode('utf-8')
            elif isinstance(content, str):
                content_bytes = content.encode('utf-8')
            else:
                content_bytes = content
            
            # Determine storage strategy
            size_bytes = len(content_bytes)
            storage_type = "blob" if size_bytes < 10 * 1024 * 1024 else "filesystem"  # 10MB threshold
            
            # Generate file ID and hash
            file_id = str(uuid.uuid4())
            content_hash = hashlib.sha256(content_bytes).hexdigest()
            
            # Determine MIME type
            mime_type = self._guess_mime_type(filename)
            
            # Store file content
            file_path = None
            blob_content = None
            
            if storage_type == "filesystem":
                # Store on filesystem
                file_path = str(self.files_root / f"{file_id}_{filename}")
                Path(file_path).write_bytes(content_bytes)
            else:
                # Store as blob in database
                blob_content = content_bytes
            
            # Create memory for the file
            memory_content = self._create_file_memory_content(
                filename=filename,
                file_type=file_type,
                size_bytes=size_bytes,
                content_preview=content.decode('utf-8', errors='ignore')[:500] if isinstance(content, bytes) else str(content)[:500] if isinstance(content, str) else "",
                agent_name=agent_name
            )
            
            # Process memory
            processed_memory = self.memory_agent.process_conversation(
                thread_id=self.thread_id,
                user_input=f"File operation: {file_type} file '{filename}'",
                ai_output=memory_content,
                agent_name=agent_name,
                conversation_id=f"file_{file_id}"
            )
            
            # Store file record in database
            self._store_file_record(
                file_id=file_id,
                memory_id=processed_memory.id,
                filename=filename,
                file_path=file_path,
                storage_type=storage_type,
                file_type=file_type,
                mime_type=mime_type,
                size_bytes=size_bytes,
                hash_sha256=content_hash,
                content=blob_content,
                agent_name=agent_name,
                metadata=metadata
            )
            
            # Create initial version
            self._create_file_version(
                file_id=file_id,
                version_number=1,
                content=content_bytes,
                created_by=agent_name,
                description="Initial version"
            )
            
            print(f"✅ File stored: {filename} ({storage_type}, {size_bytes} bytes)")
            
            return {
                "file_id": file_id,
                "memory_id": processed_memory.id,
                "storage_type": storage_type,
                "filename": filename,
                "size_bytes": size_bytes
            }
            
        except Exception as e:
            print(f"❌ Failed to store file {filename}: {e}")
            raise
    
    def get_file_content(self, file_id: str) -> Optional[bytes]:
        """Get file content by file ID"""
        try:
            with sqlite3.connect(self.db_manager.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT storage_type, file_path, content, filename
                    FROM files 
                    WHERE id = ? AND thread_id = ?
                """, (file_id, self.thread_id))
                
                result = cursor.fetchone()
                if not result:
                    return None
                
                if result['storage_type'] == 'filesystem':
                    # Read from filesystem
                    file_path = Path(result['file_path'])
                    if file_path.exists():
                        return file_path.read_bytes()
                    else:
                        print(f"⚠️ File not found on filesystem: {file_path}")
                        return None
                else:
                    # Return blob content
                    return result['content']
                    
        except Exception as e:
            return None
    
    def search_files_by_content(self, query: str, limit: int = 10, agent_name: str = "user") -> List[Dict]:
        """Search files using AI-powered memory search"""
        try:
            # Search for related memories
            search_results = self.search_engine.search_memories(
                query=f"files {query}",
                thread_id=self.thread_id,
                agent_name=agent_name
            )
            
            # Extract file IDs from memories
            file_results = []
            seen_file_ids = set()
            
            with sqlite3.connect(self.db_manager.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                for memory in search_results:
                    # Find files linked to this memory
                    cursor = conn.execute("""
                        SELECT f.*, m.summary as memory_summary
                        FROM files f
                        LEFT JOIN memories m ON f.memory_id = m.id
                        WHERE f.memory_id = ? AND f.thread_id = ?
                    """, (memory.get('memory_id'), self.thread_id))
                    
                    for file_row in cursor.fetchall():
                        if file_row['id'] not in seen_file_ids:
                            seen_file_ids.add(file_row['id'])
                            file_dict = dict(file_row)
                            file_dict['search_relevance'] = memory.get('search_rank', 0)
                            file_dict['memory_context'] = memory.get('summary', '')
                            file_results.append(file_dict)
                
                # Also search files directly by filename
                cursor = conn.execute("""
                    SELECT f.*, m.summary as memory_summary
                    FROM files f
                    LEFT JOIN memories m ON f.memory_id = m.id
                    WHERE f.thread_id = ? AND (
                        f.filename LIKE ? OR 
                        f.metadata LIKE ?
                    )
                    ORDER BY f.created_at DESC
                    LIMIT ?
                """, (self.thread_id, f"%{query}%", f"%{query}%", limit))
                
                for file_row in cursor.fetchall():
                    if file_row['id'] not in seen_file_ids:
                        seen_file_ids.add(file_row['id'])
                        file_dict = dict(file_row)
                        file_dict['search_relevance'] = 0.5  # Lower relevance for filename matches
                        file_dict['memory_context'] = file_dict.get('memory_summary', '')
                        file_results.append(file_dict)
            
            # Sort by relevance
            file_results.sort(key=lambda x: x.get('search_relevance', 0), reverse=True)
            
            return file_results[:limit]
            
        except Exception as e:
            print(f"❌ File search failed: {e}")
            return []
    
    def update_file(
        self,
        file_id: str,
        new_content: Union[str, bytes],
        modified_by: str = "user",
        change_description: str = "File updated"
    ) -> bool:
        """Update file content and create new version"""
        try:
            # Get current file info
            with sqlite3.connect(self.db_manager.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT * FROM files WHERE id = ? AND thread_id = ?
                """, (file_id, self.thread_id))
                
                file_info = cursor.fetchone()
                if not file_info:
                    print(f"❌ File not found: {file_id}")
                    return False
                
                file_info = dict(file_info)
            
            # Process new content
            if isinstance(new_content, str):
                content_bytes = new_content.encode('utf-8')
            else:
                content_bytes = new_content
            
            # Get next version number
            next_version = self._get_next_version_number(file_id)
            
            # Update file content based on storage type
            if file_info['storage_type'] == 'filesystem':
                # Update filesystem file
                file_path = Path(file_info['file_path'])
                file_path.write_bytes(content_bytes)
            else:
                # Update blob in database
                with sqlite3.connect(self.db_manager.db_path) as conn:
                    conn.execute("""
                        UPDATE files 
                        SET content = ?, modified_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    """, (content_bytes, file_id))
                    conn.commit()
            
            # Create new version
            self._create_file_version(
                file_id=file_id,
                version_number=next_version,
                content=content_bytes,
                created_by=modified_by,
                description=change_description
            )
            
            # Create memory for the update
            update_memory = f"File '{file_info['filename']}' was updated by {modified_by}. {change_description}"
            self.memory_agent.process_conversation(
                thread_id=self.thread_id,
                user_input=f"Update file: {file_info['filename']}",
                ai_output=update_memory,
                agent_name=modified_by,
                conversation_id=f"file_update_{file_id}_{next_version}"
            )
            
            print(f"✅ File updated: {file_info['filename']} (version {next_version})")
            return True
            
        except Exception as e:
            print(f"❌ Failed to update file: {e}")
            return False
    
    def list_files(self, file_type: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """List files in the thread"""
        try:
            with sqlite3.connect(self.db_manager.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                if file_type:
                    cursor = conn.execute("""
                        SELECT f.*, m.summary as memory_summary
                        FROM files f
                        LEFT JOIN memories m ON f.memory_id = m.id
                        WHERE f.thread_id = ? AND f.file_type = ?
                        ORDER BY f.created_at DESC
                        LIMIT ?
                    """, (self.thread_id, file_type, limit))
                else:
                    cursor = conn.execute("""
                        SELECT f.*, m.summary as memory_summary
                        FROM files f
                        LEFT JOIN memories m ON f.memory_id = m.id
                        WHERE f.thread_id = ?
                        ORDER BY f.created_at DESC
                        LIMIT ?
                    """, (self.thread_id, limit))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            print(f"❌ Failed to list files: {e}")
            return []
    
    def get_file_versions(self, file_id: str) -> List[Dict]:
        """Get version history for a file"""
        try:
            with sqlite3.connect(self.db_manager.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT * FROM file_versions 
                    WHERE file_id = ?
                    ORDER BY version_number DESC
                """, (file_id,))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            print(f"❌ Failed to get file versions: {e}")
            return []
    
    def _create_file_memory_content(
        self,
        filename: str,
        file_type: str,
        size_bytes: int,
        content_preview: str,
        agent_name: str
    ) -> str:
        """Create memory content for file operations"""
        
        size_str = self._format_file_size(size_bytes)
        
        memory_content = f"""File Operation: {file_type.title()} - {filename}

File Details:
- Name: {filename}
- Type: {file_type}
- Size: {size_str}
- Processed by: {agent_name}

"""
        
        if content_preview and len(content_preview.strip()) > 0:
            memory_content += f"Content Preview:\n{content_preview[:300]}..."
            if len(content_preview) > 300:
                memory_content += "\n(Content truncated for memory storage)"
        
        return memory_content
    
    def _store_file_record(
        self,
        file_id: str,
        memory_id: str,
        filename: str,
        file_path: Optional[str],
        storage_type: str,
        file_type: str,
        mime_type: str,
        size_bytes: int,
        hash_sha256: str,
        content: Optional[bytes],
        agent_name: str,
        metadata: Optional[Dict]
    ):
        """Store file record in database"""
        
        with sqlite3.connect(self.db_manager.db_path) as conn:
            conn.execute("""
                INSERT INTO files (
                    id, thread_id, memory_id, filename, file_path, storage_type,
                    file_type, mime_type, size_bytes, hash_sha256, content,
                    created_by_agent, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                file_id, self.thread_id, memory_id, filename, file_path, storage_type,
                file_type, mime_type, size_bytes, hash_sha256, content,
                agent_name, json.dumps(metadata or {})
            ))
            conn.commit()
    
    def _create_file_version(
        self,
        file_id: str,
        version_number: int,
        content: bytes,
        created_by: str,
        description: str
    ):
        """Create a new file version"""
        
        version_id = str(uuid.uuid4())
        
        with sqlite3.connect(self.db_manager.db_path) as conn:
            conn.execute("""
                INSERT INTO file_versions (
                    id, file_id, version_number, content, created_by, change_description
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (version_id, file_id, version_number, content, created_by, description))
            conn.commit()
    
    def _get_next_version_number(self, file_id: str) -> int:
        """Get the next version number for a file"""
        
        with sqlite3.connect(self.db_manager.db_path) as conn:
            cursor = conn.execute("""
                SELECT MAX(version_number) as max_version 
                FROM file_versions 
                WHERE file_id = ?
            """, (file_id,))
            
            result = cursor.fetchone()
            return (result[0] or 0) + 1
    
    def _guess_mime_type(self, filename: str) -> str:
        """Guess MIME type from filename"""
        
        import mimetypes
        mime_type, _ = mimetypes.guess_type(filename)
        return mime_type or "application/octet-stream"
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format"""
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"


def get_enhanced_file_manager(thread_id: str) -> EnhancedThreadFileManager:
    """Get enhanced file manager for a thread"""
    return EnhancedThreadFileManager(thread_id)


# Export for easy import
__all__ = ["EnhancedThreadFileManager", "get_enhanced_file_manager"]
