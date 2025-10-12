from fastapi import APIRouter, HTTPException
from typing import List, Optional, Dict, Any
from services.calendar_service import CalendarService
from services.openrouter_service import OpenRouterService
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/calendar", tags=["calendar"])
calendar_service = CalendarService()
ai = OpenRouterService()

class MeetingBriefRequest(BaseModel):
    event_id: str
    include_related: Optional[bool] = False

@router.get("/events")
def get_events() -> List[Dict[str, Any]]:
    return calendar_service.get_upcoming_events()

@router.post("/meeting-brief")
def meeting_brief(req: MeetingBriefRequest) -> Dict[str, Any]:
    event = calendar_service.get_event(req.event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    # Use AI to generate a meeting brief if available
    ai_brief = None
    if ai and ai.available():
        ai_brief = ai.meeting_brief(
            title=event["title"],
            when_iso=event["start"],
            attendees=event["attendees"],
            description=event.get("description", "")
        )
    return {
        "event": event,
        "brief": ai_brief or "No AI brief available (using mock or fallback)",
    }
