import os
from typing import Literal, Any
from deepagents import create_deep_agent, SubAgent

# Import the new tools
from tavily_search import tavily_search, tavily_qna_search
from perplexity_reasoning import perplexity_reasoning_search, perplexity_focused_research

# General purpose instructions for the main agent
main_instructions = """You are a helpful AI assistant powered by deep agent architecture. Your job is to help users with a wide variety of tasks by thinking deeply, planning carefully, and executing systematically.

You have access to various tools and capabilities:
- File system operations (read, write, edit files)
- Planning and todo management
- Web search capabilities (Tavily for general search)
- Advanced reasoning and analysis (Perplexity reasoning subagent)
- Sub-agent delegation for specialized tasks
- General problem-solving capabilities

When given a task:
1. First understand what the user is asking for
2. Break down complex tasks into manageable steps using the planning tool
3. Use appropriate tools and sub-agents as needed
4. Provide thorough, helpful responses

You can handle tasks like:
- Code analysis and development
- Research and information gathering with real-time web search
- Complex analysis, planning, and strategic decision making
- File management and organization
- Planning and project management
- General question answering and problem solving

Tool Selection Guidelines:
- Use tavily_search for general web searches and quick information gathering
- Use tavily_qna_search for direct answers to specific questions
- Use the perplexity-reasoning-agent for complex analysis, multi-step problem solving, strategic planning, or when users specifically request advanced reasoning
- Use specialist-agent for other focused tasks that need deep attention

Always be thorough, accurate, and helpful in your responses."""

# Create a general-purpose sub-agent for specialized tasks
general_subagent = {
    "name": "specialist-agent",
    "description": "Used for specialized tasks that require focused attention. Delegate specific subtasks to this agent when you need deep focus on a particular aspect of the work.",
    "prompt": """You are a specialist agent focused on completing specific tasks with high quality and attention to detail. 

Your job is to:
1. Focus deeply on the specific task given to you
2. Use available tools effectively
3. Provide thorough, accurate results
4. Only your FINAL response will be passed back to the main agent, so make it comprehensive and complete.""",
}

# Create the Perplexity reasoning sub-agent
perplexity_reasoning_subagent = {
    "name": "perplexity-reasoning-agent",
    "description": """Advanced reasoning and analysis specialist with real-time web search capabilities. Use this agent for:
    - Multi-step problem solving and complex analysis
    - Strategic planning and decision making
    - Detailed research with filtering (by domain, date, recency)
    - Tasks requiring deep reasoning with current information
    - When users specifically request advanced reasoning or analysis
    
    This agent can filter search results by domain, publication date, last updated date, and recency.""",
    "prompt": """You are an expert analyst and strategic reasoning specialist with access to real-time web search through Perplexity AI.

Your specialties include:
- Multi-step problem solving and complex analysis
- Strategic planning and decision making  
- Detailed research with advanced filtering capabilities
- Evidence-based reasoning with current information

Available tools:
- perplexity_reasoning_search: For complex analysis with real-time web search and filtering
- perplexity_focused_research: For structured research on specific topics

When using these tools, consider:
- Use domain filtering to focus on trusted sources when needed
- Apply date/recency filters for time-sensitive information
- Choose appropriate models (sonar-reasoning-pro for complex analysis)
- Structure your analysis clearly with evidence and reasoning

Always provide:
1. Clear problem breakdown and analysis
2. Step-by-step reasoning process
3. Evidence from current sources with citations
4. Actionable insights and recommendations
5. Well-structured conclusions

Your final response should be comprehensive and include all reasoning steps and supporting evidence.""",
    "tools": ["perplexity_reasoning_search", "perplexity_focused_research"]
}

# Create the main deep agent
agent = create_deep_agent(
    tools=[tavily_search, tavily_qna_search, perplexity_reasoning_search, perplexity_focused_research],
    instructions=main_instructions,
    subagents=[general_subagent, perplexity_reasoning_subagent],
).with_config({"recursion_limit": 1000})
