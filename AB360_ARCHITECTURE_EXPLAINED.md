# ab360 Architecture Explained

Complete guide to how Storage, LangChain, LangGraph, LangSmith, Vector DB, and SQLite work together.

---

## 🎯 Overview: The Big Picture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INPUT                               │
│                    "Plan my day with learning"                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     LANGGRAPH AGENT                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Step 1: Detect Intent → "planning"                       │  │
│  │  Step 2: Search Memory (Vector DB) → Past preferences    │  │
│  │  Step 3: Plan Actions → Which tools to use                │  │
│  │  Step 4: Execute Tools (LangChain) → Call functions      │  │
│  │  Step 5: Generate Response → Format answer               │  │
│  │  Step 6: Store Conversation → Save to memory             │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
┌────────────────┐ ┌────────────┐ ┌──────────────┐
│   LANGCHAIN    │ │  CHROMADB  │ │   SQLITE     │
│     TOOLS      │ │  (Vector)  │ │ (Structured) │
│  - Task Mgr    │ │  - Notes   │ │  - Tasks     │
│  - Planner     │ │  - Learning│ │  - Goals     │
│  - Notes       │ │  - Convos  │ │  - Prefs     │
│  - Learning    │ │            │ │  - Learning  │
│  - Memory      │ │            │ │  - Decisions │
└────────────────┘ └────────────┘ └──────────────┘
```

---

## 📊 Component 1: SQLite (Structured Data Storage)

### What It Does
SQLite stores **structured, queryable data** in tables.

### Location
```
ab360/backend/data/ab360.db
```

### Tables Created

#### 1. **tasks** - Task Management
```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'pending',      -- pending, in_progress, completed
    priority TEXT DEFAULT 'medium',      -- low, medium, high
    due_date TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    completed_at TEXT
)
```

**Example:**
```json
{
  "id": 1,
  "title": "Finish documentation",
  "status": "in_progress",
  "priority": "high",
  "due_date": "2026-02-10"
}
```

#### 2. **goals** - Long-term Goals
```sql
CREATE TABLE goals (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    category TEXT,                       -- personal, work, health, etc.
    target_date TEXT,
    status TEXT DEFAULT 'active',        -- active, completed, abandoned
    created_at TEXT,
    updated_at TEXT
)
```

#### 3. **preferences** - User Settings
```sql
CREATE TABLE preferences (
    id INTEGER PRIMARY KEY,
    key TEXT UNIQUE NOT NULL,            -- preference name
    value TEXT NOT NULL,                 -- preference value
    updated_at TEXT
)
```

**Examples:**
```json
[
  {"key": "work_hours", "value": "morning"},
  {"key": "notification_time", "value": "9:00"},
  {"key": "favorite_color", "value": "blue"}
]
```

#### 4. **learning_progress** - Study Tracking
```sql
CREATE TABLE learning_progress (
    id INTEGER PRIMARY KEY,
    topic TEXT NOT NULL,                 -- Main topic
    subtopic TEXT,                       -- Subtopic within main topic
    status TEXT DEFAULT 'not_started',   -- not_started, in_progress, completed
    progress INTEGER DEFAULT 0,          -- 0-100 percentage
    notes TEXT,                          -- Learning notes
    last_reviewed TEXT,                  -- When last studied
    created_at TEXT,
    updated_at TEXT
)
```

**Example:**
```json
{
  "topic": "Python",
  "subtopic": "Decorators",
  "status": "in_progress",
  "progress": 60,
  "notes": "Understood basic syntax, need practice"
}
```

#### 5. **decisions** - Decision History
```sql
CREATE TABLE decisions (
    id INTEGER PRIMARY KEY,
    question TEXT NOT NULL,
    options TEXT NOT NULL,               -- JSON array of options
    analysis TEXT,                       -- AI analysis
    decision TEXT,                       -- User's final decision
    created_at TEXT
)
```

#### 6. **conversations** - Chat History
```sql
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY,
    user_input TEXT NOT NULL,
    intent TEXT,                         -- planning, learning, etc.
    agent_response TEXT,
    tool_calls TEXT,                     -- JSON of tools used
    created_at TEXT
)
```

### Why SQLite?
✅ **Fast queries** - "Get all pending tasks"  
✅ **Relationships** - Link tasks to goals  
✅ **Filtering** - "Show high priority tasks due this week"  
✅ **No setup** - Built into Python  
✅ **Reliable** - ACID compliant  

### Code Example
```python
# app/core/database.py
from app.core.database import db

