"""Memory Tool"""

import json
from datetime import datetime
from langchain.tools import tool

from app.core.database import db
from app.core.vector_store import vector_store


@tool
def store_preference(key: str, value: str) -> str:
    """Store a user preference.
    
    Args:
        key: Preference key (required)
        value: Preference value (required)
    
    Returns:
        JSON string with result
    """
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO preferences (key, value)
                   VALUES (?, ?)
                   ON CONFLICT(key) DO UPDATE SET value = ?, updated_at = CURRENT_TIMESTAMP""",
                (key, value, value)
            )
            
            return json.dumps({
                "success": True,
                "message": f"Preference '{key}' stored successfully"
            })
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@tool
def get_preference(key: str) -> str:
    """Get a user preference by key.
    
    Args:
        key: Preference key (required)
    
    Returns:
        JSON string with preference value
    """
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM preferences WHERE key = ?", (key,))
            row = cursor.fetchone()
            
            if row:
                return json.dumps({
                    "success": True,
                    "key": key,
                    "value": row[0]
                })
            else:
                return json.dumps({
                    "success": False,
                    "error": f"Preference '{key}' not found"
                })
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@tool
def get_all_preferences() -> str:
    """Get all user preferences.
    
    Returns:
        JSON string with all preferences
    """
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM preferences")
            prefs = {row[0]: row[1] for row in cursor.fetchall()}
            
            return json.dumps({
                "success": True,
                "count": len(prefs),
                "preferences": prefs
            })
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@tool
def search_memory(query: str, limit: int = 5) -> str:
    """Search across all memory (notes, learning, conversations).
    
    Args:
        query: Search query (required)
        limit: Maximum results per type (default: 5)
    
    Returns:
        JSON string with search results
    """
    try:
        results = vector_store.search_all(query, n_results=limit)
        
        total_count = sum(len(v) for v in results.values())
        
        return json.dumps({
            "success": True,
            "total_count": total_count,
            "results": results
        })
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@tool
def store_conversation(user_input: str, agent_response: str, intent: str = "") -> str:
    """Store an important conversation in memory.
    
    Args:
        user_input: User's input (required)
        agent_response: Agent's response (required)
        intent: Detected intent (optional)
    
    Returns:
        JSON string with result
    """
    try:
        # Store in SQLite
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO conversations (user_input, intent, agent_response)
                   VALUES (?, ?, ?)""",
                (user_input, intent, agent_response)
            )
        
        # Store in vector memory
        conv_id = f"conv_{datetime.now().timestamp()}"
        content = f"User: {user_input}\nAssistant: {agent_response}"
        vector_store.add_conversation(conv_id, content, {"intent": intent})
        
        return json.dumps({
            "success": True,
            "message": "Conversation stored in memory"
        })
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


# Export all tools
memory_tools = [
    store_preference,
    get_preference,
    get_all_preferences,
    search_memory,
    store_conversation
]
