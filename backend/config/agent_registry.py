"""
Agent Registry - Central configuration for multiple deepagents.

This module provides a registry system for managing multiple deepagent configurations,
allowing dynamic creation and management of different agent types.
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import os
from pathlib import Path

from src.deepagents.sub_agent import SubAgent


class AgentType(Enum):
    """Predefined agent types with specific capabilities."""
    GENERAL = "general"
    RESEARCH = "research"
    CODING = "coding"
    ANALYSIS = "analysis"
    CREATIVE = "creative"
    TECHNICAL = "technical"
    MEDICAL_RESEARCH = "medical_research"
    PYTHON_CODING = "python_coding"


@dataclass
class AgentConfig:
    """Configuration for a deepagent instance."""
    
    # Basic identification
    id: str
    name: str
    description: str
    agent_type: AgentType
    
    # Visual configuration
    color: str = "#3B82F6"
    icon: str = "🤖"
    
    # Agent behavior configuration
    instructions: str = ""
    tools: List[str] = field(default_factory=list)
    subagents: List[str] = field(default_factory=list)
    
    # Model configuration
    model_config: Optional[Dict[str, Any]] = None
    
    # Advanced configuration
    recursion_limit: int = 100
    interrupt_config: Optional[Dict[str, Any]] = None
    builtin_tools: Optional[List[str]] = None
    main_agent_tools: Optional[List[str]] = None
    
    # Metadata
    enabled: bool = True
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class AgentRegistry:
    """Registry for managing multiple deepagent configurations."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the agent registry.
        
        Args:
            config_path: Path to the agent configuration file. If None, uses default.
        """
        self.config_path = config_path or self._get_default_config_path()
        self._agents: Dict[str, AgentConfig] = {}
        self._agent_factories: Dict[str, Callable] = {}
        self._load_configurations()
    
    def _get_default_config_path(self) -> str:
        """Get the default configuration file path."""
        backend_dir = Path(__file__).parent.parent
        return str(backend_dir / "config" / "agents.json")
    
    def _load_configurations(self):
        """Load agent configurations from file."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for agent_data in data.get('agents', []):
                        # Convert agent_type string to enum
                        if 'agent_type' in agent_data:
                            agent_data['agent_type'] = AgentType(agent_data['agent_type'])
                        config = AgentConfig(**agent_data)
                        self._agents[config.id] = config
                    print(f"Successfully loaded {len(self._agents)} agent configurations")
            except Exception as e:
                import traceback
                print(f"Warning: Failed to load agent configurations: {e}")
                print(f"Full traceback: {traceback.format_exc()}")
        
        # Ensure we have at least the main agent
        if not self._agents:
            print("No agents loaded, creating default agents...")
            self._create_default_agents()
    
    def _create_default_agents(self):
        """Create default agent configurations."""
        default_agents = [
            AgentConfig(
                id="main-agent",
                name="Main Agent",
                description="General purpose AI agent for complex tasks",
                agent_type=AgentType.GENERAL,
                color="#3B82F6",
                icon="🧠",
                instructions="You are a general-purpose AI agent capable of handling complex tasks.",
                enabled=True
            ),
            AgentConfig(
                id="research-agent",
                name="Research Agent",
                description="Specialized agent for research and data analysis",
                agent_type=AgentType.RESEARCH,
                color="#8B5CF6",
                icon="🔬",
                instructions="You are a research specialist focused on thorough analysis and investigation.",
                enabled=True
            ),
            AgentConfig(
                id="code-assistant",
                name="Code Assistant",
                description="Specialized agent for coding and development tasks",
                agent_type=AgentType.CODING,
                color="#10B981",
                icon="💻",
                instructions="You are a coding specialist focused on software development and programming tasks.",
                enabled=True
            ),
            AgentConfig(
                id="content-creator",
                name="Content Creator",
                description="Agent for writing and content creation tasks",
                agent_type=AgentType.CREATIVE,
                color="#F59E0B",
                icon="✍️",
                instructions="You are a content creation specialist focused on writing and creative tasks.",
                enabled=True
            )
        ]
        
        for agent in default_agents:
            self._agents[agent.id] = agent
        
        self.save_configurations()
    
    def register_agent(self, config: AgentConfig) -> bool:
        """Register a new agent configuration.
        
        Args:
            config: The agent configuration to register.
            
        Returns:
            True if registration was successful, False otherwise.
        """
        if config.id in self._agents:
            return False
        
        self._agents[config.id] = config
        self.save_configurations()
        return True
    
    def update_agent(self, agent_id: str, config: AgentConfig) -> bool:
        """Update an existing agent configuration.
        
        Args:
            agent_id: The ID of the agent to update.
            config: The new configuration.
            
        Returns:
            True if update was successful, False otherwise.
        """
        if agent_id not in self._agents:
            return False
        
        config.id = agent_id  # Ensure ID consistency
        self._agents[agent_id] = config
        self.save_configurations()
        return True
    
    def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent configuration.
        
        Args:
            agent_id: The ID of the agent to unregister.
            
        Returns:
            True if unregistration was successful, False otherwise.
        """
        if agent_id not in self._agents:
            return False
        
        del self._agents[agent_id]
        self.save_configurations()
        return True
    
    def get_agent(self, agent_id: str) -> Optional[AgentConfig]:
        """Get an agent configuration by ID.
        
        Args:
            agent_id: The ID of the agent to retrieve.
            
        Returns:
            The agent configuration if found, None otherwise.
        """
        return self._agents.get(agent_id)
    
    def list_agents(self, enabled_only: bool = True) -> List[AgentConfig]:
        """List all registered agent configurations.
        
        Args:
            enabled_only: If True, only return enabled agents.
            
        Returns:
            List of agent configurations.
        """
        agents = list(self._agents.values())
        if enabled_only:
            agents = [agent for agent in agents if agent.enabled]
        return agents
    
    def get_agent_ids(self, enabled_only: bool = True) -> List[str]:
        """Get list of all agent IDs.
        
        Args:
            enabled_only: If True, only return enabled agent IDs.
            
        Returns:
            List of agent IDs.
        """
        agents = self.list_agents(enabled_only)
        return [agent.id for agent in agents]
    
    def register_factory(self, agent_id: str, factory_func: Callable):
        """Register a factory function for creating an agent instance.
        
        Args:
            agent_id: The ID of the agent.
            factory_func: Function that returns a configured deepagent instance.
        """
        self._agent_factories[agent_id] = factory_func
    
    def get_factory(self, agent_id: str) -> Optional[Callable]:
        """Get the factory function for an agent.
        
        Args:
            agent_id: The ID of the agent.
            
        Returns:
            The factory function if registered, None otherwise.
        """
        return self._agent_factories.get(agent_id)
    
    def save_configurations(self):
        """Save agent configurations to file."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            # Convert to serializable format
            data = {
                "agents": [
                    {
                        "id": agent.id,
                        "name": agent.name,
                        "description": agent.description,
                        "agent_type": agent.agent_type.value,
                        "color": agent.color,
                        "icon": agent.icon,
                        "instructions": agent.instructions,
                        "tools": agent.tools,
                        "subagents": agent.subagents,
                        "model_config": agent.model_config,
                        "recursion_limit": agent.recursion_limit,
                        "interrupt_config": agent.interrupt_config,
                        "builtin_tools": agent.builtin_tools,
                        "main_agent_tools": agent.main_agent_tools,
                        "enabled": agent.enabled,
                        "created_at": agent.created_at,
                        "updated_at": agent.updated_at
                    }
                    for agent in self._agents.values()
                ]
            }
            
            with open(self.config_path, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"Warning: Failed to save agent configurations: {e}")


# Global registry instance
_registry = None

def get_agent_registry() -> AgentRegistry:
    """Get the global agent registry instance."""
    global _registry
    if _registry is None:
        _registry = AgentRegistry()
    return _registry


def register_agent_config(config: AgentConfig) -> bool:
    """Convenience function to register an agent configuration."""
    return get_agent_registry().register_agent(config)


def get_agent_config(agent_id: str) -> Optional[AgentConfig]:
    """Convenience function to get an agent configuration."""
    return get_agent_registry().get_agent(agent_id)


def list_available_agents() -> List[AgentConfig]:
    """Convenience function to list all available agents."""
    return get_agent_registry().list_agents()
