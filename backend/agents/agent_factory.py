"""
Agent Factory - Dynamic creation of deepagents based on configurations.

This module provides factory functions for creating deepagent instances
dynamically based on agent configurations from the registry.
"""

from typing import Dict, List, Optional, Any, Callable
import importlib
import inspect
from pathlib import Path

from src.deepagents import create_deep_agent
from src.deepagents.sub_agent import SubAgent
from config.agent_registry import AgentConfig, AgentType, get_agent_registry
from config.prompts import (
    MAIN_AGENT_INSTRUCTIONS,
    RESEARCH_AGENT_INSTRUCTIONS,
    CODING_AGENT_INSTRUCTIONS,
    CREATIVE_AGENT_INSTRUCTIONS,
    MEDICAL_RESEARCH_INSTRUCTIONS,
    PYTHON_CODING_INSTRUCTIONS
)
from config.settings import get_settings
from config.checkpointer import get_default_checkpointer
from models import get_default_model


class AgentFactory:
    """Factory for creating deepagent instances from configurations."""
    
    def __init__(self):
        """Initialize the agent factory."""
        self.registry = get_agent_registry()
        self._tool_registry: Dict[str, Callable] = {}
        self._subagent_registry: Dict[str, Callable] = {}
        self._initialize_registries()
    
    def _initialize_registries(self):
        """Initialize tool and subagent registries by discovering available components."""
        self._discover_tools()
        self._discover_subagents()
    
    def _discover_tools(self):
        """Discover and register available tools."""
        # Try to import each tool individually to identify specific issues
        tools_to_import = [
            # Search tools
            ("tavily_search", "tools.search.tavily_search", "tavily_search"),
            ("tavily_qna_search", "tools.search.tavily_search", "tavily_qna_search"),
            ("perplexity_reasoning_search", "tools.search.perplexity", "perplexity_reasoning_search"),
            ("perplexity_focused_research", "tools.search.perplexity", "perplexity_focused_research"),
            ("academic_search", "tools.search.perplexity_strategies", "academic_search"),
            ("technical_search", "tools.search.perplexity_strategies", "technical_search"),
            ("market_research", "tools.search.perplexity_strategies", "market_research"),
            ("deep_research", "tools.search.perplexity_strategies", "deep_research"),
            ("sonar_deep_research", "tools.search.sonar_deep_research", "sonar_deep_research"),
            
            # CORE API tools
            ("search_works", "tools.core_api", "search_works"),
            ("scroll_export_works", "tools.core_api", "scroll_export_works"),
            ("get_work_by_id", "tools.core_api", "get_work_by_id"),
            ("batch_get_works_by_ids", "tools.core_api", "batch_get_works_by_ids"),
            ("aggregate_works", "tools.core_api", "aggregate_works"),
            ("time_trend_analysis", "tools.core_api", "time_trend_analysis"),
            ("search_journals", "tools.core_api", "search_journals"),
            ("get_journal_by_id", "tools.core_api", "get_journal_by_id"),
            ("analyze_top_venues_for_topic", "tools.core_api", "analyze_top_venues_for_topic"),
            
            # Utility tools
            ("get_active_subagents", "tools.subagent_tracker", "get_active_subagents"),
            ("get_subagent_summary", "tools.subagent_tracker", "get_subagent_summary"),
            
            # Memory Enhanced Tools
            ("enhanced_write_file", "tools.memory_enhanced_tools", "enhanced_write_file"),
            ("enhanced_read_file", "tools.memory_enhanced_tools", "enhanced_read_file"),
            ("intelligent_file_search", "tools.memory_enhanced_tools", "intelligent_file_search"),
            ("get_thread_memory_context", "tools.memory_enhanced_tools", "get_thread_memory_context"),
            ("get_shared_context_summary", "tools.memory_enhanced_tools", "get_shared_context_summary"),
            ("list_thread_files", "tools.memory_enhanced_tools", "list_thread_files"),
            ("update_file_content", "tools.memory_enhanced_tools", "update_file_content"),
            
            # Literature Review Tools
            ("extract_paper_metadata", "tools.literature.extract_paper_metadata", "extract_paper_metadata"),
            ("generate_prisma_diagram", "tools.literature.generate_prisma_diagram", "generate_prisma_diagram"),
            ("export_citations", "tools.literature.export_citations", "export_citations"),
            ("quality_assessment", "tools.literature.quality_assessment", "quality_assessment"),
        ]
        
        for tool_name, module_path, function_name in tools_to_import:
            try:
                module = importlib.import_module(module_path)
                tool_func = getattr(module, function_name)
                self._tool_registry[tool_name] = tool_func
                print(f"Successfully loaded tool: {tool_name}")
            except ImportError as e:
                print(f"Warning: Could not import tool '{tool_name}' from '{module_path}': {e}")
            except AttributeError as e:
                print(f"Warning: Tool function '{function_name}' not found in '{module_path}': {e}")
            except Exception as e:
                print(f"Warning: Unexpected error loading tool '{tool_name}': {e}")
    
    def _discover_subagents(self):
        """Discover and register available subagent creators."""
        subagents_to_import = [
            ("general_subagent", "subagents.general_agent", "create_general_subagent"),
            ("reasoning_subagent", "subagents.reasoning_agent", "create_reasoning_subagent"),
            ("deep_research_subagent", "subagents.deep_research_agent", "create_deep_research_agent"),
            ("market_analysis_subagent", "subagents.market_analysis_agent", "create_market_analysis_agent"),
            ("technical_research_subagent", "subagents.technical_research_agent", "create_technical_research_agent"),
            
            # Literature Review Subagents
            ("request_validator", "subagents.request_validator", "create_request_validator"),
            ("planning_coordinator", "subagents.planning_coordinator", "create_planning_coordinator"),
            ("literature_screener", "subagents.literature_screener", "create_literature_screener"),
            ("content_analyzer", "subagents.content_analyzer", "create_content_analyzer"),
            ("synthesis_engine", "subagents.synthesis_engine", "create_synthesis_engine"),
        ]
        
        for subagent_name, module_path, function_name in subagents_to_import:
            try:
                module = importlib.import_module(module_path)
                creator_func = getattr(module, function_name)
                self._subagent_registry[subagent_name] = creator_func
                print(f"Successfully loaded subagent creator: {subagent_name}")
            except ImportError as e:
                print(f"Warning: Could not import subagent '{subagent_name}' from '{module_path}': {e}")
            except AttributeError as e:
                print(f"Warning: Subagent creator '{function_name}' not found in '{module_path}': {e}")
            except Exception as e:
                print(f"Warning: Unexpected error loading subagent '{subagent_name}': {e}")
        
        # Special handling for CORE research subagents
        try:
            module = importlib.import_module("subagents.core_research_subagents")
            get_all_core_research_subagents = getattr(module, "get_all_core_research_subagents")
            core_subagents = get_all_core_research_subagents()
            for i, subagent in enumerate(core_subagents):
                self._subagent_registry[f"core_research_subagent_{i}"] = lambda: subagent
            print(f"Successfully loaded {len(core_subagents)} CORE research subagents")
        except Exception as e:
            print(f"Warning: Could not load CORE research subagents: {e}")
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tool names."""
        return list(self._tool_registry.keys())
    
    def get_available_subagents(self) -> List[str]:
        """Get list of available subagent names."""
        return list(self._subagent_registry.keys())
    
    def _get_default_tools_for_type(self, agent_type: AgentType) -> List[str]:
        """Get default tools for a specific agent type."""
        base_tools = [
            "get_active_subagents",
            "get_subagent_summary"
        ]
        
        if agent_type == AgentType.GENERAL:
            return base_tools + [
                "tavily_search",
                "tavily_qna_search",
                "perplexity_reasoning_search",
                "perplexity_focused_research"
            ]
        elif agent_type == AgentType.RESEARCH:
            return base_tools + [
                "academic_search",
                "technical_search",
                "deep_research",
                "sonar_deep_research",
                "search_works",
                "scroll_export_works",
                "get_work_by_id",
                "batch_get_works_by_ids",
                "aggregate_works",
                "time_trend_analysis",
                "search_journals",
                "get_journal_by_id",
                "analyze_top_venues_for_topic"
            ]
        elif agent_type == AgentType.CODING:
            return base_tools + [
                "tavily_search",
                "technical_search",
                "perplexity_focused_research"
            ]
        elif agent_type == AgentType.CREATIVE:
            return base_tools + [
                "tavily_search",
                "perplexity_reasoning_search"
            ]
        elif agent_type == AgentType.MEDICAL_RESEARCH:
            return base_tools + [
                # Medical literature search tools
                "academic_search",
                "deep_research",
                "sonar_deep_research",
                # CORE API tools for medical literature
                "search_works",
                "scroll_export_works", 
                "get_work_by_id",
                "batch_get_works_by_ids",
                "aggregate_works",
                "time_trend_analysis",
                "search_journals",
                "get_journal_by_id",
                "analyze_top_venues_for_topic"
            ]
        elif agent_type == AgentType.PYTHON_CODING:
            return base_tools + [
                # Python-focused development tools
                "tavily_search",
                "technical_search", 
                "perplexity_focused_research"
            ]
        else:
            return base_tools
    
    def _get_default_subagents_for_type(self, agent_type: AgentType) -> List[str]:
        """Get default subagents for a specific agent type."""
        base_subagents = ["general_subagent"]
        
        if agent_type == AgentType.GENERAL:
            return base_subagents + [
                "reasoning_subagent",
                "deep_research_subagent"
            ]
        elif agent_type == AgentType.RESEARCH:
            return base_subagents + [
                "reasoning_subagent",
                "deep_research_subagent",
                "market_analysis_subagent",
                "technical_research_subagent"
            ]
        elif agent_type == AgentType.CODING:
            return base_subagents + [
                "reasoning_subagent",
                "technical_research_subagent"
            ]
        elif agent_type == AgentType.CREATIVE:
            return base_subagents + [
                "reasoning_subagent"
            ]
        elif agent_type == AgentType.MEDICAL_RESEARCH:
            return base_subagents + [
                "reasoning_subagent",
                "deep_research_subagent",
                "technical_research_subagent"
                # Note: CORE research subagents will be added automatically
            ]
        elif agent_type == AgentType.PYTHON_CODING:
            return base_subagents + [
                "reasoning_subagent",
                "technical_research_subagent"
            ]
        else:
            return base_subagents
    
    def _get_default_instructions_for_type(self, agent_type: AgentType) -> str:
        """Get default instructions for a specific agent type."""
        instructions_map = {
            AgentType.GENERAL: MAIN_AGENT_INSTRUCTIONS,
            AgentType.RESEARCH: RESEARCH_AGENT_INSTRUCTIONS,
            AgentType.CODING: CODING_AGENT_INSTRUCTIONS,
            AgentType.CREATIVE: CREATIVE_AGENT_INSTRUCTIONS,
            AgentType.MEDICAL_RESEARCH: MEDICAL_RESEARCH_INSTRUCTIONS,
            AgentType.PYTHON_CODING: PYTHON_CODING_INSTRUCTIONS,
        }
        return instructions_map.get(agent_type, MAIN_AGENT_INSTRUCTIONS)
    
    def create_agent(self, agent_id: str) -> Optional[Any]:
        """Create a deepagent instance from configuration.
        
        Args:
            agent_id: The ID of the agent to create.
            
        Returns:
            Configured deepagent instance or None if creation failed.
        """
        config = self.registry.get_agent(agent_id)
        if not config or not config.enabled:
            return None
        
        try:
            # Get application settings
            settings = get_settings()
            
            # Resolve subagents first so their tool requirements can be included
            subagent_names = config.subagents or self._get_default_subagents_for_type(config.agent_type)
            subagents = []
            subagent_required_tools: set[str] = set()
            for subagent_name in subagent_names:
                if subagent_name in self._subagent_registry:
                    try:
                        subagent = self._subagent_registry[subagent_name]()
                        subagents.append(subagent)

                        # Collect tool requirements from the subagent specification
                        required_tools = []
                        if hasattr(subagent, "tools"):
                            required_tools = getattr(subagent, "tools") or []
                        elif isinstance(subagent, dict):
                            required_tools = subagent.get("tools", []) or []

                        if required_tools:
                            # Some SubAgent implementations use tuples; normalize to list
                            if not isinstance(required_tools, (list, tuple, set)):
                                required_tools = [required_tools]
                            subagent_required_tools.update(required_tools)
                    except Exception as e:
                        print(f"Warning: Failed to create subagent '{subagent_name}': {e}")
                else:
                    print(f"Warning: Subagent '{subagent_name}' not found for agent '{agent_id}'")

            # Resolve tools, augmenting with any subagent requirements
            explicit_tools = config.tools if config.tools else self._get_default_tools_for_type(config.agent_type)
            combined_tool_names = list(dict.fromkeys(list(explicit_tools) + list(subagent_required_tools)))
            tools = []
            missing_tools = []
            for tool_name in combined_tool_names:
                if tool_name in self._tool_registry:
                    tools.append(self._tool_registry[tool_name])
                else:
                    missing_tools.append(tool_name)

            if missing_tools:
                print(f"Warning: Agent '{agent_id}' missing tools: {missing_tools}")
                print(f"Available tools: {list(self._tool_registry.keys())}")
            
            # Get instructions
            instructions = config.instructions or self._get_default_instructions_for_type(config.agent_type)
            
            # Get model configuration
            model = get_default_model()
            if config.model_config:
                # TODO: Implement custom model configuration
                pass
            
            # Get persistent checkpointer for state storage
            checkpointer = get_default_checkpointer()
            
            # Create the agent
            agent = create_deep_agent(
                tools=tools,
                instructions=instructions,
                subagents=subagents,
                model=model,
                checkpointer=checkpointer,
                builtin_tools=config.builtin_tools,
                interrupt_config=config.interrupt_config,
                main_agent_tools=config.main_agent_tools,
            ).with_config({
                "recursion_limit": config.recursion_limit or settings.get("recursion_limit", 100)
            })
            
            return agent
            
        except Exception as e:
            import traceback
            print(f"Error creating agent '{agent_id}': {e}")
            print(f"Full traceback: {traceback.format_exc()}")
            return None
    
    def create_all_agents(self) -> Dict[str, Any]:
        """Create all enabled agents.
        
        Returns:
            Dictionary mapping agent IDs to their instances.
        """
        agents = {}
        for agent_config in self.registry.list_agents(enabled_only=True):
            agent = self.create_agent(agent_config.id)
            if agent:
                agents[agent_config.id] = agent
        return agents
    
    def register_tool(self, name: str, tool_func: Callable):
        """Register a new tool.
        
        Args:
            name: Name of the tool.
            tool_func: The tool function.
        """
        self._tool_registry[name] = tool_func
    
    def register_subagent_creator(self, name: str, creator_func: Callable):
        """Register a new subagent creator.
        
        Args:
            name: Name of the subagent.
            creator_func: Function that creates and returns a SubAgent instance.
        """
        self._subagent_registry[name] = creator_func


# Global factory instance
_factory = None

def get_agent_factory() -> AgentFactory:
    """Get the global agent factory instance."""
    global _factory
    if _factory is None:
        _factory = AgentFactory()
    return _factory


def create_agent_by_id(agent_id: str) -> Optional[Any]:
    """Convenience function to create an agent by ID."""
    return get_agent_factory().create_agent(agent_id)


def create_all_configured_agents() -> Dict[str, Any]:
    """Convenience function to create all configured agents."""
    return get_agent_factory().create_all_agents()
