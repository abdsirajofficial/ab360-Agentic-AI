"""Memory management endpoints"""

from fastapi import APIRouter, HTTPException
from typing import List

from app.models import MemoryCreate, Memory, MemorySearchRequest
from app.core.vector_store import vector_store
from datetime import datetime

router = APIRouter(prefix="/api/memory", tags=["memory"])


@router.post("/search")
async def search_memory(request: MemorySearchRequest):
    """Search memory across all types or specific type"""
    try:
        if request.type:
            # Search specific type
            if request.type == "notes":
                results = vector_store.search_notes(request.query, request.n_results)
            elif request.type == "learning":
                results = vector_store.search_learning(request.query, request.n_results)
            elif request.type == "conversations":
                results = vector_store.search_conversations(request.query, request.n_results)
            else:
                raise HTTPException(status_code=400, detail="Invalid memory type")
            
            return {"results": results, "type": request.type}
        else:
            # Search all types
            results = vector_store.search_all(request.query, request.n_results)
            return {"results": results}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/")
async def create_memory(memory: MemoryCreate):
    """Store a new memory"""
    try:
        memory_id = f"{memory.type}_{datetime.now().timestamp()}"
        
        if memory.type == "note":
            vector_store.add_note(memory_id, memory.content, memory.metadata)
        elif memory.type == "learning":
            vector_store.add_learning_summary(memory_id, memory.content, memory.metadata)
        elif memory.type == "conversation":
            vector_store.add_conversation(memory_id, memory.content, memory.metadata)
        else:
            raise HTTPException(status_code=400, detail="Invalid memory type")
        
        return {
            "success": True,
            "memory_id": memory_id,
            "message": f"Memory stored successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{memory_type}/{memory_id}")
async def delete_memory(memory_type: str, memory_id: str):
    """Delete a memory by ID and type"""
    try:
        if memory_type == "note":
            vector_store.delete_note(memory_id)
        elif memory_type == "learning":
            vector_store.delete_learning(memory_id)
        elif memory_type == "conversation":
            vector_store.delete_conversation(memory_id)
        else:
            raise HTTPException(status_code=400, detail="Invalid memory type")
        
        return {"message": f"Memory {memory_id} deleted successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
