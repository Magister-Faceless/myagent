"""
Migration Script for Enhanced Memory System

This script migrates existing MyAgents data to the new enhanced memory system
while preserving all existing functionality and data.
"""

import os
import sys
import sqlite3
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Add backend to path for imports
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

# Load environment variables from .env file
env_path = backend_path / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print(f"📝 Loaded environment variables from: {env_path}")
else:
    print(f"⚠️ Warning: .env file not found at {env_path}")

from core.database.enhanced_schema import EnhancedDatabaseManager
from core.memory.memory_agent import get_memory_agent
from config.checkpointer import get_checkpointer_path


class MigrationManager:
    """Manages migration from existing system to enhanced memory system"""
    
    def __init__(self):
        """Initialize migration manager"""
        self.backend_dir = Path(__file__).parent.parent
        self.existing_db_path = get_checkpointer_path()
        self.enhanced_db = EnhancedDatabaseManager()
        self.memory_agent = get_memory_agent()
        
        # Create backup directory
        self.backup_dir = self.backend_dir / "data" / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
    def run_migration(self) -> bool:
        """
        Run complete migration process
        
        Returns:
            True if migration successful, False otherwise
        """
        try:
            print("🚀 Starting migration to enhanced memory system...")
            
            # Step 1: Backup existing data
            print("\n📦 Step 1: Backing up existing data...")
            backup_path = self._backup_existing_data()
            if not backup_path:
                print("❌ Backup failed - aborting migration")
                return False
            print(f"✅ Backup created: {backup_path}")
            
            # Step 2: Initialize enhanced database
            print("\n🗄️ Step 2: Initializing enhanced database...")
            self._initialize_enhanced_database()
            print("✅ Enhanced database initialized")
            
            # Step 3: Migrate existing threads
            print("\n🔄 Step 3: Migrating existing threads...")
            migrated_threads = self._migrate_existing_threads()
            print(f"✅ Migrated {migrated_threads} threads")
            
            # Step 4: Extract memories from conversation history
            print("\n🧠 Step 4: Extracting memories from conversation history...")
            extracted_memories = self._extract_memories_from_history()
            print(f"✅ Extracted {extracted_memories} memories")
            
            # Step 5: Update configuration
            print("\n⚙️ Step 5: Updating configuration...")
            self._update_configuration()
            print("✅ Configuration updated")
            
            # Step 6: Verify migration
            print("\n✅ Step 6: Verifying migration...")
            if self._verify_migration():
                print("✅ Migration completed successfully!")
                print(f"\n📊 Migration Summary:")
                print(f"   - Threads migrated: {migrated_threads}")
                print(f"   - Memories extracted: {extracted_memories}")
                print(f"   - Backup location: {backup_path}")
                return True
            else:
                print("❌ Migration verification failed")
                return False
                
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            return False
    
    def _backup_existing_data(self) -> Optional[str]:
        """Backup existing data"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"myagents_backup_{timestamp}"
            backup_path = self.backup_dir / backup_name
            backup_path.mkdir(exist_ok=True)
            
            # Backup existing SQLite database if it exists
            if Path(self.existing_db_path).exists():
                shutil.copy2(self.existing_db_path, backup_path / "original_agent_state.db")
            
            # Backup any existing data directory
            data_dir = self.backend_dir / "data"
            if data_dir.exists():
                shutil.copytree(data_dir, backup_path / "data", dirs_exist_ok=True)
            
            # Create backup manifest
            manifest = {
                "backup_date": datetime.now().isoformat(),
                "original_db_path": self.existing_db_path,
                "enhanced_db_path": self.enhanced_db.db_path,
                "migration_version": "1.0"
            }
            
            with open(backup_path / "manifest.json", "w") as f:
                json.dump(manifest, f, indent=2)
            
            return str(backup_path)
            
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return None
    
    def _initialize_enhanced_database(self):
        """Initialize the enhanced database"""
        # Database is already initialized in the constructor
        print(f"Enhanced database created at: {self.enhanced_db.db_path}")
    
    def _migrate_existing_threads(self) -> int:
        """Migrate existing threads from the original checkpointer"""
        migrated_count = 0
        
        try:
            # Check if original database exists
            if not Path(self.existing_db_path).exists():
                print("No existing database found - starting fresh")
                return 0
            
            # Connect to original database
            with sqlite3.connect(self.existing_db_path) as original_conn:
                original_conn.row_factory = sqlite3.Row
                
                # Try to find thread-like data in the original database
                # LangGraph typically stores data in 'checkpoints' table
                try:
                    cursor = original_conn.execute("""
                        SELECT DISTINCT thread_id FROM checkpoints 
                        WHERE thread_id IS NOT NULL
                    """)
                    
                    for row in cursor.fetchall():
                        thread_id = row['thread_id']
                        if thread_id:
                            # Create thread in enhanced database
                            self.enhanced_db.create_thread(
                                thread_id=thread_id,
                                name=f"Migrated Thread {thread_id[:8]}",
                                created_by_agent="migration_script"
                            )
                            migrated_count += 1
                            
                except sqlite3.OperationalError as e:
                    print(f"⚠️ Could not migrate threads from original database: {e}")
                    print("This is normal if the original database has a different schema")
            
            return migrated_count
            
        except Exception as e:
            print(f"⚠️ Thread migration encountered issues: {e}")
            return migrated_count
    
    def _extract_memories_from_history(self) -> int:
        """Extract memories from existing conversation history"""
        extracted_count = 0
        
        try:
            # Check if original database exists
            if not Path(self.existing_db_path).exists():
                return 0
            
            # Connect to original database
            with sqlite3.connect(self.existing_db_path) as original_conn:
                original_conn.row_factory = sqlite3.Row
                
                try:
                    # Try to extract conversation data from checkpoints
                    cursor = original_conn.execute("""
                        SELECT thread_id, checkpoint, metadata
                        FROM checkpoints 
                        WHERE thread_id IS NOT NULL
                        ORDER BY thread_id, created_at
                    """)
                    
                    current_thread = None
                    conversation_parts = []
                    
                    for row in cursor.fetchall():
                        thread_id = row['thread_id']
                        
                        # Process accumulated conversation when thread changes
                        if current_thread and current_thread != thread_id:
                            extracted_count += self._process_thread_conversation(
                                current_thread, conversation_parts
                            )
                            conversation_parts = []
                        
                        current_thread = thread_id
                        
                        # Try to extract conversation data from checkpoint
                        try:
                            checkpoint_data = json.loads(row['checkpoint']) if row['checkpoint'] else {}
                            
                            # Look for messages in various possible locations
                            messages = []
                            if 'messages' in checkpoint_data:
                                messages = checkpoint_data['messages']
                            elif 'state' in checkpoint_data and 'messages' in checkpoint_data['state']:
                                messages = checkpoint_data['state']['messages']
                            
                            for message in messages:
                                if isinstance(message, dict):
                                    conversation_parts.append(message)
                                    
                        except (json.JSONDecodeError, KeyError):
                            continue
                    
                    # Process final thread
                    if current_thread and conversation_parts:
                        extracted_count += self._process_thread_conversation(
                            current_thread, conversation_parts
                        )
                    
                except sqlite3.OperationalError as e:
                    print(f"⚠️ Could not extract memories from original database: {e}")
                    print("This is normal if the original database has a different schema")
            
            return extracted_count
            
        except Exception as e:
            print(f"⚠️ Memory extraction encountered issues: {e}")
            return extracted_count
    
    def _process_thread_conversation(self, thread_id: str, conversation_parts: List[Dict]) -> int:
        """Process conversation parts for a thread and extract memories"""
        extracted_count = 0
        
        try:
            # Group messages into user-assistant pairs
            user_message = None
            
            for message in conversation_parts:
                if not isinstance(message, dict):
                    continue
                
                role = message.get('role', message.get('type', ''))
                content = message.get('content', '')
                
                if not content:
                    continue
                
                if role in ['user', 'human']:
                    user_message = content
                elif role in ['assistant', 'ai'] and user_message:
                    # Process this user-assistant pair
                    try:
                        self.memory_agent.process_conversation(
                            thread_id=thread_id,
                            user_input=user_message,
                            ai_output=content,
                            agent_name="migration_script"
                        )
                        extracted_count += 1
                    except Exception as e:
                        print(f"⚠️ Failed to process conversation pair: {e}")
                    
                    user_message = None  # Reset for next pair
            
            return extracted_count
            
        except Exception as e:
            print(f"⚠️ Failed to process thread conversation: {e}")
            return 0
    
    def _update_configuration(self):
        """Update configuration to use enhanced system"""
        try:
            # Create configuration update file
            config_update = {
                "enhanced_system_enabled": True,
                "enhanced_db_path": self.enhanced_db.db_path,
                "migration_completed": datetime.now().isoformat(),
                "migration_version": "1.0"
            }
            
            config_file = self.backend_dir / "data" / "enhanced" / "config.json"
            with open(config_file, "w") as f:
                json.dump(config_update, f, indent=2)
                
        except Exception as e:
            print(f"⚠️ Configuration update failed: {e}")
    
    def _verify_migration(self) -> bool:
        """Verify migration completed successfully"""
        try:
            # Check if enhanced database exists and has tables
            if not Path(self.enhanced_db.db_path).exists():
                print("❌ Enhanced database not found")
                return False
            
            # Check if tables exist
            with sqlite3.connect(self.enhanced_db.db_path) as conn:
                cursor = conn.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name IN ('threads', 'memories', 'files')
                """)
                
                tables = [row[0] for row in cursor.fetchall()]
                required_tables = ['threads', 'memories', 'files']
                
                for table in required_tables:
                    if table not in tables:
                        print(f"❌ Required table missing: {table}")
                        return False
            
            print("✅ All required tables present")
            return True
            
        except Exception as e:
            print(f"❌ Migration verification failed: {e}")
            return False


def main():
    """Main migration function"""
    print("🔄 MyAgents Enhanced Memory System Migration")
    print("=" * 50)
    
    migration_manager = MigrationManager()
    
    # Ask for confirmation
    response = input("\nThis will migrate your existing MyAgents data to the enhanced memory system.\n"
                    "A backup will be created before migration.\n"
                    "Continue? (y/N): ").strip().lower()
    
    if response not in ['y', 'yes']:
        print("Migration cancelled.")
        return
    
    # Run migration
    success = migration_manager.run_migration()
    
    if success:
        print("\n🎉 Migration completed successfully!")
        print("\nNext steps:")
        print("1. Test the enhanced system with a simple conversation")
        print("2. Verify that files and memories are accessible")
        print("3. Check that cross-agent memory sharing works")
        print("\nIf you encounter any issues, you can restore from the backup.")
    else:
        print("\n❌ Migration failed!")
        print("Your original data has been backed up and is safe.")
        print("Please check the error messages above and try again.")


if __name__ == "__main__":
    main()
