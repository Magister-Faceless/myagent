"""
Request Validator Subagent - DeepAgents v1.1 Implementation

Validates if user requests are appropriate for literature review and provides
recommendations for proceeding or redirecting to other agents.
Uses Grok-4-Fast model for fast validation and reasoning.
"""

from src.deepagents.sub_agent import SubAgent
from typing import Dict, Any, List
import json
from datetime import datetime

# Import prompts
from config.prompts import REQUEST_VALIDATOR_PROMPT
from models import get_default_model


# Helper functions for the subagent (not exposed as tools)
def _validate_literature_review_request(
    user_request: str,
    context: str = ""
) -> Dict[str, Any]:
    """
    Validate if a user request is appropriate for literature review.
    
    Args:
        user_request: The user's original request
        context: Additional context about the request
        
    Returns:
        Dictionary with validation results and recommendations
    """
    try:
        # Analyze request for literature review appropriateness
        validation_result = {
            "is_appropriate": True,
            "confidence": 0.9,
            "reasoning": "",
            "recommendations": [],
            "redirect_suggestions": [],
            "scope_assessment": {},
            "timestamp": datetime.now().isoformat()
        }
        
        # Keywords that indicate literature review appropriateness
        positive_indicators = [
            "literature review", "systematic review", "meta-analysis",
            "research synthesis", "evidence synthesis", "scoping review",
            "narrative review", "bibliometric analysis", "research trends",
            "state of the art", "research gaps", "evidence base"
        ]
        
        # Keywords that might indicate other agent types
        redirect_indicators = {
            "coding": ["code", "programming", "debug", "implement", "software"],
            "creative": ["write", "story", "creative", "poem", "fiction"],
            "general": ["calculate", "math", "solve", "explain", "define"]
        }
        
        request_lower = user_request.lower()
        
        # Check for positive indicators
        positive_matches = [ind for ind in positive_indicators if ind in request_lower]
        
        # Check for redirect indicators
        redirect_matches = {}
        for agent_type, keywords in redirect_indicators.items():
            matches = [kw for kw in keywords if kw in request_lower]
            if matches:
                redirect_matches[agent_type] = matches
        
        # Assess appropriateness
        if positive_matches:
            validation_result["is_appropriate"] = True
            validation_result["confidence"] = min(0.95, 0.7 + len(positive_matches) * 0.1)
            validation_result["reasoning"] = f"Request contains literature review indicators: {', '.join(positive_matches)}"
            validation_result["recommendations"] = [
                "Proceed with literature review workflow",
                "Create structured research plan",
                "Define clear research question and scope"
            ]
        elif redirect_matches:
            validation_result["is_appropriate"] = False
            validation_result["confidence"] = 0.8
            validation_result["reasoning"] = f"Request appears more suitable for other agents: {redirect_matches}"
            validation_result["redirect_suggestions"] = list(redirect_matches.keys())
        else:
            # Ambiguous case - could be literature review
            validation_result["is_appropriate"] = True
            validation_result["confidence"] = 0.6
            validation_result["reasoning"] = "Request could benefit from literature review approach"
            validation_result["recommendations"] = [
                "Clarify if systematic literature analysis is needed",
                "Consider if research synthesis would be valuable"
            ]
        
        # Assess scope complexity
        scope_indicators = {
            "broad": ["comprehensive", "extensive", "all", "complete", "thorough"],
            "focused": ["specific", "particular", "focused", "narrow", "targeted"],
            "temporal": ["recent", "latest", "current", "historical", "trends"],
            "methodological": ["systematic", "meta-analysis", "quantitative", "qualitative"]
        }
        
        scope_assessment = {}
        for scope_type, indicators in scope_indicators.items():
            matches = [ind for ind in indicators if ind in request_lower]
            if matches:
                scope_assessment[scope_type] = matches
        
        validation_result["scope_assessment"] = scope_assessment
        
        return validation_result
        
    except Exception as e:
        return {
            "is_appropriate": False,
            "confidence": 0.0,
            "reasoning": f"Error during validation: {str(e)}",
            "recommendations": ["Please rephrase your request"],
            "redirect_suggestions": ["general"],
            "scope_assessment": {},
            "timestamp": datetime.now().isoformat()
        }


def _assess_research_feasibility(
    research_topic: str,
    time_constraints: str = "",
    resource_constraints: str = ""
) -> Dict[str, Any]:
    """
    Assess the feasibility of conducting a literature review on the given topic.
    
    Args:
        research_topic: The main research topic or question
        time_constraints: Any time limitations
        resource_constraints: Any resource limitations
        
    Returns:
        Dictionary with feasibility assessment
    """
    try:
        feasibility_assessment = {
            "feasible": True,
            "complexity_level": "medium",
            "estimated_papers": "50-100",
            "estimated_time": "2-4 weeks",
            "challenges": [],
            "recommendations": [],
            "search_strategy_hints": [],
            "timestamp": datetime.now().isoformat()
        }
        
        # Assess topic complexity
        complex_topics = [
            "artificial intelligence", "machine learning", "climate change",
            "cancer treatment", "mental health", "covid-19", "blockchain"
        ]
        
        topic_lower = research_topic.lower()
        
        if any(complex_topic in topic_lower for complex_topic in complex_topics):
            feasibility_assessment["complexity_level"] = "high"
            feasibility_assessment["estimated_papers"] = "200-500"
            feasibility_assessment["estimated_time"] = "4-8 weeks"
            feasibility_assessment["challenges"] = [
                "Large volume of literature",
                "Rapidly evolving field",
                "Multiple sub-domains to consider"
            ]
        
        # Provide search strategy hints
        if "systematic" in topic_lower:
            feasibility_assessment["search_strategy_hints"] = [
                "Use PRISMA guidelines",
                "Define clear inclusion/exclusion criteria",
                "Search multiple databases"
            ]
        
        feasibility_assessment["recommendations"] = [
            "Start with a focused research question",
            "Consider using CORE API for comprehensive search",
            "Plan for iterative refinement of scope"
        ]
        
        return feasibility_assessment
        
    except Exception as e:
        return {
            "feasible": False,
            "complexity_level": "unknown",
            "estimated_papers": "unknown",
            "estimated_time": "unknown",
            "challenges": [f"Assessment error: {str(e)}"],
            "recommendations": ["Please provide more specific topic information"],
            "search_strategy_hints": [],
            "timestamp": datetime.now().isoformat()
        }


def create_request_validator():
    """Create the Request Validator subagent with Grok-4-Fast model."""
    
    # Use default model (Grok-4-Fast) for fast validation
    model = get_default_model()
    
    return {
        "name": "request_validator",
        "description": "Validates literature review requests and assesses feasibility. Handles validation logic internally including appropriateness assessment, scope analysis, and feasibility evaluation.",
        "prompt": REQUEST_VALIDATOR_PROMPT,
        # No external tools needed - subagent handles validation logic internally
        "model": model
    }
