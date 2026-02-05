# ab360 - Personal Desktop AI Assistant

ab360 is a personal AI assistant designed to help with daily planning, learning, decision support, and communication assistance.

## Features

- 🗓️ **Daily Planning**: Create and manage tasks, set goals, generate daily plans
- 📚 **Learning Assistant**: Track learning progress, create study plans
- 💾 **Memory Management**: Store and retrieve notes, preferences, and important conversations
- ✍️ **Communication Helper**: Rewrite text with different tones (polite, professional, casual)
- 🤔 **Decision Support**: Analyze options and get recommendations
- 🎯 **Intent Detection**: Automatically understands what you want to do
- 🔍 **Vector Memory**: Semantic search across all your stored information

## Architecture

### Backend
- **Framework**: FastAPI
- **Agent**: LangGraph + LangChain
- **AI Models**: Ollama (local), Gemini Flash, or Kimi K2.5 (auto-detects available)
- **Database**: SQLite for structured data
- **Vector Store**: ChromaDB for semantic memory
- **Tools**: Task Manager, Planner, Notes, Learning Tracker, Memory

### Frontend
- **Framework**: React 18 + Vite
- **Styling**: Tailwind CSS (Soft UI design)
- **Desktop**: Tauri (Rust-based desktop wrapper)
- **Features**: Draggable floating bar, chat interface

## Prerequisites

- Python 3.11+
- Node.js 18+
- Poetry (Python dependency management)
- **One of these AI models:**
  - Ollama (free, local, no API key) - **Recommended**
  - Gemini API key (free tier)
  - Kimi API key (free tier)

## Setup

### 1. Choose Your AI Model

**Option A - Ollama (Recommended - Free & Local):**
```bash
# Install from https://ollama.ai
ollama pull llama2
```

**Option B - Gemini (Cloud - Free Tier):**
```bash
# Get free API key from https://makersuite.google.com/app/apikey
```

**Option C - Use Multiple (Best - Auto Fallback):**
- Install Ollama + add Gemini key to .env

See [MODEL_SETUP.md](MODEL_SETUP.md) for detailed guide.

### 2. Backend Setup

```bash
cd backend

# Install dependencies
poetry install

# Create .env file
cp env.example .env

# Edit .env and add your API key(s):
# GOOGLE_API_KEY=your_key     (for Gemini)
# KIMI_API_KEY=your_key       (for Kimi)
# OLLAMA_MODEL=llama2         (for Ollama - auto-detected)

# Run backend server
poetry run uvicorn app.main:app --reload
```

You'll see which models are available:
```
✅ Ollama available (local)
✅ Gemini available (cloud)
✅ Using primary model: Ollama (llama2)
```

Backend will run on http://localhost:8000

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend will run on http://localhost:3000

### 3. Desktop App (Tauri)

```bash
# Install Tauri CLI (if not already installed)
cargo install tauri-cli

# Run desktop app in development
cd ab360
cargo tauri dev

# Build desktop app for production
cargo tauri build
```

## Quick Start

### Option 1: Web Development Mode
1. Start backend: `cd backend && poetry run uvicorn app.main:app --reload`
2. Start frontend: `cd frontend && npm run dev`
3. Open browser: http://localhost:3000

### Option 2: Desktop App
1. Start backend: `cd backend && poetry run uvicorn app.main:app --reload`
2. Start Tauri: `cargo tauri dev`

## Usage Examples

### Daily Planning
```
"Plan my day with 2 hours of office work and 30 minutes learning Python"
```

### Task Management
```
"Create a task to finish the report by Friday"
"Show me my pending tasks"
"Mark task 5 as completed"
```

### Learning
```
"Create a learning plan for React hooks"
"Update my Python progress to 60%"
```

### Note Taking
```
"Remember that my favorite color is blue"
"Save a note: meeting notes from today"
"Search my notes about project ideas"
```

### Communication
```
"Rewrite this email in a professional tone: [your text]"
```

### Decision Making
```
"Help me decide between option A and option B for [situation]"
```

## API Endpoints

### Chat
- `POST /api/chat` - Main conversation endpoint

### Tasks
- `GET /api/tasks` - Get all tasks
- `POST /api/tasks` - Create task
- `PATCH /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task

### Memory
- `POST /api/memory/search` - Search memory
- `POST /api/memory` - Store memory
- `DELETE /api/memory/{type}/{id}` - Delete memory

## Project Structure

```
ab360/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── agent/       # LangGraph agent
│   │   ├── core/        # Config, database, vector store
│   │   ├── models/      # Pydantic schemas
│   │   ├── routes/      # API routes
│   │   ├── services/    # AI services
│   │   └── tools/       # Agent tools
│   ├── data/            # SQLite DB & ChromaDB (created on first run)
│   └── pyproject.toml   # Python dependencies
├── frontend/            # React frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   └── styles/      # CSS files
│   └── package.json     # Node dependencies
└── src-tauri/          # Tauri desktop wrapper
    ├── src/
    └── Cargo.toml      # Rust dependencies
```

## Configuration

### Backend (.env)
```env
GOOGLE_API_KEY=your_key_here
KIMI_API_KEY=your_key_here (optional)
DEBUG=true
LOG_LEVEL=INFO
DATABASE_PATH=./data/ab360.db
VECTOR_STORE_PATH=./data/chromadb
```

### Frontend
API URL is configured in `src/components/ChatWindow.jsx` (default: http://localhost:8000)

## Design Principles

- Simple over complex
- User always in control
- Explain before acting
- Memory-driven personalization
- Minimal UI, fast access

## Tech Stack Summary

| Layer | Technology |
|-------|-----------|
| Desktop Shell | Tauri (Rust) |
| Frontend | React, Vite, Tailwind CSS |
| Backend | FastAPI, Python |
| Agent | LangGraph, LangChain |
| AI Models | Gemini, Kimi |
| Database | SQLite |
| Vector DB | ChromaDB |
| Package Mgmt | Poetry (Python), npm (Node) |

## Development Tips

1. **Backend logs**: Check terminal running uvicorn for agent execution logs
2. **Tool execution**: Tools are called automatically by the agent based on intent
3. **Memory search**: Automatically retrieves relevant context for each query
4. **Session persistence**: Session ID maintains conversation context

## Keyboard Shortcuts (Desktop)

- Toggle window visibility (configurable in Tauri)
- Always-on-top toggle
- Drag floating bar to reposition

## Troubleshooting

### Backend won't start
- Check Python version: `python --version` (need 3.11+)
- Verify API keys in `.env` file
- Install dependencies: `poetry install`

### Frontend connection error
- Ensure backend is running on port 8000
- Check CORS settings in `backend/app/main.py`

### Tauri build fails
- Install Rust: https://rustup.rs/
- Install system dependencies (varies by OS)
- Check Tauri prerequisites: https://tauri.app/v1/guides/getting-started/prerequisites

## License

Personal project - see individual component licenses

## Contributing

This is a personal assistant project. Fork and customize for your needs!

## Roadmap

- [ ] Voice input
- [ ] Mobile app
- [ ] Calendar integration
- [ ] Habit tracking dashboard
- [ ] Export/import data
- [ ] Theme customization
- [ ] Offline mode

---

Built with ❤️ using modern AI and web technologies
