<!--
Project-specific Copilot instructions for the Brody repository.
Keep this file short (20-50 lines). Focus on concrete, discoverable patterns
and examples that help an automated coding agent make correct, low-risk
changes without asking for extra context.
-->

# Copilot / AI Agent Instructions — Brody

- Project purpose: Brody is an MVP multi-agent AI productivity hub (backend in
  `backend/` using FastAPI; frontend in `frontend/` using React; agent
  orchestration in `agents/`). Key feature: "Prepare My Day" (`GET /api/prepare-day`).

- Primary edit areas and conventions:
  - Backend: `backend/main.py` is a small FastAPI app. Follow its existing
    style (Pydantic models at top, simple route handlers). Use the same
    dependency list in `backend/requirements.txt` (FastAPI, Uvicorn, Pydantic,
    python-dotenv).
  - Agents: `agents/coordinator.py` contains the coordinator and minimal
    BaseAgent subclasses. Add agent logic by extending these classes and
    keeping public methods named like `check_triggers`, `get_important`,
    `get_prioritized`, `get_upcoming` to preserve orchestration.
  - Frontend: `frontend/` is a Create React App project. Use `axios` for
    API calls (already in `package.json`). Keep API base URL usage minimal and
    respect CORS (backend allows all origins in current dev setup).

- Architecture notes (why things are structured this way):
  - The coordinator aggregates structured outputs from specialized agents
    (email/task/meeting). Changes that add new data must preserve the simple
    JSON-shape the frontend and API expect: `{meetings:[], tasks:[], suggestions:[]}`.
  - The backend currently returns mock data; integrate LLMs or external APIs
    only behind feature flags or new endpoints to avoid breaking the MVP API
    contract (`/api/prepare-day`, `/api/classify-email`, `/api/suggest-task`).

- Safe edit patterns and examples:
  - To add a new route, follow `main.py` examples: define a Pydantic model,
    then a route function returning serializable primitives or model instances.
    Example: see `classify_email` and `suggest_task`.
  - To add persistent config or secrets, prefer `python-dotenv` and add
    entries to `.env` (do not commit secrets).
  - When extending agents, register them on `BrodyCoordinator.agents` with a
    stable key (e.g., `email_agent`) so `prepare_day()` picks them up.

- Tests / dev flow observed from repo:
  - Backend: run from `backend/` with Python 3.9+; `pip install -r requirements.txt`
    then `python main.py` (UVicorn is used in `if __name__ == '__main__'`).
  - Frontend: run from `frontend/` with Node 18+; `npm install` then `npm start`.

- Integration points to watch:
  - API endpoints called by the frontend: `/api/prepare-day`, `/api/classify-email`,
    `/api/suggest-task`, `/api/meeting-brief`. Changing shapes will break the UI.
  - Agents may later call external services (Gmail, Calendar, LLM). Keep adapters
    small, testable, and behind feature flags.

- Project-specific gotchas:
  - The backend is intentionally simple and returns mock data; don't assume
    persistence or authentication exist when adding features.
  - `agents/coordinator.py` expects agent names like `email_agent` — use those
    exact keys if you want `prepare_day()` to auto-include them.

- When uncertain, prefer minimal, backwards-compatible changes and reference
  the following files in any PR or change note:
  - `backend/main.py` (API contract and examples)
  - `agents/coordinator.py` (agent lifecycle and method names)
  - `docs/DEVELOPMENT.md` and `README.md` (run/dev commands and high-level
    architecture)

Please ask for clarification only when a change would alter API shapes,
authentication, or external integrations that are not mocked in this repo.
