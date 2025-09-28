"""
Memory-Enhanced Tools for MyAgents

These tools integrate with the memory system to provide intelligent file management,
context retrieval, and cross-agent collaboration capabilities.
"""

import os
from typing import Dict, List, Optional, Any
from langchain_core.tools import tool

from core.storage.enhanced_file_manager import get_enhanced_file_manager
from core.memory.cross_agent_manager import get_cross_agent_manager
from core.memory.search_engine import get_search_engine


@tool
def enhanced_write_file(
    path: str, 
    content: str, 
    thread_id: str,
    agent_name: str = "unknown",
    file_type: str = "generated"
) -> str:
    """
    Write file with automatic memory creation and intelligent storage
    
    Args:
        path: File path/name
        content: File content
        thread_id: Thread ID for context
        agent_name: Agent creating the file
        file_type: Type of file (generated, upload, export)
        
    Returns:
        Success message with file details
    """
    try:
        file_manager = get_enhanced_file_manager(thread_id)
        
        result = file_manager.store_file_with_memory(
            content=content,
            filename=path,
            file_type=file_type,
            agent_name=agent_name
        )
        
        return f"✅ File created: {path}\n" \
               f"Storage: {result['storage_type']}\n" \
               f"Size: {result['size_bytes']} bytes\n" \
               f"Memory ID: {result['memory_id']}\n" \
               f"File ID: {result['file_id']}"
        
    except Exception as e:
        return f"❌ Error writing file {path}: {str(e)}"


@tool
def enhanced_read_file(
    file_path: str,
    thread_id: str,
    agent_name: str = "unknown"
) -> str:
    """
    Read file content with memory context tracking
    
    Args:
        file_path: Path to the file or file ID
        thread_id: Thread ID for context
        agent_name: Agent reading the file
        
    Returns:
        File content or error message
    """
    try:
        file_manager = get_enhanced_file_manager(thread_id)
        cross_agent_manager = get_cross_agent_manager(thread_id)
        
        # Record the file access
        cross_agent_manager.record_agent_interaction(
            source_agent=agent_name,
            interaction_type="file_read",
            context={"file_path": file_path}
        )
        
        # Try to get file by ID first, then by filename
        content = None
        if len(file_path) == 36 and "-" in file_path:  # Looks like UUID
            content = file_manager.get_file_content(file_path)
        
        if content is None:
            # Search for file by name
            files = file_manager.list_files()
            for file_info in files:
                if file_info['filename'] == file_path:
                    content = file_manager.get_file_content(file_info['id'])
                    break
        
        if content is None:
            return f"❌ File not found: {file_path}"
        
        # Decode content if it's bytes
        if isinstance(content, bytes):
            try:
                content = content.decode('utf-8')
            except UnicodeDecodeError:
                return f"❌ Cannot read binary file: {file_path}"
        
        return content
        
    except Exception as e:
        return f"❌ Error reading file {file_path}: {str(e)}"


@tool
def intelligent_file_search(
    query: str,
    thread_id: str,
    agent_name: str = "unknown",
    limit: int = 5
) -> str:
    """
    Search files using AI-powered memory search
    
    Args:
        query: Search query describing what to look for
        thread_id: Thread ID for context
        agent_name: Agent performing the search
        limit: Maximum number of results
        
    Returns:
        Formatted search results
    """
    try:
        file_manager = get_enhanced_file_manager(thread_id)
        cross_agent_manager = get_cross_agent_manager(thread_id)
        
        # Record the search interaction
        cross_agent_manager.record_agent_interaction(
            source_agent=agent_name,
            interaction_type="file_search",
            context={"query": query, "limit": limit}
        )
        
        # Execute intelligent search
        results = file_manager.search_files_by_content(query, limit)
        
        if not results:
            return f"🔍 No files found matching: '{query}'"
        
        # Format results
        response_parts = [f"🔍 Found {len(results)} files matching '{query}':\n"]
        
        for i, result in enumerate(results, 1):
            filename = result.get('filename', 'Unknown')
            file_type = result.get('file_type', 'unknown')
            size = result.get('size_bytes', 0)
            created_by = result.get('created_by_agent', 'unknown')
            memory_context = result.get('memory_context', '')
            
            # Format file size
            if size < 1024:
                size_str = f"{size} B"
            elif size < 1024 * 1024:
                size_str = f"{size/1024:.1f} KB"
            else:
                size_str = f"{size/(1024*1024):.1f} MB"
            
            response_parts.append(
                f"{i}. **{filename}** ({file_type})\n"
                f"   Size: {size_str} | Created by: {created_by}\n"
                f"   Context: {memory_context[:100]}{'...' if len(memory_context) > 100 else ''}\n"
            )
        
        return "\n".join(response_parts)
        
    except Exception as e:
        return f"❌ File search failed: {str(e)}"


