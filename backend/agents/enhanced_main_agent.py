"""
Enhanced Main Agent with Memory System Integration

This is the enhanced version of the main agent that integrates with the new
memory system for intelligent context management and cross-agent collaboration.
"""

import os
from typing import Literal, Any
from src.deepagents import create_deep_agent
from src.deepagents.sub_agent import SubAgent

# Import enhanced tools
from tools.memory_enhanced_tools import MEMORY_ENHANCED_TOOLS

# Import existing tools from the tools module
from tools.search.tavily_search import tavily_search, tavily_qna_search
from tools.search.perplexity import perplexity_reasoning_search, perplexity_focused_research
from tools.search.perplexity_strategies import academic_search, technical_search, market_research, deep_research
from tools.search.sonar_deep_research import sonar_deep_research

# Import CORE API tools
from tools.core_api import (
    search_works, 
    scroll_export_works,
    get_work_by_id, 
    batch_get_works_by_ids,
    aggregate_works, 
    time_trend_analysis,
    search_journals, 
    get_journal_by_id,
    analyze_top_venues_for_topic
)

# Import utility tools
from tools.subagent_tracker import get_active_subagents, get_subagent_summary
from tools.operation_monitor import check_operation_status, suggest_alternatives

# Import subagent creators
from subagents.general_agent import create_general_subagent
from subagents.reasoning_agent import create_reasoning_subagent
from subagents.deep_research_agent import create_deep_research_agent
from subagents.market_analysis_agent import create_market_analysis_agent
from subagents.technical_research_agent import create_technical_research_agent

# Import CORE API research subagents
from subagents.core_research_subagents import get_all_core_research_subagents

# Import configuration
from config.prompts import ENHANCED_MAIN_AGENT_INSTRUCTIONS
from config.settings import get_settings

# Import model configuration
from models import get_default_model

# Import checkpointer configuration
from config.checkpointer import get_default_checkpointer

# Utilities
from utils.subagent_tracking import enable_subagent_tracking

# Import memory system components
from core.memory.memory_agent import get_memory_agent
from core.memory.cross_agent_manager import get_cross_agent_manager


def create_enhanced_main_agent():
    """Create and configure the enhanced main deep agent with memory integration"""
    
    # Get application settings
    settings = get_settings()
    
    # Create subagents
    general_subagent = create_general_subagent()
    reasoning_subagent = create_reasoning_subagent()
    deep_research_subagent = create_deep_research_agent()
    market_analysis_subagent = create_market_analysis_agent()
    technical_research_subagent = create_technical_research_agent()
    
    # Get all CORE API research subagents
    core_research_subagents = get_all_core_research_subagents()
    
    # Get the default model with fallback
    model = get_default_model()
    
    # Get persistent checkpointer for state storage
    checkpointer = get_default_checkpointer()
    
    # Combine all tools: enhanced memory tools + existing tools
    all_tools = MEMORY_ENHANCED_TOOLS + [
        # General search tools
        tavily_search,
        tavily_qna_search,
        # Perplexity reasoning tools
        perplexity_reasoning_search,
        perplexity_focused_research,
        # Specialized research strategy tools
        academic_search,
        technical_search,
        market_research,
        deep_research,
        # Elite sonar deep research tool
        sonar_deep_research,
        # CORE API tools for scientific research
        search_works,
        scroll_export_works,
        get_work_by_id,
        batch_get_works_by_ids,
        aggregate_works,
        time_trend_analysis,
        search_journals,
        get_journal_by_id,
        analyze_top_venues_for_topic,
        # Utility tools for task and subagent management
        get_active_subagents,
        get_subagent_summary,
        # Operation monitoring and error handling tools
        check_operation_status,
        suggest_alternatives,
    ]
    
    # Create the enhanced main deep agent with human-in-the-loop for high-cost operations
    with enable_subagent_tracking():
        agent = create_deep_agent(
            tools=all_tools,
            instructions=ENHANCED_MAIN_AGENT_INSTRUCTIONS,
            subagents=[
                general_subagent,
                reasoning_subagent,
                deep_research_subagent,
                market_analysis_subagent,
                technical_research_subagent,
            ]
            + core_research_subagents,
            model=model,
            checkpointer=checkpointer,
            # Configure human-in-the-loop for task spawning when using sonar-deep-research agent
            interrupt_config={
                "sonar_deep_research": {
                    "allow_ignore": False,
                    "allow_respond": True,
                    "allow_edit": True,
                    "allow_accept": True,
                }
            },
        ).with_config({"recursion_limit": settings["recursion_limit"]})
    
    # Add memory processing hook
    original_invoke = agent.invoke
    
    def enhanced_invoke(input_data, config=None):
        """Enhanced invoke with automatic memory processing"""
        try:
            # Get thread ID from config
            thread_id = None
            if config and "configurable" in config:
                thread_id = config["configurable"].get("thread_id")
            
            # Call original invoke
            result = original_invoke(input_data, config)
            
            # Process conversation for memory if we have thread context
            if thread_id and isinstance(input_data, dict):
                try:
                    user_input = ""
                    ai_output = ""
                    
                    # Extract user input
                    if "messages" in input_data:
                        messages = input_data["messages"]
                        if messages and isinstance(messages[-1], dict):
                            user_input = messages[-1].get("content", "")
                    elif "input" in input_data:
                        user_input = str(input_data["input"])
                    
                    # Extract AI output
                    if isinstance(result, dict) and "messages" in result:
                        ai_messages = result["messages"]
                        if ai_messages and isinstance(ai_messages[-1], dict):
                            ai_output = ai_messages[-1].get("content", "")
                    elif hasattr(result, 'content'):
                        ai_output = result.content
                    else:
                        ai_output = str(result)
                    
                    # Process conversation for memory
                    if user_input and ai_output:
                        memory_agent.process_conversation(
                            thread_id=thread_id,
                            user_input=user_input,
                            ai_output=ai_output,
                            agent_name="enhanced_main_agent"
                        )
                        
                        # Update cross-agent manager
                        cross_agent_manager = get_cross_agent_manager(thread_id)
                        cross_agent_manager.record_agent_interaction(
                            source_agent="enhanced_main_agent",
                            interaction_type="conversation",
                            context={"user_input_length": len(user_input)},
                            result={"ai_output_length": len(ai_output)}
                        )
                        
                except Exception as e:
                    print(f"⚠️ Memory processing failed: {e}")
                    # Don't fail the main operation if memory processing fails
            
            return result
            
        except Exception as e:
            print(f"❌ Enhanced invoke failed: {e}")
            # Fallback to original invoke
            return original_invoke(input_data, config)
    
    # Replace invoke method
    agent.invoke = enhanced_invoke
    
    return agent


# Create the enhanced agent instance for LangGraph
agent = create_enhanced_main_agent()

# Export for easy import
__all__ = ["create_enhanced_main_agent", "agent"]
