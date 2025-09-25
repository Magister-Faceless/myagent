"""
LangGraph Configuration Generator - Dynamic generation of langgraph.json.

This module generates the langgraph.json configuration file dynamically
based on registered agents in the agent registry.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List

from config.agent_registry import get_agent_registry, AgentConfig


class LangGraphGenerator:
    """Generator for dynamic langgraph.json configuration."""
    
    def __init__(self, backend_path: str = None):
        """Initialize the generator.
        
        Args:
            backend_path: Path to the backend directory. If None, auto-detected.
        """
        self.backend_path = backend_path or self._detect_backend_path()
        self.langgraph_path = os.path.join(self.backend_path, "langgraph.json")
        self.registry = get_agent_registry()
    
    def _detect_backend_path(self) -> str:
        """Auto-detect the backend directory path."""
        current_file = Path(__file__)
        # Navigate up from utils/ to backend/
        backend_path = current_file.parent.parent
        return str(backend_path)
    
    def generate_agent_module_path(self, agent_id: str) -> str:
        """Generate the module path for an agent.
        
        Args:
            agent_id: The agent ID.
            
        Returns:
            Module path string for the agent.
        """
        # Convert agent-id to agent_id for Python module naming
        module_name = agent_id.replace("-", "_")
        return f"agents.dynamic_agents:{module_name}"
    
    def generate_langgraph_config(self) -> Dict[str, Any]:
        """Generate the complete langgraph.json configuration.
        
        Returns:
            Dictionary containing the langgraph configuration.
        """
        # Get all enabled agents
        agents = self.registry.list_agents(enabled_only=True)
        
        # Generate graphs configuration
        graphs = {}
        for agent in agents:
            graphs[agent.id] = self.generate_agent_module_path(agent.id)
        
        # Base configuration
        config = {
            "dependencies": ["."],
            "graphs": graphs,
            "env": ".env"
        }
        
        return config
    
    def write_langgraph_config(self) -> bool:
        """Write the langgraph.json configuration file.
        
        Returns:
            True if successful, False otherwise.
        """
        try:
            config = self.generate_langgraph_config()
            
            with open(self.langgraph_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            print(f"Generated langgraph.json with {len(config['graphs'])} agents")
            return True
            
        except Exception as e:
            print(f"Error writing langgraph.json: {e}")
            return False
    
    def generate_dynamic_agents_module(self) -> str:
        """Generate the dynamic_agents.py module content.
        
        Returns:
            Python code as string for the dynamic agents module.
        """
        agents = self.registry.list_agents(enabled_only=True)
        
        # Generate imports
        imports = [
            '"""',
            'Dynamic Agents Module - Auto-generated agent instances.',
            '',
            'This module is automatically generated based on the agent registry.',
            'Do not modify this file manually.',
            '"""',
            '',
            'from agents.agent_factory import create_agent_by_id',
            ''
        ]
        
        # Generate agent instances
        agent_instances = []
        for agent in agents:
            # Convert agent-id to valid Python variable name
            var_name = agent.id.replace("-", "_")
            agent_instances.extend([
                f'# {agent.name} - {agent.description}',
                f'{var_name} = create_agent_by_id("{agent.id}")',
                ''
            ])
        
        return '\n'.join(imports + agent_instances)
    
    def write_dynamic_agents_module(self) -> bool:
        """Write the dynamic_agents.py module file.
        
        Returns:
            True if successful, False otherwise.
        """
        try:
            module_content = self.generate_dynamic_agents_module()
            module_path = os.path.join(self.backend_path, "agents", "dynamic_agents.py")
            
            # Ensure agents directory exists
            os.makedirs(os.path.dirname(module_path), exist_ok=True)
            
            with open(module_path, 'w') as f:
                f.write(module_content)
            
            print(f"Generated dynamic_agents.py module")
            return True
            
        except Exception as e:
            print(f"Error writing dynamic_agents.py: {e}")
            return False
    
    def regenerate_all(self) -> bool:
        """Regenerate both langgraph.json and dynamic_agents.py.
        
        Returns:
            True if both files were generated successfully, False otherwise.
        """
        success = True
        success &= self.write_dynamic_agents_module()
        success &= self.write_langgraph_config()
        return success
    
    def backup_existing_config(self) -> bool:
        """Create a backup of the existing langgraph.json.
        
        Returns:
            True if backup was created or no file exists, False on error.
        """
        if not os.path.exists(self.langgraph_path):
            return True
        
        try:
            backup_path = f"{self.langgraph_path}.backup"
            with open(self.langgraph_path, 'r') as src:
                with open(backup_path, 'w') as dst:
                    dst.write(src.read())
            print(f"Backed up existing langgraph.json to {backup_path}")
            return True
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False


def generate_langgraph_config(backup_existing: bool = True) -> bool:
    """Convenience function to generate langgraph configuration.
    
    Args:
        backup_existing: Whether to backup existing configuration.
        
    Returns:
        True if generation was successful, False otherwise.
    """
    generator = LangGraphGenerator()
    
    if backup_existing:
        generator.backup_existing_config()
    
    return generator.regenerate_all()


def update_langgraph_for_agent_changes():
    """Update langgraph.json when agent configurations change."""
    return generate_langgraph_config(backup_existing=False)


if __name__ == "__main__":
    # Generate configuration when run directly
    success = generate_langgraph_config()
    if success:
        print("Successfully generated langgraph configuration")
    else:
        print("Failed to generate langgraph configuration")
