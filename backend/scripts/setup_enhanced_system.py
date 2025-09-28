"""
Setup Script for Enhanced Memory System

This script sets up the enhanced memory system for new installations
and provides utilities for system management.
"""

import os
import sys
from pathlib import Path
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
from core.memory.search_engine import get_search_engine
from core.storage.enhanced_file_manager import get_enhanced_file_manager


def setup_enhanced_system():
    """Set up the enhanced memory system"""
    
    print("🚀 Setting up MyAgents Enhanced Memory System")
    print("=" * 50)
    
    try:
        # Step 1: Initialize enhanced database
        print("\n📊 Step 1: Initializing enhanced database...")
        db_manager = EnhancedDatabaseManager()
        print(f"✅ Enhanced database initialized: {db_manager.db_path}")
        
        # Step 2: Test memory agent
        print("\n🧠 Step 2: Testing memory agent...")
        memory_agent = get_memory_agent()
        
        # Create a test memory
        test_memory = memory_agent.process_conversation(
            thread_id="setup_test",
            user_input="Setting up enhanced memory system",
            ai_output="Enhanced memory system setup completed successfully. The system now supports intelligent memory processing, cross-agent collaboration, and enhanced file management.",
            agent_name="setup_script"
        )
        print(f"✅ Memory agent working - created test memory: {test_memory.id}")
        
        # Step 3: Test search engine
        print("\n🔍 Step 3: Testing search engine...")
        search_engine = get_search_engine()
        
        # Test search
        search_results = search_engine.search_memories(
            query="setup",
            thread_id="setup_test",
            agent_name="setup_script"
        )
        print(f"✅ Search engine working - found {len(search_results)} results")
        
        # Step 4: Test file manager
        print("\n📁 Step 4: Testing file manager...")
        file_manager = get_enhanced_file_manager("setup_test")
        
        # Create a test file
        test_file_result = file_manager.store_file_with_memory(
            content="# Enhanced Memory System Setup\n\nThis is a test file created during setup.",
            filename="setup_test.md",
            file_type="generated",
            agent_name="setup_script"
        )
        print(f"✅ File manager working - created test file: {test_file_result['file_id']}")
        
        # Step 5: Verify system integration
        print("\n🔗 Step 5: Verifying system integration...")
        
        # Test file search
        file_search_results = file_manager.search_files_by_content("setup test")
        print(f"✅ File search working - found {len(file_search_results)} files")
        
        # Test memory search for files
        memory_search_results = search_engine.search_memories(
            query="test file setup",
            thread_id="setup_test",
            agent_name="setup_script"
        )
        print(f"✅ Memory-file integration working - found {len(memory_search_results)} related memories")
        
        print("\n🎉 Enhanced Memory System Setup Complete!")
        print("\n📋 System Summary:")
        print(f"   - Database: {db_manager.db_path}")
        print(f"   - Test thread: setup_test")
        print(f"   - Test memory: {test_memory.id}")
        print(f"   - Test file: {test_file_result['file_id']}")
        
        print("\n✨ Next Steps:")
        print("1. Run the migration script if you have existing data:")
        print("   python scripts/migrate_to_enhanced_system.py")
        print("2. Update your agent configurations to use enhanced agents")
        print("3. Test the system with a real conversation")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure all dependencies are installed")
        print("2. Check that the backend directory structure is correct")
        print("3. Verify that the models are properly configured")
        return False


