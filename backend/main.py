"""
Brody Backend - Proactive Multi-Agent AI Hub
Main FastAPI application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import os


from dotenv import load_dotenv
# Load .env from project root (parent directory)
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))


# try:
from services.openrouter_service import OpenRouterService
_openrouter = OpenRouterService()
# except Exception:
#     _openrouter = None

try:
    from routes.auth import router as auth_router
except Exception:
    auth_router = None

try:
    from routes.user import router as user_router
except Exception:
    user_router = None

try:
    from routes.calendar import router as calendar_router
except Exception:
    calendar_router = None

try:
    from routes.email import router as email_router
except Exception:
    email_router = None

app = FastAPI(
    title="Brody API",
    description="Proactive Multi-Agent AI Hub for productivity",
    version="0.1.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include authentication routes if available
if auth_router:
    app.include_router(auth_router)

# Include user routes if available  
if user_router:
    app.include_router(user_router)

# Include email routes if available
if email_router:
    app.include_router(email_router)

# Include calendar routes if available
if calendar_router:
    app.include_router(calendar_router)

# Data models
class EmailMessage(BaseModel):
    id: str
    subject: str
    body: str
    sender: str
    timestamp: datetime
    urgency: Optional[str] = None

class TaskSuggestion(BaseModel):
    id: str
    title: str
    description: str
    priority: str
    suggested_time: Optional[datetime] = None
    source_email_id: Optional[str] = None

class MeetingBrief(BaseModel):
    meeting_id: str
    title: str
    time: datetime
    summary: str
    key_points: List[str]
    action_items: List[str]
    draft_agenda: Optional[str] = None

# Health check
@app.get("/")
async def root():
    return {
        "message": "Brody API - Proactive Multi-Agent AI Hub",
        "status": "running",
        "version": "0.1.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# AI service status (validates Task 1.1 integration without changing behavior)
@app.get("/ai/status")
async def ai_status():
    available = bool(_openrouter and _openrouter.available())
    return {
        "provider": "openrouter",
        "available": available,
        "default_model": os.getenv("DEFAULT_MODEL", "anthropic/claude-3.5-sonnet"),
        "fallback_model": os.getenv("FALLBACK_MODEL", "openai/gpt-4o-mini"),
        "only_free": os.getenv("ONLY_FREE_MODELS", "true"),
        "free_allowlist": os.getenv("FREE_MODEL_ALLOWLIST", "meta-llama/llama-3.1-8b-instruct:free,mistralai/mistral-7b-instruct:free,nousresearch/nous-hermes-2-mistral-7b:free")
    }

@app.get("/ai/test")
async def ai_test():
    """Quick check that OpenRouter returns non-empty content."""
    if not (_openrouter and _openrouter.available()):
        return {"ok": False, "reason": "client-unavailable"}
    out = _openrouter._chat([
        {"role": "system", "content": "Return ONLY the word TEST"},
        {"role": "user", "content": "Say TEST"},
    ], model=os.getenv("DEFAULT_MODEL"))
    return {"ok": bool(out and out.strip()), "content": (out or "")[:100]}

# Email endpoints
@app.post("/api/classify-email")
async def classify_email(email: EmailMessage):
    """
    Classify email urgency and suggest actions
    """
    # Prefer AI classification via OpenRouter if available
    if _openrouter and _openrouter.available():
        result = _openrouter.classify_email(email.subject, email.body, email.sender)
        if result:
            # Map AI output to existing response style while returning AI fields
            urgency = result.get("urgency", "medium")
            suggested_action = result.get("action", "fyi")
            return {
                "email_id": email.id,
                "urgency": urgency,
                "suggested_action": suggested_action,
                "ai": result
            }
    # Fallback: simple rule-based classification
    urgency = "normal"
    if any(word in email.subject.lower() for word in ["urgent", "asap", "important"]):
        urgency = "high"
    elif any(word in email.subject.lower() for word in ["fyi", "optional"]):
        urgency = "low"
    return {
        "email_id": email.id,
        "urgency": urgency,
        "suggested_action": "review" if urgency == "high" else "archive"
    }

@app.post("/api/suggest-task")
async def suggest_task(email: EmailMessage):
    """
    Generate task suggestion from email
    """
    # Prefer AI suggestions if available
    if _openrouter and _openrouter.available():
        suggestions = _openrouter.suggest_tasks(email.subject, email.body, email.sender)
        if suggestions:
            # Return the first suggestion as MVP behavior, include all as metadata
            first = suggestions[0]
            suggestion = TaskSuggestion(
                id=f"task_{email.id}",
                title=first.get("title", f"Follow up: {email.subject}"),
                description=first.get("description", f"Review and respond to email from {email.sender}"),
                priority=first.get("priority", "medium"),
                source_email_id=email.id
            )
            return {"suggestion": suggestion, "ai": suggestions}
    # Fallback mock suggestion
    suggestion = TaskSuggestion(
        id=f"task_{email.id}",
        title=f"Follow up: {email.subject}",
        description=f"Review and respond to email from {email.sender}",
        priority="medium",
        source_email_id=email.id
    )
    return suggestion

# Meeting prep endpoint
@app.get("/api/prepare-day")
async def prepare_day():
    """
    Proactive daily preparation - core MVP feature
    Returns meeting briefs and task priorities
    """
    # Mock data for MVP
    return {
        "date": datetime.now().isoformat(),
        "meetings": [],
        "tasks": [],
        "summary": "Your day is clear. Brody is monitoring for updates."
    }

@app.post("/api/meeting-brief")
async def generate_meeting_brief(meeting_id: str):
    """
    Generate comprehensive meeting brief
    """
    # If AI is available, generate a brief
    if _openrouter and _openrouter.available():
        content = _openrouter.meeting_brief(
            title="Team Standup",
            when_iso=datetime.now().isoformat(),
            attendees=["you", "team"],
            description="Daily sync meeting"
        )
        if content:
            brief = MeetingBrief(
                meeting_id=meeting_id,
                title="Team Standup",
                time=datetime.now(),
                summary=content.split("\n\n")[0][:200],
                key_points=["See AI brief content"],
                action_items=["Prepare talking points"],
                draft_agenda=content
            )
            return brief
    # Fallback mock brief
    brief = MeetingBrief(
        meeting_id=meeting_id,
        title="Team Standup",
        time=datetime.now(),
        summary="Daily sync with the team",
        key_points=["Review progress", "Identify blockers", "Plan next steps"],
        action_items=["Update task board", "Schedule follow-ups"],
        draft_agenda="1. Progress updates\n2. Blockers discussion\n3. Action items"
    )
    return brief

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)
