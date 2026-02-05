"""API routes"""

from app.routes.chat import router as chat_router
from app.routes.tasks import router as tasks_router
from app.routes.memory import router as memory_router

__all__ = ["chat_router", "tasks_router", "memory_router"]