def test_system():
    """Test the enhanced system functionality"""
    
    print("🧪 Testing Enhanced Memory System")
    print("=" * 40)
    
    try:
        # Test database connection
        print("\n📊 Testing database connection...")
        db_manager = EnhancedDatabaseManager()
        
        # Test thread creation
        test_thread_id = "test_system_functionality"
        db_manager.create_thread(test_thread_id, "System Test Thread", "test_script")
        print("✅ Database connection working")
        
        # Test memory processing
        print("\n🧠 Testing memory processing...")
        memory_agent = get_memory_agent()
        
        memory = memory_agent.process_conversation(
            thread_id=test_thread_id,
            user_input="Can you help me test the enhanced memory system?",
            ai_output="I'll help you test the enhanced memory system. The system includes intelligent memory processing, cross-agent collaboration, and enhanced file management capabilities.",
            agent_name="test_script"
        )
        print(f"✅ Memory processing working - ID: {memory.id}")
        
        # Test memory search
        print("\n🔍 Testing memory search...")
        search_engine = get_search_engine()
        
        results = search_engine.search_memories(
            query="enhanced memory system test",
            thread_id=test_thread_id,
            agent_name="test_script"
        )
        print(f"✅ Memory search working - found {len(results)} results")
        
        # Test file operations
        print("\n📁 Testing file operations...")
        file_manager = get_enhanced_file_manager(test_thread_id)
        
        # Create test file
        file_result = file_manager.store_file_with_memory(
            content="# System Test Results\n\nAll systems are functioning correctly.",
            filename="system_test_results.md",
            file_type="generated",
            agent_name="test_script"
        )
        print(f"✅ File creation working - ID: {file_result['file_id']}")
        
        # Test file search
        file_search_results = file_manager.search_files_by_content("system test")
        print(f"✅ File search working - found {len(file_search_results)} files")
        
        # Test cross-agent memory manager
        print("\n🤝 Testing cross-agent collaboration...")
        from core.memory.cross_agent_manager import get_cross_agent_manager
        
        cross_agent_manager = get_cross_agent_manager(test_thread_id)
        context = cross_agent_manager.get_thread_context("test_script")
        print(f"✅ Cross-agent collaboration working - context keys: {list(context.keys())}")
        
        print("\n🎉 All tests passed! Enhanced Memory System is working correctly.")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False


def clean_test_data():
    """Clean up test data created during setup and testing"""
    
    print("🧹 Cleaning up test data...")
    
    try:
        import sqlite3
        from core.database.enhanced_schema import get_enhanced_db_manager
        
        db_manager = get_enhanced_db_manager()
        
        # Remove test threads and related data
        test_thread_ids = ["setup_test", "test_system_functionality"]
        
        with sqlite3.connect(db_manager.db_path) as conn:
            for thread_id in test_thread_ids:
                # Delete files
                conn.execute("DELETE FROM files WHERE thread_id = ?", (thread_id,))
                # Delete memories
                conn.execute("DELETE FROM memories WHERE thread_id = ?", (thread_id,))
                # Delete agent interactions
                conn.execute("DELETE FROM agent_interactions WHERE thread_id = ?", (thread_id,))
                # Delete threads
                conn.execute("DELETE FROM threads WHERE id = ?", (thread_id,))
            
            conn.commit()
        
        print("✅ Test data cleaned up successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to clean test data: {e}")
        return False


def main():
    """Main setup function"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="MyAgents Enhanced Memory System Setup")
    parser.add_argument("--setup", action="store_true", help="Set up the enhanced system")
    parser.add_argument("--test", action="store_true", help="Test system functionality")
    parser.add_argument("--clean", action="store_true", help="Clean up test data")
    
    args = parser.parse_args()
    
    if args.setup:
        success = setup_enhanced_system()
        sys.exit(0 if success else 1)
    elif args.test:
        success = test_system()
        sys.exit(0 if success else 1)
    elif args.clean:
        success = clean_test_data()
        sys.exit(0 if success else 1)
    else:
        # Default: run setup
        print("MyAgents Enhanced Memory System Setup")
        print("Usage:")
        print("  python setup_enhanced_system.py --setup   # Set up the system")
        print("  python setup_enhanced_system.py --test    # Test functionality")
        print("  python setup_enhanced_system.py --clean   # Clean test data")
        print("\nRunning setup by default...")
        success = setup_enhanced_system()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
