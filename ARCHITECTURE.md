# ab360 Architecture Documentation

## System Overview

ab360 is a personal AI assistant built with a modern, modular architecture designed for extensibility and maintainability.

```
┌─────────────────────────────────────────────────────────────┐
│                      Desktop Layer (Tauri)                   │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              Frontend (React + Vite)                   │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │  │
│  │  │ Floating Bar │  │ Chat Window  │  │ UI Components│ │  │
│  │  └──────────────┘  └──────────────┘  └─────────────┘ │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                   HTTP/REST API (Axios)
                            │
┌─────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                         │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                  API Routes                            │  │
│  │  /api/chat  /api/tasks  /api/memory                   │  │
│  └───────────────────────────────────────────────────────┘  │
│                            │                                 │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              Agent Layer (LangGraph)                   │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐            │  │
│  │  │ Intent   │→ │ Memory   │→ │ Tool     │→ Response  │  │
│  │  │ Detection│  │ Retrieval│  │ Execution│            │  │
│  │  └──────────┘  └──────────┘  └──────────┘            │  │
│  └───────────────────────────────────────────────────────┘  │
│                            │                                 │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                    Tools Layer                         │  │
│  │  Task Manager │ Planner │ Notes │ Learning │ Memory   │  │
│  └───────────────────────────────────────────────────────┘  │
│                            │                                 │
│  ┌────────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │  AI Services   │  │   Database   │  │  Vector Store  │  │
│  │ Gemini / Kimi  │  │   SQLite     │  │   ChromaDB     │  │
│  └────────────────┘  └──────────────┘  └────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Frontend Layer

**Technology:** React 18, Vite, Tailwind CSS

**Key Components:**

#### FloatingBar.jsx
- Draggable component positioned at top of screen
- Uses native HTML5 drag events
- State: position (x, y), isDragging
- Features: Always-on-top, minimize/expand

#### ChatWindow.jsx
- Main conversation interface
- Features:
  - Message history display
  - Auto-scroll to bottom
  - Typing indicators
  - Intent and tool call badges
  - Session management
- API integration via Axios

**Styling:**
- Soft UI design (neumorphism-inspired)
- Colors: Primary #2563EB, Secondary #F3F4F6
- Shadows: soft, soft-lg
- Rounded corners: 8px-12px

### 2. Desktop Layer (Tauri)

**Technology:** Rust, Tauri 1.5

**Features:**
- System tray integration
- Always-on-top window control
- Transparent window support
- Global shortcuts
- Native OS integration

**Commands:**
- `toggle_always_on_top`: Toggle window always-on-top
- `show_window`: Show window
- `hide_window`: Hide window

### 3. Backend API Layer

**Technology:** FastAPI, Python 3.11+

**Endpoints:**

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | /api/chat | Main conversation |
| GET | /api/tasks | List tasks |
| POST | /api/tasks | Create task |
| PATCH | /api/tasks/{id} | Update task |
| DELETE | /api/tasks/{id} | Delete task |
| POST | /api/memory/search | Search memory |
| POST | /api/memory | Store memory |
| DELETE | /api/memory/{type}/{id} | Delete memory |

**CORS:** Configured for localhost development

### 4. Agent Layer (LangGraph)

**Flow:**

```
User Input
    ↓
Detect Intent
    ↓
Retrieve Memory (semantic search)
    ↓
Plan Actions
    ↓
Execute Tools (LangChain agent)
    ↓
Generate Response
    ↓
Store Conversation
    ↓
