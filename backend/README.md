# ab360 Backend

Personal desktop AI assistant backend powered by FastAPI and LangGraph.

## 🤖 AI Model Support

ab360 automatically detects and uses available AI models:

- **Ollama** (local, free, no API key)
- **Gemini Flash** (cloud, free tier)
- **Kimi K2.5** (cloud, free tier)

See [MODEL_SETUP.md](../MODEL_SETUP.md) for detailed setup.

## 🚀 Quick Setup

### 1. Install dependencies
```bash
poetry install
```

### 2. Choose your AI model

**Option A - Ollama (easiest, free, local):**
```bash
# Install from https://ollama.ai
ollama pull llama2
# No .env config needed!
```

**Option B - Gemini (fastest setup):**
```bash
# Get key from https://makersuite.google.com/app/apikey
# Add to .env:
echo "GOOGLE_API_KEY=your_key" >> .env
```

**Option C - Use all (recommended):**
```bash
# Copy env.example
cp env.example .env
# Edit .env and add your keys
```

### 3. Run the server
```bash
poetry run uvicorn app.main:app --reload --port 8000
```

You should see which models are available:
```
✅ Ollama available (local)
✅ Gemini available (cloud)
✅ Using primary model: Ollama (llama2)
```

## 📚 API Documentation

Once running, visit:
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/health

## 🛠️ Architecture

```
app/
├── agent/          # LangGraph workflow
│   ├── state.py    # Agent state definition
│   ├── nodes.py    # Processing nodes
│   └── graph.py    # Workflow graph
├── core/           # Infrastructure
│   ├── config.py   # Settings
│   ├── database.py # SQLite
│   └── vector_store.py # ChromaDB
├── models/         # Pydantic schemas
├── routes/         # API endpoints
├── services/       # Business logic
│   └── ai_service.py # AI model management
├── tools/          # Agent tools (19 tools)
└── main.py         # FastAPI app
```

## 🔧 Configuration

Edit `.env` file:

```env
# AI Models (choose one or more)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
GOOGLE_API_KEY=your_gemini_key
KIMI_API_KEY=your_kimi_key

# Application
APP_NAME=ab360
DEBUG=true
LOG_LEVEL=INFO

# Database
DATABASE_PATH=./data/ab360.db
VECTOR_STORE_PATH=./data/chromadb
```

## 🎯 Endpoints

### Chat
- `POST /api/chat` - Main conversation endpoint
  ```json
  {
    "message": "Plan my day with 2 hours of work",
    "session_id": "optional"
  }
  ```

### Tasks
- `GET /api/tasks` - List all tasks
- `GET /api/tasks?status=pending` - Filter by status
- `POST /api/tasks` - Create task
- `PATCH /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task

### Memory
- `POST /api/memory/search` - Search memory
  ```json
  {
    "query": "my preferences",
    "type": "notes",
    "n_results": 5
  }
  ```
- `POST /api/memory` - Store memory
- `DELETE /api/memory/{type}/{id}` - Delete memory

## 🧪 Testing

```bash
# Run tests
poetry run pytest

# With coverage
poetry run pytest --cov=app
```

## 🔍 Development

### Hot Reload
```bash
poetry run uvicorn app.main:app --reload
```

### Logs
- Check terminal output for agent execution logs
- Tool calls are logged automatically
- Errors show full stack trace in DEBUG mode

### Adding Tools

1. Create new file in `app/tools/`
2. Use `@tool` decorator:
   ```python
   from langchain.tools import tool
   
   @tool
   def my_new_tool(param: str) -> str:
       """Tool description"""
       return result
   ```
3. Add to `app/tools/__init__.py`
4. Tool is automatically available!

## 🐛 Troubleshooting

### "No AI models available"
- Install Ollama OR add API key to .env
- See [MODEL_SETUP.md](../MODEL_SETUP.md)

### "Module not found"
```bash
poetry install --no-root
```

### "Database locked"
- Close other connections to database
- Delete `data/ab360.db` to reset

### Port already in use
```bash
# Use different port
poetry run uvicorn app.main:app --reload --port 8001
```

## 📦 Dependencies

Core:
- FastAPI - Web framework
- LangChain - AI tools
- LangGraph - Agent workflow
- Pydantic - Data validation

AI Models:
- langchain-google-genai - Gemini
- langchain-community - Ollama, Kimi

Storage:
- SQLite - Structured data
- ChromaDB - Vector embeddings

## 🔐 Security

- API keys in .env (never commit)
- Local data storage only
- No silent data sharing
- User confirmation for deletions

## 📖 More Documentation

- [Model Setup Guide](../MODEL_SETUP.md) - AI model configuration
- [Architecture](../ARCHITECTURE.md) - Technical details
- [Main README](../README.md) - Full project docs

---

**Ready to code!** The backend is fully functional and extensible.
