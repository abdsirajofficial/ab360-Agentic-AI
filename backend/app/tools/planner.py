"""Planner Tool"""

import json
from datetime import datetime, timedelta
from typing import Dict, Any
from langchain.tools import tool

from app.core.database import db
from app.services.ai_service import ai_service


@tool
async def create_daily_plan(focus_areas: str, available_hours: str = "8") -> str:
    """Create a daily plan based on tasks and focus areas.
    
    Args:
        focus_areas: What to focus on today (e.g., "office work, learning Python")
        available_hours: Hours available today (default: 8)
    
    Returns:
        JSON string with daily plan
    """
    try:
        # Get pending tasks
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT * FROM tasks 
                   WHERE status IN ('pending', 'in_progress')
                   ORDER BY 
                       CASE priority 
                           WHEN 'high' THEN 1
                           WHEN 'medium' THEN 2
                           WHEN 'low' THEN 3
                       END,
                       due_date ASC
                   LIMIT 10"""
            )
            tasks = [dict(row) for row in cursor.fetchall()]
        
        # Generate plan using AI
        tasks_text = "\n".join([
            f"- [{t['priority']}] {t['title']}" + (f" (due: {t['due_date']})" if t['due_date'] else "")
            for t in tasks
        ])
        
        prompt = f"""Create a daily plan for today.

Available time: {available_hours} hours
Focus areas: {focus_areas}

Current pending tasks:
{tasks_text if tasks else "No pending tasks"}

Generate a structured daily plan with time blocks. Be realistic about time estimates.
Format as JSON:
{{
    "plan": [
        {{"time": "9:00-10:00", "activity": "Task 1", "task_id": 1}},
        ...
    ],
    "summary": "Brief summary of the day"
}}"""
        
        response = await ai_service.generate_response(prompt)
        
        # Try to parse JSON, fallback to text
        try:
            plan_data = json.loads(response)
            return json.dumps({
                "success": True,
                "plan": plan_data.get("plan", []),
                "summary": plan_data.get("summary", ""),
                "focus_areas": focus_areas,
                "available_hours": available_hours
            })
        except:
            return json.dumps({
                "success": True,
                "plan_text": response,
                "focus_areas": focus_areas
            })
    
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@tool
def set_goal(title: str, description: str, category: str = "personal", target_date: str = "") -> str:
    """Set a new goal.
    
    Args:
        title: Goal title (required)
        description: Goal description (required)
        category: Goal category (default: personal)
        target_date: Target completion date YYYY-MM-DD (optional)
    
    Returns:
        JSON string with result
    """
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO goals (title, description, category, target_date)
                   VALUES (?, ?, ?, ?)""",
                (title, description, category, target_date if target_date else None)
            )
            goal_id = cursor.lastrowid
            
            return json.dumps({
                "success": True,
                "goal_id": goal_id,
                "message": f"Goal '{title}' created successfully"
            })
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@tool
def get_goals(status: str = "active") -> str:
    """Get goals by status.
    
    Args:
        status: Filter by status - active, completed, abandoned (default: active)
    
    Returns:
        JSON string with list of goals
    """
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM goals WHERE status = ? ORDER BY created_at DESC",
                (status,)
            )
            goals = [dict(row) for row in cursor.fetchall()]
            
            return json.dumps({
                "success": True,
                "count": len(goals),
                "goals": goals
            })
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


# Export all tools
planner_tools = [create_daily_plan, set_goal, get_goals]
