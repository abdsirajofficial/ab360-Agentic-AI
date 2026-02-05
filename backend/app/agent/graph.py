"""LangGraph agent workflow"""

from langgraph.graph import StateGraph, END
from app.agent.state import AgentState
from app.agent.nodes import (
    detect_intent_node,
    retrieve_memory_node,
    plan_actions_node,
    execute_tools_node,
    generate_response_node,
    store_conversation_node,
)


def create_agent_graph() -> StateGraph:
    """Create the agent workflow graph"""
    
    # Create graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("detect_intent", detect_intent_node)
    workflow.add_node("retrieve_memory", retrieve_memory_node)
    workflow.add_node("plan_actions", plan_actions_node)
    workflow.add_node("execute_tools", execute_tools_node)
    workflow.add_node("generate_response", generate_response_node)
    workflow.add_node("store_conversation", store_conversation_node)
    
    # Define edges (workflow)
    workflow.set_entry_point("detect_intent")
    workflow.add_edge("detect_intent", "retrieve_memory")
    workflow.add_edge("retrieve_memory", "plan_actions")
    workflow.add_edge("plan_actions", "execute_tools")
    workflow.add_edge("execute_tools", "generate_response")
    workflow.add_edge("generate_response", "store_conversation")
    workflow.add_edge("store_conversation", END)
    
    # Compile graph
    return workflow.compile()


# Global agent graph instance
agent_graph = create_agent_graph()
