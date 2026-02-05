"""Notes Tool"""

import json
from datetime import datetime
from typing import Optional
from langchain.tools import tool

from app.core.vector_store import vector_store


@tool
def save_note(content: str, tags: str = "") -> str:
    """Save a note to memory.
    
    Args:
        content: Note content (required)
        tags: Comma-separated tags (optional)
    
    Returns:
        JSON string with result
    """
    try:
        note_id = f"note_{datetime.now().timestamp()}"
        
        metadata = {
            "tags": tags.split(",") if tags else [],
            "created_at": datetime.now().isoformat()
        }
        
        vector_store.add_note(note_id, content, metadata)
        
        return json.dumps({
            "success": True,
            "note_id": note_id,
            "message": "Note saved successfully"
        })
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@tool
def search_notes(query: str, limit: int = 5) -> str:
    """Search for notes by content.
    
    Args:
        query: Search query (required)
        limit: Maximum number of results (default: 5)
    
    Returns:
        JSON string with search results
    """
    try:
        results = vector_store.search_notes(query, n_results=limit)
        
        return json.dumps({
            "success": True,
            "count": len(results),
            "notes": results
        })
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@tool
def delete_note(note_id: str) -> str:
    """Delete a note by ID.
    
    Args:
        note_id: Note ID to delete (required)
    
    Returns:
        JSON string with result
    """
    try:
        vector_store.delete_note(note_id)
        
        return json.dumps({
            "success": True,
            "message": f"Note {note_id} deleted successfully"
        })
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


# Export all tools
notes_tools = [save_note, search_notes, delete_note]
