"""Agent nodes (processing steps)"""

import json
from typing import Dict, Any
from langchain_core.messages import HumanMessage, AIMessage

from app.agent.state import AgentState
from app.services.ai_service import ai_service
from app.core.vector_store import vector_store
from app.tools import all_tools


async def detect_intent_node(state: AgentState) -> Dict[str, Any]:
    """Detect user intent from input"""
    user_input = state["user_input"]
    
    # Detect intent using AI
    intent = await ai_service.detect_intent(user_input)
    
    return {
        "intent": intent,
        "messages": [HumanMessage(content=user_input)]
    }


async def retrieve_memory_node(state: AgentState) -> Dict[str, Any]:
    """Retrieve relevant memory based on user input"""
    user_input = state["user_input"]
    
    # Search across all memory types
    memory_results = vector_store.search_all(user_input, n_results=3)
    
    # Flatten results
    retrieved_memory = []
    for memory_type, results in memory_results.items():
        for result in results:
            retrieved_memory.append({
                "type": memory_type,
                "content": result["content"],
                "metadata": result["metadata"]
            })
    
    return {"retrieved_memory": retrieved_memory}


async def plan_actions_node(state: AgentState) -> Dict[str, Any]:
    """Plan which tools/actions to use based on intent"""
    intent = state["intent"]
    user_input = state["user_input"]
    
    # Define action plans based on intent
    action_plans = {
        "planning": ["check_pending_tasks", "create_daily_plan_or_task"],
        "learning": ["get_learning_progress", "create_or_update_learning_plan"],
        "remembering": ["search_memory_or_store_info"],
        "rewriting": ["rewrite_text"],
        "decision_making": ["analyze_decision"],
        "general": ["search_memory", "general_conversation"]
    }
    
    planned_actions = action_plans.get(intent, ["general_conversation"])
    
    return {"planned_actions": planned_actions}


async def execute_tools_node(state: AgentState) -> Dict[str, Any]:
    """Execute planned tools based on actions"""
    user_input = state["user_input"]
    intent = state["intent"]
    memory_context = state.get("retrieved_memory", [])
    
    # Build context from memory
    memory_text = ""
    if memory_context:
        memory_text = "\n\nRelevant context from memory:\n"
        for mem in memory_context[:3]:  # Top 3 memories
            memory_text += f"- [{mem['type']}] {mem['content'][:200]}...\n"
    
    # Create response using AI directly (simplified approach)
    system_prompt = f"""You are ab360, a personal AI assistant. You help with:
- Daily planning and task management
- Learning and self-improvement
- Memory and information storage
- Communication assistance
- Decision support

Current intent: {intent}
{memory_text}

Respond helpfully to the user's request. Be concise but thorough."""
    
    try:
        # Generate response using Ollama
        response = await ai_service.generate_response(user_input, system_prompt)
        
        return {
            "tool_results": [{"output": response}],
            "messages": [AIMessage(content=response)]
        }
    except Exception as e:
        error_msg = f"Error generating response: {str(e)}"
        return {
            "tool_results": [{"error": error_msg}],
            "messages": [AIMessage(content=error_msg)]
        }


async def generate_response_node(state: AgentState) -> Dict[str, Any]:
    """Generate final response based on tool results"""
    user_input = state["user_input"]
    intent = state["intent"]
    tool_results = state.get("tool_results", [])
    
    # If tool execution provided output, use it
    if tool_results and len(tool_results) > 0:
        last_result = tool_results[-1]
        if "output" in last_result:
            final_response = last_result["output"]
        elif "error" in last_result:
            final_response = f"I encountered an issue: {last_result['error']}"
        else:
            final_response = "I've processed your request."
    else:
        # Generate response without tools
        system_prompt = f"""You are ab360, a helpful personal AI assistant.
The user's intent seems to be: {intent}

Provide a helpful, concise response."""
        
        final_response = await ai_service.generate_response(user_input, system_prompt)
    
    return {"final_response": final_response}


async def store_conversation_node(state: AgentState) -> Dict[str, Any]:
    """Store important conversation in memory"""
    from app.tools.memory import store_conversation
    
    user_input = state["user_input"]
    final_response = state["final_response"]
    intent = state["intent"]
    
    # Store if conversation seems important (not just general chat)
    if intent in ["planning", "learning", "remembering", "decision_making"]:
        try:
            await store_conversation(user_input, final_response, intent)
        except:
            pass  # Fail silently
    
    return {}