@tool
def get_thread_memory_context(
    query: str,
    thread_id: str,
    agent_name: str = "unknown",
    context_type: str = "general"
) -> str:
    """
    Get relevant context from thread memory
    
    Args:
        query: What to search for in memory
        thread_id: Thread ID for context
        agent_name: Agent requesting context
        context_type: Type of context (general, files, decisions, important)
        
    Returns:
        Formatted memory context
    """
    try:
        cross_agent_manager = get_cross_agent_manager(thread_id)
        
        # Search thread memory
        results = cross_agent_manager.search_thread_memory(
            query=query,
            requesting_agent=agent_name,
            search_type=context_type,
            limit=5
        )
        
        if not results:
            return f"🧠 No relevant context found for: '{query}'"
        
        # Format results
        response_parts = [f"🧠 Found {len(results)} relevant memories for '{query}':\n"]
        
        for i, memory in enumerate(results, 1):
            summary = memory.get('summary', memory.get('content', '')[:100])
            importance = memory.get('importance', 'medium')
            classification = memory.get('classification', 'unknown')
            created_by = memory.get('created_by_agent', 'unknown')
            
            # Add importance indicator
            importance_icon = {
                'critical': '🔴',
                'high': '🟡', 
                'medium': '🟢',
                'low': '⚪'
            }.get(importance, '⚪')
            
            response_parts.append(
                f"{i}. {importance_icon} **{classification.title()}** (by {created_by})\n"
                f"   {summary}{'...' if len(summary) == 100 else ''}\n"
            )
        
        return "\n".join(response_parts)
        
    except Exception as e:
        return f"❌ Memory search failed: {str(e)}"


@tool
def get_shared_context_summary(
    thread_id: str,
    agent_name: str = "unknown"
) -> str:
    """
    Get a comprehensive summary of shared context in the thread
    
    Args:
        thread_id: Thread ID for context
        agent_name: Agent requesting the summary
        
    Returns:
        Formatted context summary
    """
    try:
        cross_agent_manager = get_cross_agent_manager(thread_id)
        
        # Get comprehensive context summary
        summary = cross_agent_manager.get_shared_context_summary(agent_name)
        
        return f"📋 **Thread Context Summary**\n\n{summary}"
        
    except Exception as e:
        return f"❌ Failed to get context summary: {str(e)}"


@tool
def list_thread_files(
    thread_id: str,
    agent_name: str = "unknown",
    file_type: Optional[str] = None,
    limit: int = 10
) -> str:
    """
    List files in the current thread
    
    Args:
        thread_id: Thread ID for context
        agent_name: Agent requesting the list
        file_type: Filter by file type (upload, generated, export)
        limit: Maximum number of files to list
        
    Returns:
        Formatted file list
    """
    try:
        file_manager = get_enhanced_file_manager(thread_id)
        cross_agent_manager = get_cross_agent_manager(thread_id)
        
        # Record the interaction
        cross_agent_manager.record_agent_interaction(
            source_agent=agent_name,
            interaction_type="file_list",
            context={"file_type": file_type, "limit": limit}
        )
        
        # Get file list
        files = file_manager.list_files(file_type, limit)
        
        if not files:
            filter_text = f" ({file_type})" if file_type else ""
            return f"📁 No files found in thread{filter_text}"
        
        # Format file list
        response_parts = [f"📁 **Thread Files** ({len(files)} files):\n"]
        
        for i, file_info in enumerate(files, 1):
            filename = file_info.get('filename', 'Unknown')
            ftype = file_info.get('file_type', 'unknown')
            size = file_info.get('size_bytes', 0)
            created_by = file_info.get('created_by_agent', 'unknown')
            created_at = file_info.get('created_at', '')
            
            # Format file size
            if size < 1024:
                size_str = f"{size} B"
            elif size < 1024 * 1024:
                size_str = f"{size/1024:.1f} KB"
            else:
                size_str = f"{size/(1024*1024):.1f} MB"
            
            # Format date
            try:
                from datetime import datetime
                date_obj = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                date_str = date_obj.strftime('%Y-%m-%d %H:%M')
            except:
                date_str = created_at[:16] if created_at else 'Unknown'
            
            response_parts.append(
                f"{i}. **{filename}** ({ftype})\n"
                f"   Size: {size_str} | By: {created_by} | {date_str}\n"
            )
        
        return "\n".join(response_parts)
        
    except Exception as e:
        return f"❌ Failed to list files: {str(e)}"


@tool
def update_file_content(
    file_path: str,
    new_content: str,
    thread_id: str,
    agent_name: str = "unknown",
    change_description: str = "File updated"
) -> str:
    """
    Update file content and create a new version
    
    Args:
        file_path: File path or file ID
        new_content: New file content
        thread_id: Thread ID for context
        agent_name: Agent making the update
        change_description: Description of changes made
        
    Returns:
        Success message or error
    """
    try:
        file_manager = get_enhanced_file_manager(thread_id)
        
        # Find file ID if path is provided
        file_id = file_path
        if len(file_path) != 36 or "-" not in file_path:  # Not a UUID
            files = file_manager.list_files()
            file_id = None
            for file_info in files:
                if file_info['filename'] == file_path:
                    file_id = file_info['id']
                    break
            
            if file_id is None:
                return f"❌ File not found: {file_path}"
        
        # Update the file
        success = file_manager.update_file(
            file_id=file_id,
            new_content=new_content,
            modified_by=agent_name,
            change_description=change_description
        )
        
        if success:
            return f"✅ File updated successfully: {file_path}\n" \
                   f"Change: {change_description}\n" \
                   f"Updated by: {agent_name}"
        else:
            return f"❌ Failed to update file: {file_path}"
        
    except Exception as e:
        return f"❌ Error updating file: {str(e)}"


# Export all tools for easy import
MEMORY_ENHANCED_TOOLS = [
    enhanced_write_file,
    enhanced_read_file,
    intelligent_file_search,
    get_thread_memory_context,
    get_shared_context_summary,
    list_thread_files,
    update_file_content
]

__all__ = [
    "enhanced_write_file",
    "enhanced_read_file", 
    "intelligent_file_search",
    "get_thread_memory_context",
    "get_shared_context_summary",
    "list_thread_files",
    "update_file_content",
    "MEMORY_ENHANCED_TOOLS"
]
