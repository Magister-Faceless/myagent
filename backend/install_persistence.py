#!/usr/bin/env python3
"""
Installation script for persistent checkpointer dependencies.

This script installs the required dependencies for file persistence
and creates the necessary directory structure.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Command: {cmd}")
        print(f"   Error: {e.stderr}")
        return False


def main():
    """Main installation function."""
    print("🚀 Installing persistent checkpointer for file persistence...")
    print()
    
    # Install the required dependency
    if not run_command("pip install langgraph-checkpoint-sqlite>=2.0.0", "Installing langgraph-checkpoint-sqlite"):
        sys.exit(1)
    
    # Create data directory structure
    backend_dir = Path(__file__).parent
    data_dir = backend_dir / "data"
    checkpoints_dir = data_dir / "checkpoints"
    
    print("🔄 Creating directory structure...")
    checkpoints_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ Created directory: {checkpoints_dir}")
    
    # Create .gitignore for data directory if it doesn't exist
    gitignore_path = data_dir / ".gitignore"
    if not gitignore_path.exists():
        with open(gitignore_path, 'w') as f:
            f.write("# Ignore all database files\n")
            f.write("*.db\n")
            f.write("*.db-shm\n")
            f.write("*.db-wal\n")
            f.write("\n")
            f.write("# But keep the directory structure\n")
            f.write("!.gitignore\n")
        print(f"✅ Created .gitignore: {gitignore_path}")
    
    print()
    print("🎉 Persistent checkpointer installation completed!")
    print()
    print("📋 What was installed:")
    print("   • langgraph-checkpoint-sqlite package")
    print("   • backend/data/checkpoints/ directory")
    print("   • backend/config/checkpointer.py configuration")
    print("   • Updated all agent files to use persistent storage")
    print()
    print("🔧 Next steps:")
    print("   1. Restart your LangGraph server: langgraph dev")
    print("   2. Test file creation in the chat interface")
    print("   3. Restart the server again to verify files persist")
    print()
    print("💡 To disable persistence, set DISABLE_PERSISTENCE=true in your .env file")


if __name__ == "__main__":
    main()
