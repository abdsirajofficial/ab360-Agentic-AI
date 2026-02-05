"""Learning Tracker Tool"""

import json
from datetime import datetime
from langchain.tools import tool

from app.core.database import db
from app.core.vector_store import vector_store
from app.services.ai_service import ai_service


@tool
async def create_learning_plan(topic: str, time_available: str = "30 minutes", difficulty: str = "beginner") -> str:
    """Create a learning plan for a topic.
    
    Args:
        topic: Topic to learn (required)
        time_available: Time available per session (default: "30 minutes")
        difficulty: Difficulty level - beginner, intermediate, advanced (default: beginner)
    
    Returns:
        JSON string with learning plan
    """
    try:
        prompt = f"""Create a learning plan for: {topic}

Difficulty level: {difficulty}
Time available per session: {time_available}

Generate a structured learning plan with:
1. Key subtopics to cover
2. Recommended sequence
3. Time estimates
4. Practice exercises

Format as JSON:
{{
    "topic": "{topic}",
    "subtopics": [
        {{"name": "subtopic 1", "duration": "10 minutes", "order": 1}},
        ...
    ],
    "estimated_total_time": "X hours",
    "recommendations": ["tip 1", "tip 2"]
}}"""
        
        response = await ai_service.generate_response(prompt)
        
        # Try to parse JSON
        try:
            plan = json.loads(response)
            
            # Store subtopics in database
            with db.get_connection() as conn:
                cursor = conn.cursor()
                for subtopic in plan.get("subtopics", []):
                    cursor.execute(
                        """INSERT INTO learning_progress (topic, subtopic, status)
                           VALUES (?, ?, ?)""",
                        (topic, subtopic.get("name", ""), "not_started")
                    )
            
            return json.dumps({
                "success": True,
                "plan": plan
            })
        except:
            return json.dumps({
                "success": True,
                "plan_text": response
            })
    
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@tool
def update_learning_progress(topic: str, subtopic: str, progress: int, notes: str = "") -> str:
    """Update learning progress for a topic.
    
    Args:
        topic: Main topic (required)
        subtopic: Subtopic name (required)
        progress: Progress percentage 0-100 (required)
        notes: Progress notes (optional)
    
    Returns:
        JSON string with result
    """
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Determine status based on progress
            if progress == 0:
                status = "not_started"
            elif progress == 100:
                status = "completed"
            else:
                status = "in_progress"
            
            cursor.execute(
                """UPDATE learning_progress 
                   SET progress = ?, status = ?, notes = ?, 
                       last_reviewed = CURRENT_TIMESTAMP,
                       updated_at = CURRENT_TIMESTAMP
                   WHERE topic = ? AND subtopic = ?""",
                (progress, status, notes, topic, subtopic)
            )
            
            if cursor.rowcount == 0:
                return json.dumps({"success": False, "error": "Topic/subtopic not found"})
            
            # Store in vector memory if notes provided
            if notes:
                summary_id = f"learning_{topic}_{subtopic}_{datetime.now().timestamp()}"
                content = f"Learning {topic} - {subtopic}: {notes}"
                vector_store.add_learning_summary(summary_id, content, {
                    "topic": topic,
                    "subtopic": subtopic,
                    "progress": progress
                })
            
            return json.dumps({
                "success": True,
                "message": f"Progress updated: {topic} - {subtopic} ({progress}%)"
            })
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@tool
def get_learning_progress(topic: str = "") -> str:
    """Get learning progress, optionally filtered by topic.
    
    Args:
        topic: Filter by topic (optional)
    
    Returns:
        JSON string with learning progress
    """
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            if topic:
                cursor.execute(
                    "SELECT * FROM learning_progress WHERE topic = ? ORDER BY updated_at DESC",
                    (topic,)
                )
            else:
                cursor.execute("SELECT * FROM learning_progress ORDER BY updated_at DESC")
            
            progress = [dict(row) for row in cursor.fetchall()]
            
            return json.dumps({
                "success": True,
                "count": len(progress),
                "progress": progress
            })
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


# Export all tools
learning_tools = [create_learning_plan, update_learning_progress, get_learning_progress]
