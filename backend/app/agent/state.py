"""Agent state definition"""

from typing import TypedDict, List, Dict, Any
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """State structure for the agent"""
    
    # User input
    user_input: str
    
    # Detected intent
    intent: str
    
    # Retrieved memory context
    retrieved_memory: List[Dict[str, Any]]
    
    # Planned actions based on intent
    planned_actions: List[str]
    
    # Tool execution results
    tool_results: List[Dict[str, Any]]
    
    # Messages for chat history
    messages: List[BaseMessage]
    
    # Final response to user
    final_response: str
    
    # Session ID
    session_id: str
    
    # Metadata
    metadata: Dict[str, Any]