with db.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM tasks WHERE status = 'pending' ORDER BY priority"
    )
    tasks = [dict(row) for row in cursor.fetchall()]
```

---

## 🧠 Component 2: ChromaDB (Vector Storage)

### What It Does
ChromaDB stores **embeddings** (numerical representations of text) for **semantic search**.

Unlike SQLite which needs exact matches, ChromaDB finds **similar meanings**.

### Location
```
ab360/backend/data/chromadb/
```

### Collections (Like Tables)

#### 1. **notes** - User Notes
Stores free-form text notes with semantic search capability.

**Example:**
```python
# Stored
"Remember that I prefer working in the morning and like coffee"

# Can be found by searching:
"work preferences"  → Finds the note (semantic match!)
"morning routine"   → Finds the note (semantic match!)
"my habits"         → Finds the note (semantic match!)
```

#### 2. **learning** - Learning Summaries
Stores learning notes and summaries.

**Example:**
```python
# Stored
"Learned about Python decorators - they modify function behavior"

# Can be found by:
"function wrappers"  → Finds this (semantic understanding!)
"python advanced"    → Finds this
```

#### 3. **conversations** - Important Chats
Stores important conversations for context retrieval.

### How Vector Search Works

```
1. User Input: "What do I prefer for breakfast?"

2. Convert to Vector (embedding):
   [0.234, -0.123, 0.456, ..., 0.789]  # 1536 dimensions

3. Compare with Stored Vectors:
   Note 1: [0.245, -0.134, 0.467, ...]  → Distance: 0.92 (Close!)
   Note 2: [0.891, 0.234, -0.456, ...]  → Distance: 0.34 (Far)
   
4. Return Closest Matches:
   → "I prefer working mornings and like coffee" (similarity: 92%)
```

### Why ChromaDB?
✅ **Semantic search** - Finds meaning, not exact words  
✅ **Context retrieval** - Agent gets relevant info automatically  
✅ **Flexible** - Stores any text  
✅ **Fast** - Optimized for similarity search  

### Code Example
```python
# app/core/vector_store.py
from app.core.vector_store import vector_store

# Store a note
vector_store.add_note(
    note_id="note_123",
    content="I prefer working in the morning",
    metadata={"created_at": "2026-02-05"}
)

# Search semantically
results = vector_store.search_notes("work preferences", n_results=5)
# Returns notes about work habits, even if they don't say "preferences"
```

---

## 🔗 Component 3: LangChain (Tool Framework)

### What It Does
LangChain provides the **tool infrastructure** that lets the AI agent call Python functions.

### Tools in ab360

Each tool is a Python function decorated with `@tool`:

```python
from langchain.tools import tool

@tool
def create_task(title: str, priority: str = "medium") -> str:
    """Create a new task.
    
    Args:
        title: Task title
        priority: Priority level (low, medium, high)
    
    Returns:
        JSON with task details
    """
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (title, priority) VALUES (?, ?)",
            (title, priority)
        )
        task_id = cursor.lastrowid
    
    return json.dumps({
        "success": True,
        "task_id": task_id,
        "message": f"Task '{title}' created"
    })
```

### Tool Categories

#### 1. **Task Manager Tools** (4 tools)
- `create_task` - Make new task
- `update_task_status` - Change task status
- `get_tasks` - List tasks
- `get_pending_tasks` - List active tasks

#### 2. **Planner Tools** (3 tools)
- `create_daily_plan` - AI generates schedule
- `set_goal` - Create long-term goal
- `get_goals` - List goals

#### 3. **Notes Tools** (3 tools)
- `save_note` - Store note in vector DB
- `search_notes` - Semantic search
- `delete_note` - Remove note

#### 4. **Learning Tools** (3 tools)
- `create_learning_plan` - AI generates study plan
- `update_learning_progress` - Track progress
- `get_learning_progress` - View progress

#### 5. **Memory Tools** (5 tools)
- `store_preference` - Save user preference
- `get_preference` - Retrieve preference
- `search_memory` - Search all memory types
- `store_conversation` - Save important chats

### How LangChain Tools Work

```python
# 1. Define tool
@tool
def my_tool(param: str) -> str:
    """Tool description for AI"""
    return f"Result: {param}"

