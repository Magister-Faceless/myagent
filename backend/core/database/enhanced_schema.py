"""
Enhanced Database Schema for MyAgents with Memory System Integration

This module provides the enhanced database schema that integrates AI memory
capabilities with the existing thread-based architecture.
"""

import sqlite3
import os
from pathlib import Path
from typing import Optional
from datetime import datetime
import uuid
import json

class EnhancedDatabaseManager:
    """Enhanced database manager with memory system integration"""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize enhanced database manager"""
        if db_path is None:
            # Use the same path as the existing checkpointer
            backend_dir = Path(__file__).parent.parent.parent
            db_dir = backend_dir / "data" / "enhanced"
            db_dir.mkdir(parents=True, exist_ok=True)
            db_path = str(db_dir / "myagents_enhanced.db")
        
        self.db_path = db_path
        self.database_type = "sql"  # For memori compatibility
        self._init_database()
    
    def _init_database(self):
        """Initialize the enhanced database with all required tables"""
        with sqlite3.connect(self.db_path) as conn:
            # Enable foreign keys
            conn.execute("PRAGMA foreign_keys = ON")
            
            # Create all tables
            self._create_threads_table(conn)
            self._create_memories_table(conn)
            self._create_files_table(conn)
            self._create_file_versions_table(conn)
            self._create_agent_interactions_table(conn)
            self._create_indexes(conn)
            self._create_fts_tables(conn)
            
            conn.commit()
            print(f"✅ Enhanced database initialized: {self.db_path}")
    
    def _create_threads_table(self, conn):
        """Create enhanced threads table"""
        conn.execute("""
            CREATE TABLE IF NOT EXISTS threads (
                id TEXT PRIMARY KEY,
                name TEXT,
                description TEXT,
                created_by_agent TEXT,
                last_active_agent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT,
                status TEXT DEFAULT 'active'
            )
        """)
    
    def _create_memories_table(self, conn):
        """Create enhanced memories table based on Memori architecture"""
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memories (
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
                is_user_context BOOLEAN DEFAULT FALSE,
                is_preference BOOLEAN DEFAULT FALSE,
                is_skill_knowledge BOOLEAN DEFAULT FALSE,
                is_current_project BOOLEAN DEFAULT FALSE,
                confidence_score REAL DEFAULT 0.7,
                promotion_eligible BOOLEAN DEFAULT FALSE,
                created_by_agent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (thread_id) REFERENCES threads(id) ON DELETE CASCADE
            )
        """)
    
    def _create_files_table(self, conn):
        """Create enhanced files table with memory integration"""
        conn.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id TEXT PRIMARY KEY,
                thread_id TEXT NOT NULL,
                memory_id TEXT,
                filename TEXT NOT NULL,
                file_path TEXT,
                storage_type TEXT NOT NULL,
                file_type TEXT NOT NULL,
                mime_type TEXT,
                size_bytes INTEGER NOT NULL,
                hash_sha256 TEXT,
                content BLOB,
                created_by_agent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT,
                FOREIGN KEY (thread_id) REFERENCES threads(id) ON DELETE CASCADE,
                FOREIGN KEY (memory_id) REFERENCES memories(id) ON DELETE SET NULL
            )
        """)
    
    def _create_file_versions_table(self, conn):
        """Create file versions table for change tracking"""
        conn.execute("""
            CREATE TABLE IF NOT EXISTS file_versions (
                id TEXT PRIMARY KEY,
                file_id TEXT NOT NULL,
                version_number INTEGER NOT NULL,
                content BLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT,
                change_description TEXT,
                FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE,
                UNIQUE(file_id, version_number)
            )
        """)
    
    def _create_agent_interactions_table(self, conn):
        """Create agent interactions table for collaboration tracking"""
        conn.execute("""
            CREATE TABLE IF NOT EXISTS agent_interactions (
                id TEXT PRIMARY KEY,
                thread_id TEXT NOT NULL,
                source_agent TEXT NOT NULL,
                target_agent TEXT,
                interaction_type TEXT NOT NULL,
                context TEXT,
                result TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (thread_id) REFERENCES threads(id) ON DELETE CASCADE
            )
        """)
    
    def _create_indexes(self, conn):
        """Create performance indexes"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_memories_thread ON memories(thread_id)",
            "CREATE INDEX IF NOT EXISTS idx_memories_classification ON memories(classification)",
            "CREATE INDEX IF NOT EXISTS idx_memories_importance ON memories(importance)",
            "CREATE INDEX IF NOT EXISTS idx_memories_created_at ON memories(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_files_thread ON files(thread_id)",
            "CREATE INDEX IF NOT EXISTS idx_files_type ON files(file_type)",
            "CREATE INDEX IF NOT EXISTS idx_agent_interactions_thread ON agent_interactions(thread_id)",
            "CREATE INDEX IF NOT EXISTS idx_threads_status ON threads(status)",
            "CREATE INDEX IF NOT EXISTS idx_threads_last_accessed ON threads(last_accessed)"
        ]
        
        for index_sql in indexes:
            conn.execute(index_sql)
    
    def _create_fts_tables(self, conn):
        """Create full-text search tables"""
        # Full-text search for memories
        conn.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(
                content, summary, topic, entities, keywords,
                content='memories', content_rowid='rowid'
            )
        """)
        
        # Trigger to keep FTS table in sync
        conn.execute("""
            CREATE TRIGGER IF NOT EXISTS memories_fts_insert AFTER INSERT ON memories BEGIN
                INSERT INTO memories_fts(rowid, content, summary, topic, entities, keywords)
                VALUES (new.rowid, new.content, new.summary, new.topic, new.entities, new.keywords);
            END
        """)
        
        conn.execute("""
            CREATE TRIGGER IF NOT EXISTS memories_fts_delete AFTER DELETE ON memories BEGIN
                INSERT INTO memories_fts(memories_fts, rowid, content, summary, topic, entities, keywords)
                VALUES ('delete', old.rowid, old.content, old.summary, old.topic, old.entities, old.keywords);
            END
        """)
        
        conn.execute("""
            CREATE TRIGGER IF NOT EXISTS memories_fts_update AFTER UPDATE ON memories BEGIN
                INSERT INTO memories_fts(memories_fts, rowid, content, summary, topic, entities, keywords)
                VALUES ('delete', old.rowid, old.content, old.summary, old.topic, old.entities, old.keywords);
                INSERT INTO memories_fts(rowid, content, summary, topic, entities, keywords)
                VALUES (new.rowid, new.content, new.summary, new.topic, new.entities, new.keywords);
            END
        """)
    
    def search_memories(self, query: str, namespace: str = "default", limit: int = 10):
        """Search memories using full-text search (compatible with Memori interface)"""
        thread_id = namespace  # In our system, namespace is thread_id
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Handle empty or invalid queries
            if not query or not query.strip():
                # Return recent memories for empty query
                cursor = conn.execute("""
                    SELECT *, confidence_score as importance_score
                    FROM memories 
                    WHERE thread_id = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (thread_id, limit))
            else:
                # Use FTS5 for intelligent search
                try:
                    cursor = conn.execute("""
                        SELECT m.*, 
                               rank AS search_rank,
                               m.confidence_score as importance_score
                        FROM memories_fts 
                        JOIN memories m ON memories_fts.rowid = m.rowid
                        WHERE memories_fts MATCH ? AND m.thread_id = ?
                        ORDER BY rank, m.importance DESC, m.created_at DESC
                        LIMIT ?
                    """, (query.strip(), thread_id, limit))
                except sqlite3.OperationalError as e:
                    if "fts5" in str(e).lower():
                        # Fallback to regular search if FTS5 fails
                        cursor = conn.execute("""
                            SELECT *, confidence_score as importance_score
                            FROM memories 
                            WHERE thread_id = ? AND (content LIKE ? OR summary LIKE ?)
                            ORDER BY created_at DESC
                            LIMIT ?
                        """, (thread_id, f"%{query}%", f"%{query}%", limit))
                    else:
                        raise
            
            results = []
            for row in cursor.fetchall():
                result = dict(row)
                result['memory_id'] = result['id']
                results.append(result)
            
            return results
    
    def create_thread(self, thread_id: str, name: str = None, created_by_agent: str = "unknown"):
        """Create a new thread"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO threads 
                (id, name, created_by_agent, last_active_agent)
                VALUES (?, ?, ?, ?)
            """, (thread_id, name or f"Thread {thread_id[:8]}", created_by_agent, created_by_agent))
            
            conn.commit()
    
    def get_thread(self, thread_id: str):
        """Get thread information"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM threads WHERE id = ?", (thread_id,))
            result = cursor.fetchone()
            return dict(result) if result else None
    
    def update_thread_access(self, thread_id: str, agent_name: str):
        """Update thread last access information"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE threads 
                SET last_active_agent = ?, last_accessed = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (agent_name, thread_id))
            conn.commit()


def get_enhanced_db_manager() -> EnhancedDatabaseManager:
    """Get the enhanced database manager instance"""
    return EnhancedDatabaseManager()


# Export for easy import
__all__ = ["EnhancedDatabaseManager", "get_enhanced_db_manager"]
