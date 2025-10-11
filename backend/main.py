"""
Brody Backend - Proactive Multi-Agent AI Hub
Main FastAPI application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

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

# Email endpoints
@app.post("/api/classify-email")
async def classify_email(email: EmailMessage):
    """
    Classify email urgency and suggest actions
    """
    # Simple rule-based classification (can be replaced with LLM)
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
    uvicorn.run(app, host="0.0.0.0", port=8000)
