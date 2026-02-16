# BraavEngine Copilot Instructions

## Project Overview

**BraavEngine** is a dual-stack agentic system bridging AI intelligence with persistent knowledge management. The architecture consists of:

- **Frontend**: React + Vite UI (Orb Command Center) at `orb-command-center/src/`
- **Backend**: Python FastAPI + Ollama LLM kernel (`bridge_api.py`)
- **Brain**: Supabase-backed knowledge system (`brain.py`) with semantic embeddings
- **Desktop App**: Tkinter interface (`orbcore.py`) for agentic workflows
- **Watchers**: File monitoring (`orb_watcher.py`) for automatic knowledge ingestion

### Critical Data Flow

1. **User Input** → React UI (`App.jsx`) 
2. **API Call** → FastAPI backend (`bridge_api.py` port 8000)
3. **Knowledge Query** → Supabase + embeddings (`brain.py` uses SentenceTransformer)
4. **LLM Response** → Ollama local model (llama3)
5. **Persistence** → Logged to Supabase tables: `thoughts`, `interactions`, `files_in_void`, `query_logs`

---

## Key Architecture Patterns

### Schema Mapping (The Drawers)
The `brain.py` defines a strict schema contract in `SCHEMA_MAP`:
- **thoughts**: Personal entries (content, created_at, embedding, metadata)
- **interactions**: Chat memory between user and ORB
- **files_in_void**: Ingested external documents  
- **query_logs**: Audit trail of agent decisions

**CRITICAL**: Never invent columns—only use those listed in `brain.SCHEMA_MAP`.

### Embedding Strategy
- Uses `SentenceTransformer("all-MiniLM-L6-v2")` for semantic search
- All text stored in Supabase gets embedded via `brain.get_embedding()`
- Enables similarity-based retrieval for context augmentation

### LLM Integration
- **Model**: `ollama:llama3` (local, must be running)
- **Call site**: `bridge_api.py` uses `ollama.chat()` with system prompt
- **Future**: `app.py` has hooks for Gemini 2.0 Flash (Google GenAI SDK)

---

## Development Workflows

### Starting the System
```bash
# Terminal 1: Python backend (FastAPI)
cd c:\Users\srivk\braav-engine
& .\.venv\Scripts\Activate.ps1
python bridge_api.py  # Starts on http://localhost:8000

# Terminal 2: Frontend (Vite dev server)
cd orb-command-center
npm run dev  # Starts on http://localhost:5173

# Terminal 3: Desktop app (optional)
python orbcore.py  # Tkinter interface + file watcher
```

### Build & Deploy
- **Frontend**: `npm run build` → outputs to `orb-command-center/dist/`
- **Linting**: `npm run lint` (ESLint configured in `orb-command-center/`)
- **Python**: No formal build; ensure `requirements.txt` is synced after adding dependencies

### Testing
- `test_api.py` contains FastAPI endpoint tests
- Run: `python test_api.py` from workspace root
- React components use vanilla React (no testing framework configured)

---

## Project-Specific Conventions

### Naming & Terminology
- **ORB**: The agentic kernel (Ollama LLM + decision logic)
- **Void**: Watch directory (`~/ORB_VOID/`) for ingesting files
- **Drawers**: Supabase tables (persistent storage)
- **Bridge**: Connection layer between frontend and knowledge backend
- **Cortex Notes**: React textarea for user journaling

### CORS & Security
- FastAPI explicitly allows only `http://localhost:5173` (React dev server)
- Update `bridge_api.py` CORS origins when deploying to production
- `.env` file required with API keys (not in git)

### File Organization
- Root `.py` files: Core modules (brain, bridge, watcher, desktop app)
- `orb-command-center/`: Vite-based React SPA
- `assets/`, `static/`, `templates/`: Legacy/unused directories

### UI Patterns (React)
- Uses **Tailwind CSS** with dark theme (`bg-[#09090b]`, `zinc-100`)
- Icons from **lucide-react** (Settings, BookOpen, Terminal, etc.)
- State managed with `useState` (no Redux/Context API)
- Error handling: Show "Kernel unreachable" message if API fails

---

## Common Pitfalls & Solutions

| Issue | Root Cause | Fix |
|-------|-----------|-----|
| "Kernel unreachable" in UI | `bridge_api.py` not running | Start FastAPI: `python bridge_api.py` |
| Ollama model not found | Local Ollama not running | `ollama serve` + `ollama pull llama3` |
| CORS errors from React | Frontend URL not in FastAPI CORS | Update `allow_origins` in `bridge_api.py` |
| Import errors in Python | Missing dependencies | Install: `pip install -r requirements.txt` (if exists) or manually add packages |
| Vite build fails | Missing Tailwind config | Config exists at root; ensure `npm install` run in `orb-command-center/` |

---

## Integration Points for AI Agents

### When Adding Features:
1. **New LLM capability**: Modify `bridge_api.py` endpoint logic or `brain.py` agent_query()
2. **New data persistence**: Add table to Supabase, update `SCHEMA_MAP` in `brain.py`
3. **New UI component**: Add to `orb-command-center/src/App.jsx` (React)
4. **Watcher ingestion**: Extend `orb_watcher.py` → calls `brain.swallow_and_log()`

### Key Files to Understand First:
- [brain.py](brain.py) — Core reasoning loop & Supabase operations
- [bridge_api.py](bridge_api.py) — Frontend ↔ Backend gateway
- [App.jsx](App.jsx) — UI layout & state management
- [orbcore.py](orbcore.py) — Desktop app entry point

---

## Environment & Dependencies

**Python**: 3.10+ (via `.venv/`)  
**Node**: 18+ (for npm)  
**Key Packages**:
- `fastapi`, `uvicorn` — API framework
- `ollama` — LLM client
- `supabase` — Database client
- `sentence-transformers` — Embeddings
- `watchdog` — File system monitoring
- `groq` — Alternative LLM (not currently active)

**Frontend**: React 19.2 + Vite 7.2 + Tailwind 4.1

---

## Quick Reference Commands

```bash
# Activate Python venv
& .\.venv\Scripts\Activate.ps1

# Start backend
python bridge_api.py

# Start frontend
cd orb-command-center && npm run dev

# Start desktop app (includes file watcher)
python orbcore.py

# Run API tests
python test_api.py
```

---

**Last Updated**: January 2026 | For questions, check README.md or trace logs in orbcore.py output.