# 2. Agent sees tool as:
{
    "name": "my_tool",
    "description": "Tool description for AI",
    "parameters": {
        "param": {"type": "string", "description": "..."}
    }
}

# 3. Agent decides to call it:
"I need to call my_tool with param='hello'"

# 4. LangChain executes:
result = my_tool(param="hello")

# 5. Agent sees result:
"Result: hello"
```

### Why LangChain?
✅ **Structured tool calling** - AI knows what functions do  
✅ **Type safety** - Validates inputs  
✅ **Error handling** - Catches issues  
✅ **Logging** - Tracks tool usage  

---

## 🔄 Component 4: LangGraph (Agent Workflow)

### What It Does
LangGraph orchestrates the **agent's thinking process** as a state machine graph.

### Agent Workflow Graph

```
START
  │
  ▼
┌─────────────────┐
│ Detect Intent   │ → Classify: planning, learning, remembering, etc.
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Retrieve Memory │ → Search ChromaDB for relevant context
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Plan Actions    │ → Decide which tools to use
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Execute Tools   │ → Call LangChain tools (SQL, Vector, AI)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Generate Reply  │ → Format response for user
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Store Convo     │ → Save to SQLite + ChromaDB
└────────┬────────┘
         │
         ▼
        END
```

### Agent State

The state flows through each node:

```python
class AgentState(TypedDict):
    user_input: str                    # "Plan my day"
    intent: str                        # "planning"
    retrieved_memory: List[Dict]       # Past preferences from ChromaDB
    planned_actions: List[str]         # ["get_tasks", "create_daily_plan"]
    tool_results: List[Dict]           # Results from tools
    messages: List[BaseMessage]        # Chat history
    final_response: str                # "Here's your plan..."
    session_id: str                    # Session tracking
    metadata: Dict                     # Extra info
```

### Node Examples

#### Node 1: Detect Intent
```python
async def detect_intent_node(state: AgentState) -> Dict:
    user_input = state["user_input"]
    
    # Ask Ollama to classify
    intent = await ai_service.detect_intent(user_input)
    
    return {"intent": intent}
```

#### Node 2: Retrieve Memory
```python
async def retrieve_memory_node(state: AgentState) -> Dict:
    user_input = state["user_input"]
    
    # Search ChromaDB for relevant context
    memory_results = vector_store.search_all(user_input, n_results=3)
    
    return {"retrieved_memory": memory_results}
```

#### Node 4: Execute Tools
```python
async def execute_tools_node(state: AgentState) -> Dict:
    # Build context from memory
    context = format_memory(state["retrieved_memory"])
    
    # Create LangChain agent with tools
    agent = create_tool_calling_agent(
        llm=ai_service.model,
        tools=all_tools,  # All 19 tools
        prompt=build_prompt(context)
    )
    
    # Agent decides which tools to call and executes them
    result = await agent.ainvoke({"input": state["user_input"]})
    
    return {"tool_results": [result]}
```

### Why LangGraph?
✅ **State management** - Tracks everything  
✅ **Debuggable** - See each step  
✅ **Flexible** - Easy to modify flow  
✅ **Resumable** - Can pause and continue  

---

## 📊 Component 5: LangSmith (Debugging - Optional)

### What It Does
LangSmith is a **debugging and monitoring** platform for LangChain applications.

### In ab360
- **Status**: Minimal usage (development only)
- **Purpose**: Debug agent decisions
- **Data**: Tool calls, timing, errors

### Setup (Optional)
```python
# .env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_PROJECT=ab360
```

### What You See in LangSmith
- Agent decision traces
- Tool execution timing
- Error debugging
- Token usage
- Response quality

**Note**: Not required for ab360 to work!

---

## 🔄 Complete Flow Example

### User Request: "Plan my day with learning Python"

#### Step 1: FastAPI receives request
```python
POST /api/chat
{
    "message": "Plan my day with learning Python"
}
```

#### Step 2: LangGraph starts agent workflow

**Node 1 - Detect Intent:**
```python
intent = await ai_service.detect_intent("Plan my day with learning Python")
# → intent = "planning"
```

**Node 2 - Retrieve Memory:**
```python
# Search ChromaDB
memories = vector_store.search_all("Plan my day with learning Python")

