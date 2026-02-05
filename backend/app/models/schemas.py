"""Pydantic models and schemas"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# Enums
class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Intent(str, Enum):
    PLANNING = "planning"
    LEARNING = "learning"
    REMEMBERING = "remembering"
    REWRITING = "rewriting"
    DECISION_MAKING = "decision_making"
    GENERAL = "general"


class ToneType(str, Enum):
    POLITE = "polite"
    PROFESSIONAL = "professional"
    CASUAL = "casual"


# Request/Response Models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    intent: Optional[str] = None
    tool_calls: Optional[List[str]] = None
    session_id: str


# Task Models
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[str] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[str] = None


class Task(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    due_date: Optional[str] = None
    created_at: str
    updated_at: str
    completed_at: Optional[str] = None


# Memory Models
class MemoryCreate(BaseModel):
    content: str
    type: str  # note, learning, conversation
    metadata: Optional[Dict[str, Any]] = None


class Memory(BaseModel):
    id: str
    content: str
    type: str
    metadata: Dict[str, Any]
    created_at: str


class MemorySearchRequest(BaseModel):
    query: str
    type: Optional[str] = None  # note, learning, conversation, or None for all
    n_results: int = 5


# Learning Models
class LearningTopic(BaseModel):
    id: Optional[int] = None
    topic: str
    subtopic: Optional[str] = None
    status: str = "not_started"
    progress: int = 0
    notes: Optional[str] = None
    last_reviewed: Optional[str] = None


class LearningPlanRequest(BaseModel):
    topic: str
    time_available: Optional[str] = None  # e.g., "30 minutes", "1 hour"
    difficulty: Optional[str] = "beginner"


# Decision Models
class DecisionRequest(BaseModel):
    question: str
    options: List[str]


class DecisionResponse(BaseModel):
    question: str
    options: List[str]
    analysis: str
    recommendation: Optional[str] = None


# Rewrite Models
class RewriteRequest(BaseModel):
    text: str
    tone: ToneType = ToneType.PROFESSIONAL
    instructions: Optional[str] = None


class RewriteResponse(BaseModel):
    original: str
    rewritten: str
    tone: str


# Agent State Model
class AgentState(BaseModel):
    user_input: str
    intent: str = ""
    retrieved_memory: List[Dict[str, Any]] = []
    planned_actions: List[str] = []
    tool_results: List[Dict[str, Any]] = []
    final_response: str = ""
    session_id: str = ""
