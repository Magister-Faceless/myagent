"""
API Endpoints for Agent Management.

This module provides FastAPI endpoints for managing multiple deepagents,
allowing the frontend to discover and interact with available agents.
"""

from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import json
from datetime import datetime

from config.agent_registry import (
    get_agent_registry, 
    AgentConfig, 
    AgentType,
    register_agent_config,
    get_agent_config,
    list_available_agents
)
from agents.agent_factory import get_agent_factory, create_agent_by_id
from utils.langgraph_generator import update_langgraph_for_agent_changes


# Pydantic models for API requests/responses
class AgentInfo(BaseModel):
    """Agent information for frontend consumption."""
    id: str
    name: str
    description: str
    agent_type: str
    color: str
    icon: str
    enabled: bool
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class AgentCreateRequest(BaseModel):
    """Request model for creating a new agent."""
    id: str
    name: str
    description: str
    agent_type: str
    color: str = "#3B82F6"
    icon: str = "🤖"
    instructions: str = ""
    tools: List[str] = []
    subagents: List[str] = []
    model_config: Optional[Dict[str, Any]] = None
    recursion_limit: int = 100
    enabled: bool = True


class AgentUpdateRequest(BaseModel):
    """Request model for updating an agent."""
    name: Optional[str] = None
    description: Optional[str] = None
    agent_type: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    instructions: Optional[str] = None
    tools: Optional[List[str]] = None
    subagents: Optional[List[str]] = None
    model_config: Optional[Dict[str, Any]] = None
    recursion_limit: Optional[int] = None
    enabled: Optional[bool] = None


class AgentStatusResponse(BaseModel):
    """Response model for agent status."""
    agent_id: str
    status: str  # "available", "unavailable", "error"
    message: Optional[str] = None
    last_checked: str


class AvailableToolsResponse(BaseModel):
    """Response model for available tools."""
    tools: List[str]
    subagents: List[str]


# Initialize FastAPI app (this would be integrated into main FastAPI app)
app = FastAPI()


def get_registry():
    """Dependency to get agent registry."""
    return get_agent_registry()


def get_factory():
    """Dependency to get agent factory."""
    return get_agent_factory()