# Results:
[
    {"content": "I prefer working in mornings", "type": "note"},
    {"content": "Learning Python - completed basics", "type": "learning"}
]
```

**Node 3 - Plan Actions:**
```python
# Based on intent="planning"
planned_actions = ["get_pending_tasks", "create_daily_plan"]
```

**Node 4 - Execute Tools (LangChain):**

The agent calls tools:

**4a. Call get_pending_tasks:**
```python
# Tool execution
result1 = get_pending_tasks()

# Queries SQLite:
SELECT * FROM tasks WHERE status IN ('pending', 'in_progress')

# Returns:
{
    "tasks": [
        {"id": 1, "title": "Review code", "priority": "high"},
        {"id": 2, "title": "Update docs", "priority": "medium"}
    ]
}
```

**4b. Get learning progress:**
```python
# Query SQLite learning table
result2 = get_learning_progress(topic="Python")

# Returns:
{
    "topic": "Python",
    "progress": [
        {"subtopic": "Basics", "progress": 100},
        {"subtopic": "OOP", "progress": 60}
    ]
}
```

**4c. Call create_daily_plan:**
```python
# AI generates plan using context
result3 = await create_daily_plan(
    focus_areas="learning Python, pending tasks",
    available_hours="8"
)

# Ollama generates:
{
    "plan": [
        {"time": "9:00-10:30", "activity": "Review code (Task #1)"},
        {"time": "10:30-12:00", "activity": "Python OOP study"},
        {"time": "12:00-13:00", "activity": "Lunch break"},
        {"time": "13:00-14:00", "activity": "Python practice"},
        {"time": "14:00-15:00", "activity": "Update docs (Task #2)"}
    ],
    "summary": "Balanced day with work tasks and Python learning"
}
```

**Node 5 - Generate Response:**
```python
final_response = format_response(tool_results)

# Produces:
"Here's your plan for today:

9:00-10:30: Review code (High priority)
10:30-12:00: Python OOP study (continuing from 60%)
12:00-13:00: Lunch break
13:00-14:00: Python practice exercises
14:00-15:00: Update documentation

You have 2 pending tasks and will continue Python OOP learning."
```

**Node 6 - Store Conversation:**

**6a. Save to SQLite:**
```python
INSERT INTO conversations (user_input, intent, agent_response, tool_calls)
VALUES (
    'Plan my day with learning Python',
    'planning',
    'Here is your plan...',
    '["get_pending_tasks", "create_daily_plan"]'
)
```

**6b. Save to ChromaDB:**
```python
vector_store.add_conversation(
    conv_id="conv_123",
    content="User: Plan my day with learning Python\nAssistant: Here's your plan...",
    metadata={"intent": "planning", "date": "2026-02-05"}
)
```

#### Step 3: Return to user
```json
{
    "response": "Here's your plan for today:\n\n9:00-10:30: Review code...",
    "intent": "planning",
    "tool_calls": ["get_pending_tasks", "get_learning_progress", "create_daily_plan"],
    "session_id": "abc123"
}
```

---

## 📈 Data Flow Diagram

```
┌──────────────┐
│  User Input  │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────┐
│         LangGraph Agent                   │
│  ┌────────────────────────────────────┐  │
│  │ 1. Detect Intent (Ollama AI)       │  │
│  │    └→ Uses Ollama for classification│  │
│  └────────────────────────────────────┘  │
│  ┌────────────────────────────────────┐  │
│  │ 2. Retrieve Memory                 │  │
│  │    └→ ChromaDB vector search        │◄─┼─── ChromaDB
│  └────────────────────────────────────┘  │    (Semantic)
│  ┌────────────────────────────────────┐  │
│  │ 3. Execute Tools (LangChain)       │  │
│  │    ├→ Task tools                   │◄─┼─── SQLite
│  │    ├→ Learning tools               │  │    (Structured)
│  │    ├→ Memory tools                 │◄─┼─── ChromaDB
│  │    └→ Planner (uses Ollama)        │  │    (Semantic)
│  └────────────────────────────────────┘  │
│  ┌────────────────────────────────────┐  │
│  │ 4. Generate Response (Ollama AI)   │  │
│  │    └→ Format tool results           │  │
│  └────────────────────────────────────┘  │
│  ┌────────────────────────────────────┐  │
│  │ 5. Store Conversation              │  │
│  │    ├→ SQLite (structured log)      │──┼──► SQLite
│  │    └→ ChromaDB (semantic search)   │──┼──► ChromaDB
│  └────────────────────────────────────┘  │
└──────────────────────────────────────────┘
       │
       ▼
