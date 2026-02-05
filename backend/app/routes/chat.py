"""Chat endpoint"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
import uuid

from app.models import ChatRequest, ChatResponse
from app.agent import agent_graph

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint - processes user input through agent"""
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Create initial state
        initial_state = {
            "user_input": request.message,
            "intent": "",
            "retrieved_memory": [],
            "planned_actions": [],
            "tool_results": [],
            "messages": [],
            "final_response": "",
            "session_id": session_id,
            "metadata": {
                "timestamp": datetime.now().isoformat()
            }
        }
        
        # Run through agent graph
        result = await agent_graph.ainvoke(initial_state)
        
        # Extract tool calls for logging
        tool_calls = []
        for tool_result in result.get("tool_results", []):
            if "tool_name" in tool_result:
                tool_calls.append(tool_result["tool_name"])
        
        return ChatResponse(
            response=result.get("final_response", "I'm not sure how to respond to that."),
            intent=result.get("intent"),
            tool_calls=tool_calls if tool_calls else None,
            session_id=session_id
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ab360",
        "timestamp": datetime.now().isoformat()
    }
