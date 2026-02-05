"""Task Manager Tool"""

import json
from datetime import datetime
from typing import Dict, Any, List
from langchain.tools import tool

from app.core.database import db


@tool
def create_task(title: str, description: str = "", priority: str = "medium", due_date: str = "") -> str:
    """Create a new task.
    
    Args:
        title: Task title (required)
        description: Task description (optional)
        priority: Task priority - low, medium, or high (default: medium)
        due_date: Due date in YYYY-MM-DD format (optional)
    
    Returns:
        JSON string with task details or error message
    """
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO tasks (title, description, priority, due_date)
                   VALUES (?, ?, ?, ?)""",
                (title, description, priority, due_date if due_date else None)
            )
            task_id = cursor.lastrowid
            
            return json.dumps({
                "success": True,
                "task_id": task_id,
                "message": f"Task '{title}' created successfully"
            })
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@tool
def update_task_status(task_id: int, status: str) -> str:
    """Update task status.
    
    Args:
        task_id: Task ID (required)
        status: New status - pending, in_progress, completed, or cancelled
    
    Returns:
        JSON string with result
    """
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Update completed_at if marking as completed
            completed_at = datetime.now().isoformat() if status == "completed" else None
            
            cursor.execute(
                """UPDATE tasks 
                   SET status = ?, updated_at = CURRENT_TIMESTAMP, completed_at = ?
                   WHERE id = ?""",
                (status, completed_at, task_id)
            )
            
            if cursor.rowcount == 0:
                return json.dumps({"success": False, "error": f"Task {task_id} not found"})
            
            return json.dumps({
                "success": True,
                "message": f"Task {task_id} status updated to {status}"
            })
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@tool
def get_tasks(status: str = "") -> str:
    """Get tasks, optionally filtered by status.
    
    Args:
        status: Filter by status - pending, in_progress, completed, cancelled (optional)
    
    Returns:
        JSON string with list of tasks
    """
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            if status:
                cursor.execute(
                    "SELECT * FROM tasks WHERE status = ? ORDER BY created_at DESC",
                    (status,)
                )
            else:
                cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC")
            
            tasks = [dict(row) for row in cursor.fetchall()]
            
            return json.dumps({
                "success": True,
                "count": len(tasks),
                "tasks": tasks
            })
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@tool
def get_pending_tasks() -> str:
    """Get all pending and in-progress tasks.
    
    Returns:
        JSON string with list of active tasks
    """
    try:
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
                       due_date ASC"""
            )
            
            tasks = [dict(row) for row in cursor.fetchall()]
            
            return json.dumps({
                "success": True,
                "count": len(tasks),
                "tasks": tasks
            })
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


# Export all tools
task_tools = [create_task, update_task_status, get_tasks, get_pending_tasks]
