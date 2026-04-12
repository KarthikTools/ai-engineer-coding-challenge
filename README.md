# Task Agent

A web app where you type a task in plain English and a backend agent figures out which tool to use, runs it, and shows you exactly what it did step by step. 

**Stack:** Python (FastAPI) backend · React (TypeScript) frontend

---

## How to Run

You need **Python 3.9+** and **Node.js 18+** installed.

### Start the Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

> On Windows use `venv\Scripts\activate` instead.

Backend will be at http://localhost:8000  
API docs at http://localhost:8000/docs

### Start the Frontend

Open a new terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend will be at http://localhost:5173

### Run Tests

```bash
cd backend
source venv/bin/activate
python -m pytest tests/ -v
```

50 tests — all passing.

---

## What Does It Do?

You type something like:
- `"Convert hello world to uppercase"` → gives you `HELLO WORLD`
- `"Calculate 3 + 5"` → gives you `3 + 5 = 8`
- `"Weather in Tokyo"` → gives you mock weather data for Tokyo

The agent figures out which tool to use on its own. You can see every step it took to decide.

---

## What Tools Are Available?

| Tool | What It Does | Try This |
|------|-------------|----------|
| **TextProcessorTool** | Uppercase, lowercase, word count, reverse, title case | `"Reverse hello"` |
| **CalculatorTool** | Basic math, also understands words like "plus" and "times" | `"What is 10 times 4"` |
| **WeatherMockTool** | Fake weather for any city (no real API, same city always gives same result) | `"Weather in London"` |

---

## API Endpoints

| Method | URL | What It Does |
|--------|-----|-------------|
| POST | `/api/tasks` | Send a task, get the result back |
| GET | `/api/tasks` | See all past tasks |
| GET | `/api/tasks/{id}` | Get one specific task |
| GET | `/api/tasks/export` | Download all tasks as JSON |
| GET | `/api/tools` | See what tools are available |

---

## How It Works (the short version)

1. You type a task
2. The **Agent Controller** asks each tool "can you handle this?" — each tool gives a confidence score from 0 to 1
3. The tool with the highest score gets picked
4. That tool runs and gives back a result
5. Everything gets saved and you see the result + a step-by-step trace

If a tool fails, the agent will retry once before giving up.

---

## Project Structure

```
backend/
  app/
    main.py           ← starts the server
    routes.py          ← API endpoints
    models.py          ← data models (what a Task looks like)
    store.py           ← saves tasks in memory
    agent/
      controller.py    ← the brain — picks the tool and runs it
    tools/
      base.py          ← base class every tool follows
      text_processor.py
      calculator.py
      weather_mock.py
  tests/               ← 50 tests total

frontend/
  src/
    App.tsx            ← main page
    api.ts             ← talks to the backend
    types.ts           ← TypeScript types
    components/
      TaskInput.tsx    ← the text box + submit button
      TaskResultCard.tsx ← shows one result
      TaskHistory.tsx  ← shows all past tasks
      ExecutionTrace.tsx ← shows the agent's steps
      ToolList.tsx     ← shows available tools
```

---

## Design Choices I Made

- **Tools are plug-and-play.** Every tool follows the same interface (`BaseTool`). If you want to add a new tool, you just create a new file — no need to change the agent code at all.
- **Confidence scoring instead of if/else.** The agent does not use hardcoded rules. Each tool scores itself, and the best one wins. This makes it easy to add or change tools later.
- **Safe math evaluation.** The calculator does not use raw `eval()`. It parses the expression into an AST and only allows numbers and basic operators. No code injection possible.
- **In-memory storage with export.** Tasks are stored in a Python dictionary. You can export everything as JSON from the UI. Data resets when you restart the server.
- **Frontend never calls fetch() directly.** All API calls go through `api.ts` so there is one place to change if the backend changes.

---

## Bonus Features

- Retry logic — if a tool fails, the agent tries again before giving up
- Execution trace — every task shows the agent's reasoning step by step
- Export — download your task history as a JSON file
- Quick action buttons — click to try example tasks without typing
- Safe calculator — prevents code injection via AST whitelisting

---

## What I Would Add With More Time

- Chain multiple tools together for complex tasks
- Stream the agent's steps to the UI in real time
- Save tasks to a database instead of memory
- Docker setup so anyone can run it with one command
- Better natural language understanding
- Frontend tests

---

## Dependencies

**Backend:** fastapi, uvicorn, pydantic, pytest, httpx  
**Frontend:** react, react-dom, vite, typescript

---

## AI Tools Used

GitHub Copilot was used during development to help with boilerplate code and unit test scaffolding. All generated code was reviewed, understood, and adjusted by hand. The architecture, design decisions, and core logic are my own.
