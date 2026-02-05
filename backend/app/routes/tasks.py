"""Task management endpoints"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional

from app.models import Task, TaskCreate, TaskUpdate
from app.core.database import db

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("/", response_model=List[Task])
async def get_tasks(status: Optional[str] = None):
    """Get all tasks, optionally filtered by status"""
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
            
            tasks = [Task(**dict(row)) for row in cursor.fetchall()]
            return tasks
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{task_id}", response_model=Task)
async def get_task(task_id: int):
    """Get a specific task by ID"""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
            row = cursor.fetchone()
            
            if not row:
                raise HTTPException(status_code=404, detail="Task not found")
            
            return Task(**dict(row))
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=Task)
async def create_task(task: TaskCreate):
    """Create a new task"""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO tasks (title, description, priority, due_date)
                   VALUES (?, ?, ?, ?)""",
                (task.title, task.description, task.priority.value, task.due_date)
            )
            task_id = cursor.lastrowid
            
            # Fetch created task
            cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
            row = cursor.fetchone()
            
            return Task(**dict(row))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{task_id}", response_model=Task)
async def update_task(task_id: int, task_update: TaskUpdate):
    """Update a task"""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Build update query dynamically
            updates = []
            values = []
            
            if task_update.title is not None:
                updates.append("title = ?")
                values.append(task_update.title)
            if task_update.description is not None:
                updates.append("description = ?")
                values.append(task_update.description)
            if task_update.status is not None:
                updates.append("status = ?")
                values.append(task_update.status.value)
            if task_update.priority is not None:
                updates.append("priority = ?")
                values.append(task_update.priority.value)
            if task_update.due_date is not None:
                updates.append("due_date = ?")
                values.append(task_update.due_date)
            
            if not updates:
                raise HTTPException(status_code=400, detail="No fields to update")
            
            updates.append("updated_at = CURRENT_TIMESTAMP")
            values.append(task_id)
            
            query = f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, values)
            
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Task not found")
            
            # Fetch updated task
            cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
            row = cursor.fetchone()
            
            return Task(**dict(row))
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{task_id}")
async def delete_task(task_id: int):
    """Delete a task"""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Task not found")
            
            return {"message": "Task deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
