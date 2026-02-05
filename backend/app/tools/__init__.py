"""Agent tools"""

from app.tools.task_manager import task_tools
from app.tools.planner import planner_tools
from app.tools.notes import notes_tools
from app.tools.learning_tracker import learning_tools
from app.tools.memory import memory_tools

# Combine all tools
all_tools = (
    task_tools +
    planner_tools +
    notes_tools +
    learning_tools +
    memory_tools
)

__all__ = [
    "all_tools",
    "task_tools",
    "planner_tools",
    "notes_tools",
    "learning_tools",
    "memory_tools",
]