@app.get("/agents", response_model=List[AgentInfo])
async def list_agents(
    enabled_only: bool = True,
    registry = Depends(get_registry)
) -> List[AgentInfo]:
    """List all available agents.
    
    Args:
        enabled_only: If True, only return enabled agents.
        
    Returns:
        List of agent information.
    """
    try:
        agents = registry.list_agents(enabled_only=enabled_only)
        return [
            AgentInfo(
                id=agent.id,
                name=agent.name,
                description=agent.description,
                agent_type=agent.agent_type.value,
                color=agent.color,
                icon=agent.icon,
                enabled=agent.enabled,
                created_at=agent.created_at,
                updated_at=agent.updated_at
            )
            for agent in agents
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list agents: {str(e)}")


@app.get("/agents/{agent_id}", response_model=AgentInfo)
async def get_agent(
    agent_id: str,
    registry = Depends(get_registry)
) -> AgentInfo:
    """Get information about a specific agent.
    
    Args:
        agent_id: The ID of the agent to retrieve.
        
    Returns:
        Agent information.
    """
    try:
        agent = registry.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
        
        return AgentInfo(
            id=agent.id,
            name=agent.name,
            description=agent.description,
            agent_type=agent.agent_type.value,
            color=agent.color,
            icon=agent.icon,
            enabled=agent.enabled,
            created_at=agent.created_at,
            updated_at=agent.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get agent: {str(e)}")


@app.post("/agents", response_model=AgentInfo)
async def create_agent(
    request: AgentCreateRequest,
    registry = Depends(get_registry)
) -> AgentInfo:
    """Create a new agent.
    
    Args:
        request: Agent creation request.
        
    Returns:
        Created agent information.
    """
    try:
        # Validate agent type
        try:
            agent_type = AgentType(request.agent_type)
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid agent type: {request.agent_type}"
            )
        
        # Check if agent already exists
        if registry.get_agent(request.id):
            raise HTTPException(
                status_code=409, 
                detail=f"Agent '{request.id}' already exists"
            )
        
        # Create agent configuration
        now = datetime.now().isoformat()
        config = AgentConfig(
            id=request.id,
            name=request.name,
            description=request.description,
            agent_type=agent_type,
            color=request.color,
            icon=request.icon,
            instructions=request.instructions,
            tools=request.tools,
            subagents=request.subagents,
            model_config=request.model_config,
            recursion_limit=request.recursion_limit,
            enabled=request.enabled,
            created_at=now,
            updated_at=now
        )
        
        # Register the agent
        success = registry.register_agent(config)
        if not success:
            raise HTTPException(
                status_code=500, 
                detail="Failed to register agent"
            )
        
        # Update langgraph configuration
        update_langgraph_for_agent_changes()
        
        return AgentInfo(
            id=config.id,
            name=config.name,
            description=config.description,
            agent_type=config.agent_type.value,
            color=config.color,
            icon=config.icon,
            enabled=config.enabled,
            created_at=config.created_at,
            updated_at=config.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create agent: {str(e)}")


@app.put("/agents/{agent_id}", response_model=AgentInfo)
async def update_agent(
    agent_id: str,
    request: AgentUpdateRequest,
    registry = Depends(get_registry)
) -> AgentInfo:
    """Update an existing agent.
    
    Args:
        agent_id: The ID of the agent to update.
        request: Agent update request.
        
    Returns:
        Updated agent information.
    """
    try:
        # Get existing agent
        existing = registry.get_agent(agent_id)
        if not existing:
            raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
        
        # Update fields
        updates = {}
        if request.name is not None:
            updates['name'] = request.name
        if request.description is not None:
            updates['description'] = request.description
        if request.agent_type is not None:
            try:
                updates['agent_type'] = AgentType(request.agent_type)
            except ValueError:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid agent type: {request.agent_type}"
                )
        if request.color is not None:
            updates['color'] = request.color
        if request.icon is not None:
            updates['icon'] = request.icon
        if request.instructions is not None:
            updates['instructions'] = request.instructions
        if request.tools is not None:
            updates['tools'] = request.tools
        if request.subagents is not None:
            updates['subagents'] = request.subagents
        if request.model_config is not None:
            updates['model_config'] = request.model_config
        if request.recursion_limit is not None:
            updates['recursion_limit'] = request.recursion_limit
        if request.enabled is not None:
            updates['enabled'] = request.enabled
        
        # Create updated configuration
        updated_config = AgentConfig(
            id=existing.id,
            name=updates.get('name', existing.name),
            description=updates.get('description', existing.description),
            agent_type=updates.get('agent_type', existing.agent_type),
            color=updates.get('color', existing.color),
            icon=updates.get('icon', existing.icon),
            instructions=updates.get('instructions', existing.instructions),
            tools=updates.get('tools', existing.tools),
            subagents=updates.get('subagents', existing.subagents),
            model_config=updates.get('model_config', existing.model_config),
            recursion_limit=updates.get('recursion_limit', existing.recursion_limit),
            enabled=updates.get('enabled', existing.enabled),
            created_at=existing.created_at,
            updated_at=datetime.now().isoformat()
        )
        
        # Update the agent
        success = registry.update_agent(agent_id, updated_config)
        if not success:
            raise HTTPException(
                status_code=500, 
                detail="Failed to update agent"
            )
        
        # Update langgraph configuration
        update_langgraph_for_agent_changes()
        
        return AgentInfo(
            id=updated_config.id,
            name=updated_config.name,
            description=updated_config.description,
            agent_type=updated_config.agent_type.value,
            color=updated_config.color,
            icon=updated_config.icon,
            enabled=updated_config.enabled,
            created_at=updated_config.created_at,
            updated_at=updated_config.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update agent: {str(e)}")


@app.delete("/agents/{agent_id}")
async def delete_agent(
    agent_id: str,
    registry = Depends(get_registry)
) -> Dict[str, str]:
    """Delete an agent.
    
    Args:
        agent_id: The ID of the agent to delete.
        
    Returns:
        Success message.
    """
    try:
        # Check if agent exists
        if not registry.get_agent(agent_id):
            raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
        
        # Prevent deletion of main agent
        if agent_id == "main-agent":
            raise HTTPException(
                status_code=400, 
                detail="Cannot delete the main agent"
            )
        
        # Delete the agent
        success = registry.unregister_agent(agent_id)
        if not success:
            raise HTTPException(
                status_code=500, 
                detail="Failed to delete agent"
            )
        
        # Update langgraph configuration
        update_langgraph_for_agent_changes()
        
        return {"message": f"Agent '{agent_id}' deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete agent: {str(e)}")


@app.get("/agents/{agent_id}/status", response_model=AgentStatusResponse)
async def get_agent_status(
    agent_id: str,
    factory = Depends(get_factory),
    registry = Depends(get_registry)
) -> AgentStatusResponse:
    """Get the status of an agent.
    
    Args:
        agent_id: The ID of the agent to check.
        
    Returns:
        Agent status information.
    """
    try:
        # Check if agent is registered
        config = registry.get_agent(agent_id)
        if not config:
            return AgentStatusResponse(
                agent_id=agent_id,
                status="unavailable",
                message="Agent not found in registry",
                last_checked=datetime.now().isoformat()
            )
        
        if not config.enabled:
            return AgentStatusResponse(
                agent_id=agent_id,
                status="unavailable",
                message="Agent is disabled",
                last_checked=datetime.now().isoformat()
            )
        
        # Try to create agent instance
        try:
            agent = factory.create_agent(agent_id)
            if agent:
                return AgentStatusResponse(
                    agent_id=agent_id,
                    status="available",
                    message="Agent is ready",
                    last_checked=datetime.now().isoformat()
                )
            else:
                return AgentStatusResponse(
                    agent_id=agent_id,
                    status="error",
                    message="Failed to create agent instance",
                    last_checked=datetime.now().isoformat()
                )
        except Exception as e:
            return AgentStatusResponse(
                agent_id=agent_id,
                status="error",
                message=f"Agent creation error: {str(e)}",
                last_checked=datetime.now().isoformat()
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check agent status: {str(e)}")


@app.get("/tools", response_model=AvailableToolsResponse)
async def get_available_tools(
    factory = Depends(get_factory)
) -> AvailableToolsResponse:
    """Get list of available tools and subagents.
    
    Returns:
        Available tools and subagents.
    """
    try:
        return AvailableToolsResponse(
            tools=factory.get_available_tools(),
            subagents=factory.get_available_subagents()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get available tools: {str(e)}")


@app.post("/regenerate-config")
async def regenerate_langgraph_config() -> Dict[str, str]:
    """Regenerate the langgraph.json configuration.
    
    Returns:
        Success message.
    """
    try:
        success = update_langgraph_for_agent_changes()
        if success:
            return {"message": "LangGraph configuration regenerated successfully"}
        else:
            raise HTTPException(
                status_code=500, 
                detail="Failed to regenerate configuration"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to regenerate config: {str(e)}")


# Health check endpoint
@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint.
    
    Returns:
        Health status.
    """
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}