┌──────────────┐
│   Response   │
└──────────────┘
```

---

## 🎯 Key Design Decisions

### Why Two Databases?

**SQLite** - For structured queries
- ✅ "Get tasks due this week"
- ✅ "Count completed learning topics"
- ✅ Fast filtering and sorting

**ChromaDB** - For semantic search
- ✅ "What do I remember about preferences?"
- ✅ "Find notes about work habits"
- ✅ Context retrieval without exact matches

### Why LangChain + LangGraph?

**LangChain** - Tool infrastructure
- Standardizes how tools are called
- Provides validation and error handling

**LangGraph** - Workflow orchestration
- Controls the thinking process
- Makes agent behavior debuggable

### Why Local-First (Ollama)?

✅ **Privacy** - Data never leaves your PC  
✅ **Cost** - $0 forever  
✅ **Speed** - No network latency  
✅ **Reliability** - Works offline  

---

## 📁 File Locations

```
ab360/backend/
├── data/                          # All data storage
│   ├── ab360.db                  # SQLite database
│   └── chromadb/                 # Vector embeddings
│       ├── chroma.sqlite3        # ChromaDB index
│       └── [embeddings]          # Vector data
├── app/
│   ├── core/
│   │   ├── database.py           # SQLite setup & operations
│   │   ├── vector_store.py       # ChromaDB operations
│   │   └── config.py             # Configuration
│   ├── agent/
│   │   ├── state.py              # Agent state definition
│   │   ├── nodes.py              # LangGraph nodes
│   │   └── graph.py              # LangGraph workflow
│   ├── tools/
│   │   ├── task_manager.py       # Task tools (LangChain)
│   │   ├── planner.py            # Planning tools
│   │   ├── notes.py              # Notes tools
│   │   ├── learning_tracker.py   # Learning tools
│   │   └── memory.py             # Memory tools
│   └── services/
│       └── ai_service.py         # Ollama integration
```

---

## 🔍 Debugging & Inspection

### View SQLite Data
```bash
# Install DB browser
winget install DB.Browser.SQLite

# Open database
db-browser ab360/backend/data/ab360.db
```

### View ChromaDB Data
```python
from app.core.vector_store import vector_store

# List all notes
notes = vector_store.notes_collection.get()
print(notes)

# Search
results = vector_store.search_notes("preferences")
print(results)
```

### View Agent Flow
```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Watch agent execution in terminal
```

---

## 💡 Summary

| Component | Purpose | Example Use |
|-----------|---------|-------------|
| **SQLite** | Structured data | Tasks, goals, preferences with filtering |
| **ChromaDB** | Semantic search | Find notes by meaning, not exact words |
| **LangChain** | Tool framework | Standardize function calls for AI |
| **LangGraph** | Agent workflow | Control thinking process step-by-step |
| **LangSmith** | Debugging | Monitor agent decisions (optional) |
| **Ollama** | AI Model | Generate text, classify intent, create plans |

### The Power of This Architecture

1. **SQLite** stores facts → "Task #5 is high priority"
2. **ChromaDB** stores context → "User prefers mornings"
3. **LangChain** provides actions → Tools the agent can use
4. **LangGraph** orchestrates thinking → How agent decides
5. **Ollama** provides intelligence → Understanding and generation

Together, they create an **intelligent, memory-driven assistant** that:
- ✅ Remembers your preferences
- ✅ Understands what you mean (not just what you say)
- ✅ Takes actions (create tasks, search data)
- ✅ Learns from conversations
- ✅ Works completely offline

---

**This is the foundation of ab360's intelligence!** 🚀