Return Response
```

**State Definition:**
```python
{
    "user_input": str,
    "intent": str,
    "retrieved_memory": List[Dict],
    "planned_actions": List[str],
    "tool_results": List[Dict],
    "messages": List[BaseMessage],
    "final_response": str,
    "session_id": str,
    "metadata": Dict
}
```

**Node Types:**
1. `detect_intent_node`: Uses AI to classify user intent
2. `retrieve_memory_node`: Semantic search across all memory
3. `plan_actions_node`: Maps intent to tool sequence
4. `execute_tools_node`: Calls tools via LangChain agent
5. `generate_response_node`: Formats final response
6. `store_conversation_node`: Saves to memory

### 5. Tools Layer

Each tool is a LangChain `@tool` decorated function that returns JSON.

#### Task Manager Tools
- `create_task(title, description, priority, due_date)`
- `update_task_status(task_id, status)`
- `get_tasks(status)`
- `get_pending_tasks()`

#### Planner Tools
- `create_daily_plan(focus_areas, available_hours)`
- `set_goal(title, description, category, target_date)`
- `get_goals(status)`

#### Notes Tools
- `save_note(content, tags)`
- `search_notes(query, limit)`
- `delete_note(note_id)`

#### Learning Tracker Tools
- `create_learning_plan(topic, time_available, difficulty)`
- `update_learning_progress(topic, subtopic, progress, notes)`
- `get_learning_progress(topic)`

#### Memory Tools
- `store_preference(key, value)`
- `get_preference(key)`
- `get_all_preferences()`
- `search_memory(query, limit)`
- `store_conversation(user_input, agent_response, intent)`

### 6. AI Services Layer

**Primary Model:** Gemini 3 Flash Preview (via Google)
**Fallback Model:** Kimi K2.5 (configurable)

**AIService Methods:**
- `generate_response(prompt, system_prompt)`: General text generation
- `detect_intent(user_input)`: Intent classification
- `rewrite_text(text, tone, instructions)`: Text rewriting
- `analyze_decision(question, options)`: Decision analysis

**Error Handling:** Automatic fallback to secondary model on failure

### 7. Storage Layer

#### SQLite Database

**Tables:**

1. **tasks**
   - id, title, description, status, priority, due_date
   - created_at, updated_at, completed_at

2. **goals**
   - id, title, description, category, target_date, status
   - created_at, updated_at

3. **preferences**
   - id, key, value, updated_at

4. **habits**
   - id, name, frequency, last_completed, streak, created_at

5. **decisions**
   - id, question, options, analysis, decision, created_at

6. **learning_progress**
   - id, topic, subtopic, status, progress, notes
   - last_reviewed, created_at, updated_at

7. **conversations**
   - id, user_input, intent, agent_response, tool_calls, created_at

#### ChromaDB Vector Store

**Collections:**

1. **notes**: User notes and information
2. **learning**: Learning summaries and progress
3. **conversations**: Important conversation history

**Features:**
- Semantic search with embeddings
- Metadata filtering
- Relevance scoring

## Data Flow Example

### User Query: "Plan my day with office work and learning"

1. **Frontend**: User types message → ChatWindow sends POST to /api/chat

2. **Backend API**: Receives request → Creates initial agent state

3. **Intent Detection**: AI analyzes input → Returns "planning"

4. **Memory Retrieval**: ChromaDB searches for:
   - Previous plans
   - User preferences
   - Related notes

5. **Action Planning**: Maps "planning" intent → Actions:
   - check_pending_tasks
   - create_daily_plan

6. **Tool Execution**: LangChain agent:
   - Calls `get_pending_tasks()` → Returns current tasks
   - Calls `create_daily_plan("office work, learning", "8")` → AI generates plan

7. **Response Generation**: Formats tool results into conversational response

8. **Store Conversation**: Saves to vector store for future context

9. **Backend API**: Returns response with intent & tool_calls

10. **Frontend**: Displays response with badges

## Security Considerations

1. **API Keys**: Stored in `.env`, never committed
2. **Local Data**: All personal data stored locally
3. **CORS**: Restricted to localhost in development
4. **No Silent Actions**: Confirmation required for destructive operations
5. **User Control**: Manual memory deletion available

## Performance Optimizations

1. **Response Time Target**: < 3 seconds
2. **Database**: SQLite with row_factory for dict conversion
3. **Vector Search**: Limited to top 3-5 results
4. **Agent Iterations**: Max 3 to prevent loops
5. **Async**: All AI calls use async/await

## Extensibility Points

### Adding a New Tool

1. Create file in `backend/app/tools/`
2. Define function with `@tool` decorator
3. Add to `__init__.py` exports
4. Tool automatically available to agent

### Adding a New Intent

1. Update intent detection system prompt
2. Add to `Intent` enum in schemas.py
3. Update action plans in `plan_actions_node`
4. Create corresponding tools

### Adding a New Model

1. Add credentials to `.env`
2. Initialize in `AIService.__init__`
3. Add to fallback chain

### Custom UI Theme

1. Edit `tailwind.config.js` colors
2. Update CSS variables in `index.css`
3. Modify component styles in `styles/` folder

## Development Guidelines

1. **Backend**: Follow FastAPI best practices, use Pydantic models
2. **Frontend**: Functional React components, hooks for state
3. **Tools**: Return JSON with success/error structure
4. **Logging**: Use logger in backend, console in frontend
5. **Error Handling**: Graceful degradation, user-friendly messages

## Deployment Considerations

### Development
- Backend: `uvicorn --reload`
- Frontend: `vite dev`
- Hot reload enabled

### Production
- Backend: `uvicorn` with workers
- Frontend: `vite build` → static files
- Tauri: `cargo tauri build` → native executable

## Testing Strategy

1. **Unit Tests**: Individual tools and functions
2. **Integration Tests**: API endpoints
3. **Agent Tests**: Tool execution flow
4. **UI Tests**: Component rendering
5. **E2E Tests**: Full user workflows

## Monitoring

- **Logs**: JSON format with timestamps
- **Agent Steps**: Logged in development
- **Tool Calls**: Tracked in conversations table
- **Errors**: Caught and logged at each layer

## Future Architecture Enhancements

1. **Voice Input**: Add speech recognition layer
2. **Mobile App**: React Native frontend
3. **Multi-User**: Add authentication layer
4. **Cloud Sync**: Optional backend sync service
5. **Plugin System**: Dynamic tool loading
6. **Analytics**: Usage tracking and insights

---

This architecture balances simplicity with extensibility, making it easy to add features while maintaining clean separation of concerns.
