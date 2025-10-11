# Brody Development Guide

## Project Structure

```
Brody/
├── backend/           # FastAPI backend
│   ├── main.py       # API endpoints
│   └── requirements.txt
├── frontend/         # React frontend
│   ├── public/
│   ├── src/
│   └── package.json
├── agents/           # Multi-agent system
│   └── coordinator.py
├── Plans/            # Project proposals and planning docs
└── docs/             # Documentation
```

## Quick Start

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the backend:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm start
```

The app will open at `http://localhost:3000`

## API Endpoints

### Core Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `POST /api/classify-email` - Classify email urgency
- `POST /api/suggest-task` - Generate task from email
- `GET /api/prepare-day` - **Main MVP feature** - Prepare your day
- `POST /api/meeting-brief` - Generate meeting brief

## Architecture

Brody uses a multi-agent architecture:

1. **BrodyCoordinator** - Central brain that orchestrates agents
2. **EmailAgent** - Handles email monitoring and classification
3. **TaskAgent** - Manages task suggestions and prioritization
4. **MeetingAgent** - Prepares meeting briefs and agendas

## Development Workflow

### Running Both Frontend and Backend

1. Terminal 1 - Backend:
```bash
cd backend
python main.py
```

2. Terminal 2 - Frontend:
```bash
cd frontend
npm start
```

### Testing the API

Using curl:
```bash
# Health check
curl http://localhost:8000/health

# Prepare day (main feature)
curl http://localhost:8000/api/prepare-day
```

## Next Steps

1. **Integrate Real APIs**: Add Gmail, Calendar, Microsoft To Do integrations
2. **LLM Integration**: Add Gemini/OpenAI for intelligent summarization
3. **Proactive Scanning**: Implement automatic email/task monitoring
4. **Gamification**: Add points, achievements, and progress tracking
5. **Authentication**: Add user authentication and data persistence

## Contributing

See the main README.md for contribution guidelines.

## Tech Stack

- **Backend**: FastAPI, Python
- **Frontend**: React, CSS
- **Agents**: Python classes (can be extended with LangGraph)
- **Future**: Gemini API, LangGraph, FastMCP
